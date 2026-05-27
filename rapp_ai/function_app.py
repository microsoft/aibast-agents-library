"""
Base Memory Agent Platform for Azure Functions.

A modular AI assistant built on Azure Functions with GPT-4 integration. Features
a dynamic agent architecture with persistent memory across sessions using Azure
File Storage. Supports multi-user conversations with user-specific and shared
memory contexts.

Endpoints:
    GET  /api/health                        — Health check (anonymous)
    POST /api/businessinsightbot_function   — Main conversation endpoint
    POST /api/trigger/copilot-studio        — Direct agent invocation from Copilot Studio
"""
import azure.functions as func
import logging
import json
import os
import importlib
import importlib.util
import inspect
import sys
import re
from agents.basic_agent import BasicAgent
from openai import AzureOpenAI, APIError as OpenAIAPIError, RateLimitError, AuthenticationError, APITimeoutError, BadRequestError
from azure.identity import (
    ChainedTokenCredential,
    ManagedIdentityCredential,
    AzureCliCredential,
    get_bearer_token_provider
)
from datetime import datetime
import time
import threading
from utils.azure_file_storage import safe_json_loads
from utils.storage_factory import get_storage_manager
from utils.result import Result, Success, Failure, AgentLoadError, APIError


# =============================================================================
# CONSTANTS & SINGLETONS
# =============================================================================

# Default GUID to use when no specific user GUID is provided.
# INTENTIONALLY INVALID UUID FORMAT - This is a security feature, not a bug!
#
# The GUID "c0p110t0" contains non-hex characters ('p', 'l') which spells
# "copilot" visually. This deliberate invalidity serves as a database insertion
# guardrail:
#   1. Prevents accidental persistence in UUID-validated columns
#   2. Instantly recognizable in logs as "no real user context"
#   3. UUID parsing libraries reject it, surfacing issues early
#   4. Memory isolation: storage managers route to shared memory
DEFAULT_USER_GUID = "c0p110t0-aaaa-bbbb-cccc-123456789abc"

# Singleton OpenAI client - created once, reused across requests
_openai_client = None
_openai_client_lock = threading.Lock()
_openai_client_created_at = None
OPENAI_CLIENT_TTL_SECONDS = 30 * 60  # 30 minutes

# Cached agents - loaded once, refreshed periodically
_cached_agents = None
_cached_agents_lock = threading.Lock()
_cached_agents_created_at = None
AGENTS_CACHE_TTL_SECONDS = 5 * 60  # 5 minutes

# Request timeout for OpenAI API calls
OPENAI_REQUEST_TIMEOUT = 45


# =============================================================================
# OPENAI CLIENT
# =============================================================================

def _get_openai_client():
    """Get or create a singleton OpenAI client with TTL refresh."""
    global _openai_client, _openai_client_created_at

    with _openai_client_lock:
        needs_refresh = (
            _openai_client is None or
            _openai_client_created_at is None or
            (time.time() - _openai_client_created_at) >= OPENAI_CLIENT_TTL_SECONDS
        )

        if needs_refresh:
            logging.info("Creating/refreshing OpenAI client singleton")
            api_key = os.environ.get('AZURE_OPENAI_API_KEY')

            if api_key:
                logging.info("Using API key authentication for Azure OpenAI")
                _openai_client = AzureOpenAI(
                    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
                    api_key=api_key,
                    api_version=os.environ.get('AZURE_OPENAI_API_VERSION', '2025-01-01-preview'),
                    timeout=OPENAI_REQUEST_TIMEOUT,
                    max_retries=2
                )
            else:
                if os.environ.get('WEBSITE_INSTANCE_ID'):
                    credential = ManagedIdentityCredential()
                    logging.info("Using ManagedIdentityCredential for Azure deployment")
                else:
                    credential = ChainedTokenCredential(
                        ManagedIdentityCredential(),
                        AzureCliCredential()
                    )
                    logging.info("Using ChainedTokenCredential for local development")

                token_provider = get_bearer_token_provider(
                    credential,
                    "https://cognitiveservices.azure.com/.default"
                )

                _openai_client = AzureOpenAI(
                    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
                    azure_ad_token_provider=token_provider,
                    api_version=os.environ.get('AZURE_OPENAI_API_VERSION', '2025-01-01-preview'),
                    timeout=OPENAI_REQUEST_TIMEOUT,
                    max_retries=2
                )

            _openai_client_created_at = time.time()

        return _openai_client


def _reset_openai_client():
    """Reset the OpenAI client singleton to force credential refresh."""
    global _openai_client, _openai_client_created_at
    with _openai_client_lock:
        _openai_client = None
        _openai_client_created_at = None
        logging.info("OpenAI client cache reset - will refresh on next request")


# =============================================================================
# AGENT CACHING
# =============================================================================

def _get_cached_agents(force_refresh=False):
    """Get agents with caching to avoid reloading on every request."""
    global _cached_agents, _cached_agents_created_at

    with _cached_agents_lock:
        needs_refresh = (
            force_refresh or
            _cached_agents is None or
            _cached_agents_created_at is None or
            (time.time() - _cached_agents_created_at) >= AGENTS_CACHE_TTL_SECONDS
        )

        if needs_refresh:
            logging.info("Loading/refreshing agents cache")
            _cached_agents = load_agents_from_folder()
            _cached_agents_created_at = time.time()

        return _cached_agents.copy()


def _reset_agents_cache():
    """Reset the agents cache to force reload on next request."""
    global _cached_agents, _cached_agents_created_at
    with _cached_agents_lock:
        _cached_agents = None
        _cached_agents_created_at = None
        logging.info("Agents cache reset - will reload on next request")


# =============================================================================
# AGENT LOADING
# =============================================================================

def _load_single_agent_local(file: str) -> Result[BasicAgent, AgentLoadError]:
    """Load a single agent from local agents/ folder. Returns Result."""
    module_name = file[:-3]
    try:
        module = importlib.import_module(f'agents.{module_name}')
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BasicAgent) and obj is not BasicAgent:
                return Success(obj())
        return Failure(AgentLoadError(file, 'local', 'no_class', 'No BasicAgent subclass found'))
    except SyntaxError as e:
        return Failure(AgentLoadError(file, 'local', 'syntax', str(e)))
    except ImportError as e:
        return Failure(AgentLoadError(file, 'local', 'import', str(e)))
    except Exception as e:
        return Failure(AgentLoadError(file, 'local', 'instantiation', str(e)))


def _load_single_agent_azure(file_name: str, file_content: str) -> Result[BasicAgent, AgentLoadError]:
    """Load a single agent from Azure File Storage content. Returns Result."""
    temp_dir = "/tmp/agents"
    temp_file = f"{temp_dir}/{file_name}"
    module_name = file_name[:-3]

    try:
        os.makedirs(temp_dir, exist_ok=True)
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(file_content)

        if temp_dir not in sys.path:
            sys.path.append(temp_dir)

        spec = importlib.util.spec_from_file_location(module_name, temp_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BasicAgent) and obj is not BasicAgent:
                agent_instance = obj()
                os.remove(temp_file)
                return Success(agent_instance)

        os.remove(temp_file)
        return Failure(AgentLoadError(file_name, 'azure', 'no_class', 'No BasicAgent subclass found'))

    except SyntaxError as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return Failure(AgentLoadError(file_name, 'azure', 'syntax', str(e)))
    except ImportError as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return Failure(AgentLoadError(file_name, 'azure', 'import', str(e)))
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return Failure(AgentLoadError(file_name, 'azure', 'instantiation', str(e)))


def load_agents_from_folder():
    """Load agents from local folder and Azure File Storage agents/ share."""
    agents_directory = os.path.join(os.path.dirname(__file__), "agents")
    files_in_agents_directory = os.listdir(agents_directory)
    agent_files = [f for f in files_in_agents_directory if f.endswith(".py") and f not in ["__init__.py", "basic_agent.py"]]

    declared_agents = {}
    all_errors: list[AgentLoadError] = []

    for file in agent_files:
        result = _load_single_agent_local(file)
        if result.is_success:
            declared_agents[result.value.name] = result.value
        else:
            all_errors.append(result.error)

    storage_manager = get_storage_manager()

    try:
        azure_agent_files = storage_manager.list_files('agents')
        for file in azure_agent_files:
            if not file.name.endswith('_agent.py'):
                continue

            file_content = storage_manager.read_file('agents', file.name)
            if file_content is None:
                all_errors.append(AgentLoadError(file.name, 'azure', 'file_read', 'Could not read file content'))
                continue

            result = _load_single_agent_azure(file.name, file_content)
            if result.is_success:
                declared_agents[result.value.name] = result.value
            else:
                all_errors.append(result.error)

    except Exception as e:
        logging.error(f"Error listing agents from Azure File Share: {str(e)}")

    if all_errors:
        logging.warning(f"Agent loading completed with {len(all_errors)} error(s):")
        for error in all_errors:
            logging.error(f"  - {error}")

    logging.info(f"Successfully loaded {len(declared_agents)} agent(s): {list(declared_agents.keys())}")
    return declared_agents


# =============================================================================
# STRING SAFETY & CORS
# =============================================================================

def ensure_string_content(message):
    """Ensures message content is converted to a string regardless of input type."""
    if message is None:
        return {"role": "user", "content": ""}

    if not isinstance(message, dict):
        return {"role": "user", "content": str(message) if message is not None else ""}

    message = message.copy()

    if 'role' not in message:
        message['role'] = 'user'

    if 'content' in message:
        content = message['content']
        message['content'] = str(content) if content is not None else ''
    else:
        message['content'] = ''

    return message


def ensure_string_function_args(function_call):
    """Ensures function call arguments are properly stringified."""
    if not function_call:
        return None
    if not hasattr(function_call, 'arguments'):
        return None
    if function_call.arguments is None:
        return None
    if isinstance(function_call.arguments, (dict, list)):
        return json.dumps(function_call.arguments)
    return str(function_call.arguments)


def build_cors_response(origin):
    """Builds CORS response headers. Safely handles None origin."""
    return {
        "Access-Control-Allow-Origin": str(origin) if origin else "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "86400",
    }


# =============================================================================
# ASSISTANT CLASS
# =============================================================================

class Assistant:
    def __init__(self, declared_agents):
        self.config = {
            'assistant_name': str(os.environ.get('ASSISTANT_NAME', 'BusinessInsightBot')),
            'characteristic_description': str(os.environ.get('CHARACTERISTIC_DESCRIPTION', 'helpful business assistant'))
        }
        self.client = _get_openai_client()
        self.known_agents = self.reload_agents(declared_agents)
        self.user_guid = DEFAULT_USER_GUID
        self.shared_memory = None
        self.user_memory = None
        self.storage_manager = get_storage_manager()
        self._initialize_context_memory(DEFAULT_USER_GUID)

    def reload_agents(self, agent_objects):
        known_agents = {}
        if isinstance(agent_objects, dict):
            for agent_name, agent in agent_objects.items():
                if hasattr(agent, 'name'):
                    known_agents[agent.name] = agent
                else:
                    known_agents[str(agent_name)] = agent
        elif isinstance(agent_objects, list):
            for agent in agent_objects:
                if hasattr(agent, 'name'):
                    known_agents[agent.name] = agent
        else:
            logging.warning(f"Unexpected agent_objects type: {type(agent_objects)}")
        return known_agents

    def _check_first_message_for_guid(self, conversation_history):
        """Check if the first message contains only a GUID."""
        if not conversation_history or len(conversation_history) == 0:
            return None
        first_message = conversation_history[0]
        if first_message.get('role') == 'user':
            content = first_message.get('content')
            if content is None:
                return None
            content = str(content).strip()
            guid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
            if guid_pattern.match(content):
                return content
        return None

    def _initialize_context_memory(self, user_guid=None):
        """Initialize context memory with separate shared and user-specific memories."""
        try:
            context_memory_agent = self.known_agents.get('ContextMemory')
            if not context_memory_agent:
                self.shared_memory = "No shared context memory available."
                self.user_memory = "No specific context memory available."
                return

            self.storage_manager.set_memory_context(None)
            self.shared_memory = str(context_memory_agent.perform(full_recall=True))

            if not user_guid:
                user_guid = DEFAULT_USER_GUID

            self.storage_manager.set_memory_context(user_guid)
            self.user_memory = str(context_memory_agent.perform(user_guid=user_guid, full_recall=True))

        except Exception as e:
            logging.warning(f"Error initializing context memory: {str(e)}")
            self.shared_memory = "Context memory initialization failed."
            self.user_memory = "Context memory initialization failed."

    def extract_user_guid(self, text):
        """Extract a GUID from user input, only if it's the entire message."""
        if text is None:
            return None

        text_str = str(text).strip()

        guid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        match = guid_pattern.match(text_str)
        if match:
            return match.group(0)

        labeled_guid_pattern = re.compile(r'^guid[:=\s]+([0-9a-f-]{36})$', re.IGNORECASE)
        match = labeled_guid_pattern.match(text_str)
        if match:
            return match.group(1)

        return None

    def _uses_tools_api(self):
        """Determine if the current model uses the tools API or legacy functions API."""
        deployment_name = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-deployment').lower()

        legacy_models = ['gpt-35', 'gpt-4-turbo', 'gpt-4-32k']

        if 'gpt-4o' in deployment_name:
            return True

        for legacy in legacy_models:
            if legacy in deployment_name:
                return False

        if 'gpt-4' in deployment_name and 'gpt-4o' not in deployment_name:
            return False

        return True

    def _get_tools_list(self):
        """Build OpenAI tools/functions array from agent metadata."""
        if self._uses_tools_api():
            tools = []
            for agent in self.known_agents.values():
                if hasattr(agent, 'metadata'):
                    tools.append({"type": "function", "function": agent.metadata})
            return tools
        else:
            functions = []
            for agent in self.known_agents.values():
                if hasattr(agent, 'metadata'):
                    functions.append(agent.metadata)
            return functions

    def _prepare_messages(self, conversation_history):
        """Build system prompt + conversation history with memory context."""
        if not isinstance(conversation_history, list):
            conversation_history = []

        messages = []

        system_message = {
            "role": "system",
            "content": f"""
<identity>
You are a Microsoft Copilot assistant named {str(self.config.get('assistant_name', 'Assistant'))}, operating within Microsoft Teams.
</identity>

<shared_memory_output>
These are memories accessible by all users of the system:
{str(self.shared_memory)}
</shared_memory_output>

<specific_memory_output>
These are memories specific to the current conversation:
{str(self.user_memory)}
</specific_memory_output>

<context_instructions>
- <shared_memory_output> represents common knowledge shared across all conversations
- <specific_memory_output> represents specific context for the current conversation
- Apply specific context with higher precedence than shared context
- Synthesize information from both contexts for comprehensive responses
</context_instructions>

<agent_usage>
IMPORTANT: You must be honest and accurate about agent usage:
- NEVER pretend or imply you've executed an agent when you haven't actually called it
- NEVER say "using my agent" unless you are actually making a function call to that agent
- NEVER fabricate success messages about data operations that haven't occurred
- If you need to perform an action and don't have the necessary agent, say so directly
- When a user requests an action, either:
  1. Call the appropriate agent and report actual results, or
  2. Say "I don't have the capability to do that" and suggest an alternative
  3. If no details are provided besides the request to run an agent, infer the necessary input parameters by "reading between the lines" of the conversation context so far
- ALWAYS trust the tool schema provided - if a parameter is defined in the schema, USE IT
</agent_usage>

<response_format>
CRITICAL: You must structure your response in TWO distinct parts separated by the delimiter |||VOICE|||

1. FIRST PART (before |||VOICE|||): Your full formatted response
   - Use **bold** for emphasis
   - Use `code blocks` for technical content
   - Apply --- for horizontal rules to separate sections
   - Utilize > for important quotes or callouts
   - Format code with ```language syntax highlighting
   - Create numbered lists with proper indentation
   - Add personality when appropriate
   - Apply # ## ### headings for clear structure

2. SECOND PART (after |||VOICE|||): A concise voice response
   - Maximum 1-2 sentences
   - Pure conversational English with NO formatting
   - Extract only the most critical information
   - Sound like a colleague speaking casually over a cubicle wall
   - Be natural and conversational, not robotic
   - Focus on the key takeaway or action item
   - Example: "I found those Q3 sales figures - revenue's up 12 percent from last quarter." or "Sure, I'll pull up that customer data for you right now."

EXAMPLE FORMAT:
Here's the detailed analysis you requested:

**Key Findings:**
- Revenue increased by 12%
- Customer satisfaction scores improved

|||VOICE|||
Revenue's up 12 percent and customers are happier - looking good for Q3.
</response_format>
"""
        }
        messages.append(ensure_string_content(system_message))

        guid_only_first_message = self._check_first_message_for_guid(conversation_history)
        start_idx = 1 if guid_only_first_message else 0

        # Trim conversation history to last 20 messages
        trimmed_history = conversation_history[start_idx:]
        if len(trimmed_history) > 20:
            trimmed_history = trimmed_history[-20:]

        for msg in trimmed_history:
            messages.append(ensure_string_content(msg))

        return messages

    def _execute_agent(self, agent_name, json_data):
        """Run an agent by name with parameters. Returns (result_str, error_str)."""
        agent = self.known_agents.get(agent_name)
        if not agent:
            return None, f"Agent '{agent_name}' does not exist"

        try:
            agent_parameters = safe_json_loads(json_data)

            sanitized_parameters = {}
            for key, value in agent_parameters.items():
                sanitized_parameters[key] = "" if value is None else value

            if agent_name in ['ManageMemory', 'ContextMemory']:
                sanitized_parameters['user_guid'] = self.user_guid

            result = agent.perform(**sanitized_parameters)
            result = str(result) if result is not None else "Agent completed successfully"
            return result, None

        except Exception as e:
            return None, f"Error executing agent: {str(e)}"

    def _get_openai_api_call(self, messages) -> Result:
        """Make OpenAI API call with typed error handling."""
        deployment_name = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-deployment')
        use_tools = self._uses_tools_api()

        try:
            if use_tools:
                tools = self._get_tools_list()
                if tools:
                    response = self.client.chat.completions.create(
                        model=deployment_name, messages=messages,
                        tools=tools, tool_choice="auto"
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=deployment_name, messages=messages
                    )
            else:
                functions = self._get_tools_list()
                if functions:
                    response = self.client.chat.completions.create(
                        model=deployment_name, messages=messages,
                        functions=functions, function_call="auto"
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=deployment_name, messages=messages
                    )
            return Success(response)

        except RateLimitError as e:
            logging.warning(f"Rate limit hit: {e}")
            return Failure(APIError('rate_limit', str(e), 429, retryable=True))
        except AuthenticationError as e:
            logging.error(f"Auth error: {e}")
            return Failure(APIError('auth', str(e), 401, retryable=False))
        except APITimeoutError as e:
            logging.warning(f"Timeout: {e}")
            return Failure(APIError('timeout', str(e), 408, retryable=True))
        except BadRequestError as e:
            logging.error(f"Bad request: {e}")
            return Failure(APIError('invalid_request', str(e), 400, retryable=False))
        except OpenAIAPIError as e:
            status = getattr(e, 'status_code', 500)
            retryable = status >= 500
            logging.error(f"OpenAI API error ({status}): {e}")
            return Failure(APIError('server', str(e), status, retryable=retryable))
        except Exception as e:
            logging.error(f"Unexpected error in OpenAI API call: {e}")
            return Failure(APIError('unknown', str(e), None, retryable=False))

    def _parse_response_with_voice(self, content):
        """Parse the response to extract formatted and voice parts."""
        if not content:
            return "", ""

        parts = content.split("|||VOICE|||")

        if len(parts) >= 2:
            formatted_response = parts[0].strip()
            voice_response = parts[1].strip()
        else:
            formatted_response = content.strip()
            sentences = formatted_response.split('.')
            if sentences:
                voice_response = sentences[0].strip() + "."
                voice_response = re.sub(r'\*\*|`|#|>|---|[\U00010000-\U0010ffff]|[\u2600-\u26FF]|[\u2700-\u27BF]', '', voice_response)
                voice_response = re.sub(r'\s+', ' ', voice_response).strip()
            else:
                voice_response = "I've completed your request."

        return formatted_response, voice_response

    def run(self, prompt, conversation_history, max_retries=3, retry_delay=2):
        """Main conversation loop: call OpenAI → execute agents → return response."""
        guid_from_history = self._check_first_message_for_guid(conversation_history)
        guid_from_prompt = self.extract_user_guid(prompt)
        target_guid = guid_from_history or guid_from_prompt

        if target_guid and target_guid != self.user_guid:
            self.user_guid = target_guid
            self._initialize_context_memory(self.user_guid)
            logging.info(f"User GUID updated to: {self.user_guid}")
        elif not self.user_guid:
            self.user_guid = DEFAULT_USER_GUID
            self._initialize_context_memory(self.user_guid)
            logging.info(f"Using default User GUID: {self.user_guid}")

        prompt = str(prompt) if prompt is not None else ""

        if guid_from_prompt and prompt.strip() == guid_from_prompt and self.user_guid == guid_from_prompt:
            return (
                "I've successfully loaded your conversation memory. How can I assist you today?",
                "I've loaded your memory - what can I help you with?",
                ""
            )

        messages = self._prepare_messages(conversation_history)

        last_user_msg = None
        for msg in reversed(conversation_history):
            if msg.get('role') == 'user':
                last_user_msg = str(msg.get('content', '')).strip()
                break

        if last_user_msg != prompt.strip():
            messages.append(ensure_string_content({"role": "user", "content": prompt}))

        agent_logs = []
        retry_count = 0
        use_tools_api = self._uses_tools_api()

        while retry_count < max_retries:
            api_result = self._get_openai_api_call(messages)

            if api_result.is_failure:
                error = api_result.error
                retry_count += 1
                if error.retryable and retry_count < max_retries:
                    logging.warning(f"Retryable API error ({retry_count}/{max_retries}): {error}")
                    time.sleep(retry_delay)
                    continue
                else:
                    logging.error(f"API call failed: {error}")
                    error_msg = f"I encountered an error: {error.error_type}"
                    if error.error_type == 'rate_limit':
                        error_msg = "I'm experiencing high demand right now. Please try again in a moment."
                    elif error.error_type == 'auth':
                        error_msg = "There's an authentication issue. Please contact support."
                    return error_msg, "Something went wrong - try again.", ""

            response = api_result.value
            assistant_msg = response.choices[0].message
            msg_contents = assistant_msg.content or ""

            has_function_call = False
            agent_name = None
            json_data = "{}"
            tool_call_id = None

            if use_tools_api:
                if assistant_msg.tool_calls:
                    has_function_call = True
                    tool_call = assistant_msg.tool_calls[0]
                    agent_name = str(tool_call.function.name)
                    json_data = tool_call.function.arguments or "{}"
                    tool_call_id = tool_call.id
            else:
                if assistant_msg.function_call:
                    has_function_call = True
                    agent_name = str(assistant_msg.function_call.name)
                    json_data = assistant_msg.function_call.arguments or "{}"

            if not has_function_call:
                formatted_response, voice_response = self._parse_response_with_voice(msg_contents)
                return formatted_response, voice_response, "\n".join(map(str, agent_logs))

            result, error = self._execute_agent(agent_name, json_data)
            if error:
                return error, "I hit an error processing that.", ""

            agent_logs.append(f"Performed {agent_name} and got result: {result}")

            if use_tools_api:
                messages.append({
                    "role": "assistant",
                    "content": msg_contents if msg_contents else None,
                    "tool_calls": [{
                        "id": tool_call_id,
                        "type": "function",
                        "function": {"name": agent_name, "arguments": json_data}
                    }]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result
                })
            else:
                messages.append({
                    "role": "assistant",
                    "content": msg_contents if msg_contents else None,
                    "function_call": {"name": agent_name, "arguments": json_data}
                })
                messages.append({
                    "role": "function",
                    "name": agent_name,
                    "content": result
                })

            # Check if agent result indicates follow-up is needed
            needs_follow_up = False
            try:
                result_json = json.loads(result)
                if isinstance(result_json, dict):
                    if result_json.get('error') or result_json.get('status') == 'incomplete':
                        needs_follow_up = True
                    if result_json.get('requires_additional_action') is True:
                        needs_follow_up = True
            except (json.JSONDecodeError, ValueError):
                pass

            if not needs_follow_up:
                final_result = self._get_openai_api_call(messages)
                if final_result.is_failure:
                    logging.error(f"Final API call failed: {final_result.error}")
                    return "I completed the action but couldn't generate a summary.", "Action completed.", "\n".join(map(str, agent_logs))
                final_msg = final_result.value.choices[0].message
                final_content = final_msg.content or ""
                formatted_response, voice_response = self._parse_response_with_voice(final_content)
                return formatted_response, voice_response, "\n".join(map(str, agent_logs))

            retry_count += 1

        return "Service temporarily unavailable. Please try again later.", "Service is down - try again later.", ""


# =============================================================================
# AZURE FUNCTION APP & ENDPOINTS
# =============================================================================

app = func.FunctionApp()


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint for monitoring and warm-up."""
    start_time = time.time()
    origin = req.headers.get('origin')
    cors_headers = build_cors_response(origin)

    if req.method == 'OPTIONS':
        return func.HttpResponse(status_code=200, headers=cors_headers)

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "checks": {}
    }

    try:
        health_status["checks"]["basic"] = {
            "status": "pass",
            "message": "Function app is responding"
        }

        deep_check = req.params.get('deep', '').lower() == 'true'

        if deep_check:
            try:
                _get_openai_client()
                health_status["checks"]["openai_client"] = {
                    "status": "pass",
                    "message": "OpenAI client initialized successfully",
                    "client_age_seconds": round(time.time() - (_openai_client_created_at or time.time()), 2)
                }
            except Exception as e:
                health_status["checks"]["openai_client"] = {
                    "status": "fail",
                    "message": f"OpenAI client initialization failed: {str(e)}"
                }
                health_status["status"] = "degraded"

            try:
                agents = _get_cached_agents()
                health_status["checks"]["agents"] = {
                    "status": "pass",
                    "message": f"Loaded {len(agents)} agents",
                    "cache_age_seconds": round(time.time() - (_cached_agents_created_at or time.time()), 2) if _cached_agents_created_at else 0
                }
            except Exception as e:
                health_status["checks"]["agents"] = {
                    "status": "fail",
                    "message": f"Agent loading failed: {str(e)}"
                }
                health_status["status"] = "degraded"

            try:
                storage = get_storage_manager()
                if storage:
                    health_status["checks"]["storage"] = {"status": "pass", "message": "Storage manager initialized"}
                else:
                    health_status["checks"]["storage"] = {"status": "warn", "message": "Storage manager not configured (running locally)"}
            except Exception as e:
                health_status["checks"]["storage"] = {"status": "fail", "message": f"Storage check failed: {str(e)}"}
                health_status["status"] = "degraded"

        health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

        return func.HttpResponse(
            json.dumps(health_status, indent=2),
            status_code=200, mimetype="application/json", headers=cors_headers
        )

    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
        health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

        return func.HttpResponse(
            json.dumps(health_status, indent=2),
            status_code=500, mimetype="application/json", headers=cors_headers
        )


@app.route(route="trigger/copilot-studio", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def copilot_studio_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    Direct agent invocation from Copilot Studio / Power Automate flows.

    Expected Payload:
        {"agent": "AgentName", "action": "action_name", "parameters": {...}}
    """
    origin = req.headers.get('origin')
    cors_headers = build_cors_response(origin)

    if req.method == 'OPTIONS':
        return func.HttpResponse(status_code=200, headers=cors_headers)

    try:
        payload = req.get_json()

        if 'agent' not in payload or 'action' not in payload:
            return func.HttpResponse(
                json.dumps({"error": "Missing required 'agent' and 'action' fields in payload"}),
                status_code=400, mimetype="application/json", headers=cors_headers
            )

        agent_name = payload['agent']
        action = payload['action']
        parameters = payload.get('parameters', {})
        parameters['action'] = action

        agents = _get_cached_agents()
        if agent_name not in agents:
            return func.HttpResponse(
                json.dumps({"error": f"Agent not found: {agent_name}"}),
                status_code=404, mimetype="application/json", headers=cors_headers
            )

        agent = agents[agent_name]
        result = str(agent.perform(**parameters))

        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "response": result,
                "copilot_studio_format": {
                    "type": "event",
                    "name": "agent.response",
                    "value": {"success": True, "message": result}
                }
            }),
            status_code=200, mimetype="application/json", headers=cors_headers
        )

    except Exception as e:
        logging.error(f"Copilot Studio trigger error: {e}")
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "error": str(e),
                "copilot_studio_format": {
                    "type": "event",
                    "name": "agent.error",
                    "value": {"success": False, "message": str(e)}
                }
            }),
            status_code=500, mimetype="application/json", headers=cors_headers
        )


@app.route(route="businessinsightbot_function", auth_level=func.AuthLevel.FUNCTION)
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main conversation endpoint for the memory agent platform."""
    logging.info('Python HTTP trigger function processed a request.')

    origin = req.headers.get('origin')
    cors_headers = build_cors_response(origin)

    if req.method == 'OPTIONS':
        return func.HttpResponse(status_code=200, headers=cors_headers)

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON in request body", status_code=400, headers=cors_headers)

    if not req_body:
        return func.HttpResponse("Missing JSON payload in request body", status_code=400, headers=cors_headers)

    user_input = req_body.get('user_input')
    user_input = str(user_input) if user_input is not None else ""

    conversation_history = req_body.get('conversation_history', [])
    if not isinstance(conversation_history, list):
        conversation_history = []

    user_guid = req_body.get('user_guid')

    is_guid_only = re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', user_input.strip(), re.IGNORECASE)

    if not is_guid_only and not user_input.strip():
        return func.HttpResponse(
            json.dumps({"error": "Missing or empty user_input in JSON payload"}),
            status_code=400, mimetype="application/json", headers=cors_headers
        )

    try:
        agents = _get_cached_agents()
        assistant = Assistant(agents)

        if user_guid:
            assistant.user_guid = user_guid
            assistant._initialize_context_memory(user_guid)
        elif is_guid_only:
            assistant.user_guid = user_input.strip()
            assistant._initialize_context_memory(user_input.strip())

        assistant_response, voice_response, agent_logs = assistant.run(user_input, conversation_history)

        response = {
            "assistant_response": str(assistant_response),
            "voice_response": str(voice_response),
            "agent_logs": str(agent_logs),
            "user_guid": assistant.user_guid
        }

        return func.HttpResponse(json.dumps(response), mimetype="application/json", headers=cors_headers)

    except Exception as e:
        error_str = str(e)

        auth_error_indicators = [
            'AuthenticationError', 'AuthorizationFailure', 'AuthenticationFailed',
            '401', '403', 'token', 'credential', 'Unauthorized', 'invalid_api_key'
        ]

        if any(ind in error_str for ind in auth_error_indicators):
            logging.warning(f"Auth error detected, resetting all caches: {error_str}")
            _reset_openai_client()
            try:
                from utils.storage_factory import reset_storage_manager
                reset_storage_manager()
                logging.info("All credential caches reset - next request will use fresh credentials")
            except Exception as reset_err:
                logging.error(f"Failed to reset storage manager: {reset_err}")

        if any(t in error_str for t in ['timeout', 'Timeout', 'timed out']):
            return func.HttpResponse(
                json.dumps({
                    "error": "Request timed out",
                    "details": "The request took too long to process. Please try again with a simpler query.",
                    "suggestion": "Try breaking your request into smaller parts."
                }),
                status_code=408, mimetype="application/json", headers=cors_headers
            )

        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": error_str}),
            status_code=500, mimetype="application/json", headers=cors_headers
        )