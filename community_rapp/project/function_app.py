"""
Base Memory Agent Platform for Azure Functions.

A modular AI assistant built on Azure Functions with GPT-4 integration. Features
a dynamic agent architecture with persistent memory across sessions using Azure
File Storage. Supports multi-user conversations with user-specific and shared
memory contexts.

Endpoints:
    GET  /api/health                        — Health check (anonymous)
    GET  /api/version                       — Runtime version (anonymous)
    POST /api/chat                          — Grail-compatible conversation endpoint
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
import uuid
from agents.basic_agent import BasicAgent
from openai import AzureOpenAI, OpenAI, APIError as OpenAIAPIError, RateLimitError, AuthenticationError, APITimeoutError, BadRequestError
from azure.identity import (
    ChainedTokenCredential,
    ManagedIdentityCredential,
    AzureCliCredential,
    get_bearer_token_provider
)
from utils.copilot_auth import (
    get_copilot_client, is_copilot_available,
    start_device_code_flow, poll_device_code, save_token,
)
from datetime import datetime
import time
import threading
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
APP_VERSION = "1.0.0"
MAX_TOOL_ROUNDS = 3
TOOL_ROUND_FALLBACK = (
    "I couldn't finish that within the available tool steps. "
    "Try rephrasing, or breaking it into smaller steps."
)

# Singleton OpenAI client - created once, reused across requests
_openai_client = None
_openai_client_lock = threading.Lock()
_openai_client_created_at = None
OPENAI_CLIENT_TTL_SECONDS = 30 * 60  # 30 minutes

# LLM backend: "azure" (Azure OpenAI) or "copilot" (GitHub Copilot, local dev)
_llm_backend = None
_copilot_model = None

# Device code auth flow state
_device_code_data = None  # Holds device_code, user_code, verification_uri
_device_code_polling = False

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
    """Get or create a singleton OpenAI client with TTL refresh.

    Backend selection (in order):
      1. Azure OpenAI — if AZURE_OPENAI_ENDPOINT is configured
      2. GitHub Copilot — if a GitHub token is available (local dev, no Azure needed)
      3. Error — no LLM backend available
    """
    global _openai_client, _openai_client_created_at, _llm_backend, _copilot_model

    with _openai_client_lock:
        needs_refresh = (
            _openai_client is None or
            _openai_client_created_at is None or
            (time.time() - _openai_client_created_at) >= OPENAI_CLIENT_TTL_SECONDS
        )

        if needs_refresh:
            azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')

            if azure_endpoint and not azure_endpoint.startswith('https://<'):
                # ── Azure OpenAI (cloud or configured local) ──
                _llm_backend = "azure"
                _copilot_model = None
                logging.info("Creating/refreshing Azure OpenAI client")
                api_key = os.environ.get('AZURE_OPENAI_API_KEY')

                if api_key and not api_key.startswith('<'):
                    logging.info("Using API key authentication for Azure OpenAI")
                    _openai_client = AzureOpenAI(
                        azure_endpoint=azure_endpoint,
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
                        azure_endpoint=azure_endpoint,
                        azure_ad_token_provider=token_provider,
                        api_version=os.environ.get('AZURE_OPENAI_API_VERSION', '2025-01-01-preview'),
                        timeout=OPENAI_REQUEST_TIMEOUT,
                        max_retries=2
                    )
            else:
                # ── GitHub Copilot (local-first, no Azure needed) ──
                client, model = get_copilot_client()
                if client:
                    _llm_backend = "copilot"
                    _copilot_model = model
                    _openai_client = client
                    logging.info(f"Using GitHub Copilot backend (model: {model})")
                else:
                    _llm_backend = None
                    _copilot_model = None
                    _openai_client = None
                    logging.warning(
                        "No LLM backend available. Configure Azure OpenAI in "
                        "local.settings.json, or authenticate with GitHub Copilot "
                        "(set GITHUB_TOKEN or run the brainstem's login flow)."
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


def _start_device_code_auth():
    """Start the GitHub device code flow and poll in background."""
    global _device_code_data, _device_code_polling

    if _device_code_polling:
        return _device_code_data  # Already in progress

    flow = start_device_code_flow()
    if not flow:
        return None

    _device_code_data = flow
    _device_code_polling = True

    def _poll():
        global _device_code_data, _device_code_polling
        device_code = flow.get("device_code")
        interval = flow.get("interval", 5)
        expires_in = flow.get("expires_in", 900)
        deadline = time.time() + expires_in

        while time.time() < deadline:
            time.sleep(interval)
            result = poll_device_code(device_code)
            if result and "access_token" in result:
                save_token(result)
                _reset_openai_client()
                _device_code_data = None
                _device_code_polling = False
                logging.info("GitHub Copilot authenticated via device code flow")
                return
            if result and result.get("status") == "expired":
                break

        _device_code_data = None
        _device_code_polling = False
        logging.warning("Device code flow expired or failed")

    thread = threading.Thread(target=_poll, daemon=True)
    thread.start()
    return flow


def _get_auth_message():
    """If no LLM is available, start device code flow and return auth instructions."""
    if _llm_backend is not None:
        return None  # LLM is available, no auth needed

    flow = _device_code_data or _start_device_code_auth()
    if not flow:
        return (
            "No AI backend is configured. To enable AI responses:\n\n"
            "**Option 1 — GitHub Copilot (recommended for local dev):**\n"
            "Set `GITHUB_TOKEN` in your environment and restart.\n\n"
            "**Option 2 — Azure OpenAI:**\n"
            "Edit `local.settings.json` and set your Azure OpenAI endpoint and key."
        )

    user_code = flow.get("user_code", "")
    verification_uri = flow.get("verification_uri", "https://github.com/login/device")

    return (
        f"**Authenticate with GitHub to enable AI responses.**\n\n"
        f"1. Go to: **{verification_uri}**\n"
        f"2. Enter code: **{user_code}**\n"
        f"3. Authorize the app\n\n"
        f"I'm waiting for authorization — once you complete the steps above, "
        f"send another message and I'll be ready to chat.\n\n"
        f"|||VOICE|||Go to {verification_uri} and enter code {user_code} to authenticate."
    )


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
        with open(temp_file, 'w') as f:
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
        self.requested_model = self._get_requested_model()
        self.responded_model = self.requested_model
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

    def _prepare_messages(
        self,
        conversation_history,
        *,
        voice_mode=True,
        skip_guid_message=True,
        trim_history=True
    ):
        """Build system prompt + conversation history with memory context."""
        if not isinstance(conversation_history, list):
            conversation_history = []

        messages = []

        system_content = f"""
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
        if not voice_mode:
            system_content = re.sub(
                r"\n<response_format>.*?</response_format>\n?",
                "\n",
                system_content,
                flags=re.DOTALL
            )

        system_message = {
            "role": "system",
            "content": system_content
        }
        messages.append(ensure_string_content(system_message))

        guid_only_first_message = (
            self._check_first_message_for_guid(conversation_history)
            if skip_guid_message else None
        )
        start_idx = 1 if guid_only_first_message else 0

        trimmed_history = conversation_history[start_idx:]
        if trim_history and len(trimmed_history) > 20:
            trimmed_history = trimmed_history[-20:]

        for msg in trimmed_history:
            messages.append(ensure_string_content(msg))

        return messages

    def _execute_agent(self, agent_name, json_data):
        """Run one tool call and return its result plus the grail-format log line."""
        try:
            agent_parameters = json.loads(json_data)
        except (TypeError, json.JSONDecodeError):
            agent_parameters = None

        if not isinstance(agent_parameters, dict):
            result = "Error: Tool arguments must be a valid JSON object."
            return result, f"[{agent_name}] {result}"

        agent = self.known_agents.get(agent_name)
        if not agent:
            result = f"Agent '{agent_name}' not found."
            return result, result

        try:
            if agent_name in ['ManageMemory', 'ContextMemory']:
                agent_parameters['user_guid'] = self.user_guid

            result = str(agent.perform(**agent_parameters))
            return result, f"[{agent_name}] {result}"

        except Exception as e:
            result = f"Error: {e}"
            return result, f"[{agent_name}] ERROR: {e}"

    def _get_requested_model(self):
        if _llm_backend == "copilot" and _copilot_model:
            return _copilot_model
        return os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-deployment')

    def _get_openai_api_call(self, messages, include_tools=True) -> Result:
        """Make OpenAI API call with typed error handling."""
        deployment_name = self._get_requested_model()
        use_tools = self._uses_tools_api()

        try:
            if use_tools and include_tools:
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
            elif include_tools:
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

    def _call_model(self, messages, include_tools, max_retries, retry_delay):
        """Call the model, retrying only retryable transport/provider failures."""
        api_result = None
        for retry_count in range(max_retries):
            api_result = self._get_openai_api_call(
                messages,
                include_tools=include_tools
            )
            if api_result.is_success or not api_result.error.retryable:
                return api_result
            if retry_count + 1 < max_retries:
                logging.warning(
                    "Retryable API error (%s/%s): %s",
                    retry_count + 1,
                    max_retries,
                    api_result.error
                )
                time.sleep(retry_delay)
        return api_result

    def _format_model_response(self, content, voice_mode, parse_voice):
        if voice_mode and parse_voice:
            return self._parse_response_with_voice(content)
        return content or "", ""

    def _api_failure_response(self, error):
        logging.error(f"API call failed: {error}")
        error_msg = f"I encountered an error: {error.error_type}"
        if error.error_type == 'rate_limit':
            error_msg = "I'm experiencing high demand right now. Please try again in a moment."
        elif error.error_type == 'auth':
            error_msg = "There's an authentication issue. Please contact support."
        return error_msg, "Something went wrong - try again.", ""

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

    def run(
        self,
        prompt,
        conversation_history,
        max_retries=3,
        retry_delay=2,
        *,
        voice_mode=True,
        parse_voice=True,
        manage_guid=True,
        trim_history=True,
        always_append_prompt=False
    ):
        """Main conversation loop: call OpenAI → execute agents → return response."""
        # If no LLM, try to refresh client (device code may have completed)
        if self.client is None:
            self.client = _get_openai_client()

        # Still no LLM? Return auth instructions instead of crashing
        if self.client is None:
            auth_msg = _get_auth_message()
            if auth_msg:
                if not (voice_mode and parse_voice):
                    return auth_msg, "", ""
                parts = auth_msg.split("|||VOICE|||")
                formatted = parts[0].strip()
                voice = parts[1].strip() if len(parts) > 1 else "Please authenticate to enable AI responses."
                return formatted, voice, ""

        prompt = str(prompt) if prompt is not None else ""
        guid_from_prompt = None

        if manage_guid:
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

            if guid_from_prompt and prompt.strip() == guid_from_prompt and self.user_guid == guid_from_prompt:
                return (
                    "I've successfully loaded your conversation memory. How can I assist you today?",
                    "I've loaded your memory - what can I help you with?",
                    ""
                )

        messages = self._prepare_messages(
            conversation_history,
            voice_mode=voice_mode,
            skip_guid_message=manage_guid,
            trim_history=trim_history
        )

        last_user_msg = None
        if not always_append_prompt:
            for msg in reversed(conversation_history):
                if msg.get('role') == 'user':
                    last_user_msg = str(msg.get('content', '')).strip()
                    break

        if always_append_prompt or last_user_msg != prompt.strip():
            messages.append(ensure_string_content({"role": "user", "content": prompt}))

        agent_logs = []
        use_tools_api = self._uses_tools_api()
        self.requested_model = self._get_requested_model()
        self.responded_model = self.requested_model

        for _ in range(MAX_TOOL_ROUNDS):
            api_result = self._call_model(
                messages,
                include_tools=True,
                max_retries=max_retries,
                retry_delay=retry_delay
            )
            if api_result.is_failure:
                return self._api_failure_response(api_result.error)

            response = api_result.value
            self.responded_model = self.requested_model
            assistant_msg = response.choices[0].message
            msg_contents = assistant_msg.content or ""

            if use_tools_api:
                tool_calls = list(assistant_msg.tool_calls or [])
                if not tool_calls:
                    formatted_response, voice_response = self._format_model_response(
                        msg_contents,
                        voice_mode,
                        parse_voice
                    )
                    return formatted_response, voice_response, "\n".join(agent_logs)

                assistant_tool_calls = []
                executable_calls = []
                for tool_call in tool_calls:
                    try:
                        agent_name = str(tool_call.function.name)
                        json_data = tool_call.function.arguments or "{}"
                        tool_call_id = str(tool_call.id)
                    except (AttributeError, TypeError) as e:
                        agent_logs.append(
                            f"[?] Skipped malformed tool call: {str(tool_call)[:80]}"
                        )
                        logging.warning(f"Malformed tool call skipped: {e}")
                        continue

                    assistant_tool_calls.append({
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": agent_name,
                            "arguments": json_data
                        }
                    })
                    executable_calls.append(
                        (tool_call_id, agent_name, json_data)
                    )

                messages.append({
                    "role": "assistant",
                    "content": msg_contents if msg_contents else None,
                    "tool_calls": assistant_tool_calls
                })

                for tool_call_id, agent_name, json_data in executable_calls:
                    result, log_line = self._execute_agent(agent_name, json_data)
                    agent_logs.append(f"Performed {agent_name} and got result: {result}" if getattr(self, "legacy_logs", False) else log_line)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": agent_name,
                        "content": result
                    })
            else:
                function_call = assistant_msg.function_call
                if not function_call:
                    formatted_response, voice_response = self._format_model_response(
                        msg_contents,
                        voice_mode,
                        parse_voice
                    )
                    return formatted_response, voice_response, "\n".join(agent_logs)

                agent_name = str(function_call.name)
                json_data = function_call.arguments or "{}"
                messages.append({
                    "role": "assistant",
                    "content": msg_contents if msg_contents else None,
                    "function_call": {"name": agent_name, "arguments": json_data}
                })
                result, log_line = self._execute_agent(agent_name, json_data)
                agent_logs.append(f"Performed {agent_name} and got result: {result}" if getattr(self, "legacy_logs", False) else log_line)
                messages.append({
                    "role": "function",
                    "name": agent_name,
                    "content": result
                })

        final_result = self._call_model(
            messages,
            include_tools=False,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        final_content = ""
        if final_result.is_success:
            final_response = final_result.value
            self.responded_model = self.requested_model
            final_content = (
                final_response.choices[0].message.content or ""
            ).strip()
        else:
            logging.error(
                f"Final tool-less completion failed: {final_result.error}"
            )

        if not final_content:
            final_content = TOOL_ROUND_FALLBACK

        formatted_response, voice_response = self._format_model_response(
            final_content,
            voice_mode,
            parse_voice
        )
        return formatted_response, voice_response, "\n".join(agent_logs)


# =============================================================================
# AZURE FUNCTION APP & ENDPOINTS
# =============================================================================

app = func.FunctionApp()

_HISTORY_ROLES = {"user", "assistant", "tool"}


def _validate_conversation_history(value):
    """Return (history, error) for the grail-compatible public contract."""
    if value is None:
        return [], None
    if not isinstance(value, list):
        return None, "conversation_history must be an array"
    for index, message in enumerate(value):
        if not isinstance(message, dict):
            return None, f"conversation_history[{index}] must be an object"
        if message.get("role") not in _HISTORY_ROLES:
            return None, f"conversation_history[{index}].role is invalid"
        if not isinstance(message.get("content"), str):
            return None, f"conversation_history[{index}].content must be a string"
    return value, None


def _json_response(payload, status_code=200, headers=None):
    return func.HttpResponse(
        json.dumps(payload),
        status_code=status_code,
        mimetype="application/json",
        headers=headers
    )


def _voice_mode_enabled():
    return os.environ.get("VOICE_MODE", "false").lower() == "true"


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint for monitoring and warm-up."""
    start_time = time.time()
    origin = req.headers.get('origin')
    cors_headers = build_cors_response(origin)

    if req.method == 'OPTIONS':
        return func.HttpResponse(status_code=200, headers=cors_headers)

    try:
        agents = _get_cached_agents()
    except Exception:
        agents = {}

    health_status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": APP_VERSION,
        "agents": list(agents.keys()),
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
                client = _get_openai_client()
                backend = _llm_backend or "none"
                model = _copilot_model if backend == "copilot" else os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'not set')
                if client:
                    health_status["checks"]["llm"] = {
                        "status": "pass",
                        "backend": backend,
                        "model": model,
                        "message": f"LLM client ready ({backend})",
                        "client_age_seconds": round(time.time() - (_openai_client_created_at or time.time()), 2)
                    }
                else:
                    health_status["checks"]["llm"] = {
                        "status": "warn",
                        "backend": "none",
                        "message": "No LLM configured. Agents, storage, and endpoints work — add Azure OpenAI or GitHub Copilot auth for AI responses."
                    }
            except Exception as e:
                health_status["checks"]["llm"] = {
                    "status": "fail",
                    "message": f"LLM client initialization failed: {str(e)}"
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


@app.route(route="version", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def version(req: func.HttpRequest) -> func.HttpResponse:
    """Return the current CommunityRAPP runtime version."""
    return _json_response(
        {"version": APP_VERSION},
        headers=build_cors_response(req.headers.get('origin'))
    )


@app.route(route="chat", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])  # Tier 2 is public and model calls cost money: keyed like the legacy route
def chat(req: func.HttpRequest) -> func.HttpResponse:
    """Grail-compatible Brainstem chat endpoint."""
    cors_headers = build_cors_response(req.headers.get('origin'))

    try:
        data = req.get_json()
    except ValueError:
        data = None

    if not isinstance(data, dict):
        return _json_response(
            {"error": "Request body must be a JSON object"},
            status_code=400,
            headers=cors_headers
        )

    user_input = data.get("user_input", "")
    if not isinstance(user_input, str):
        return _json_response(
            {"error": "user_input must be a string"},
            status_code=400,
            headers=cors_headers
        )
    user_input = user_input.strip()

    history, history_error = _validate_conversation_history(
        data.get("conversation_history", [])
    )
    if history_error:
        return _json_response(
            {"error": history_error},
            status_code=400,
            headers=cors_headers
        )

    session_id = data.get("session_id") or str(uuid.uuid4())

    if not user_input:
        return _json_response(
            {"error": "user_input is required"},
            status_code=400,
            headers=cors_headers
        )

    try:
        assistant = Assistant(_get_cached_agents())
        voice_mode = _voice_mode_enabled()
        response_text, voice_response, agent_logs = assistant.run(
            user_input,
            history,
            voice_mode=voice_mode,
            parse_voice=False,
            manage_guid=False,
            trim_history=False,
            always_append_prompt=True
        )

        if voice_mode and "|||VOICE|||" in response_text:
            response_text, voice_response = (
                part.strip()
                for part in response_text.split("|||VOICE|||", 1)
            )

        response = {
            "response": response_text,
            "session_id": session_id,
            "agent_logs": agent_logs,
            "voice_mode": voice_mode,
            "model": assistant.responded_model,
            "requested_model": assistant.requested_model
        }
        if voice_mode and voice_response:
            response["voice_response"] = voice_response

        return _json_response(response, headers=cors_headers)

    except Exception as e:
        logging.exception("Grail-compatible chat request failed")
        return _json_response(
            {"error": str(e)},
            status_code=500,
            headers=cors_headers
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
            json.dumps({"error": "user_input is required"}),
            status_code=400, mimetype="application/json", headers=cors_headers
        )

    try:
        agents = _get_cached_agents()
        assistant = Assistant(agents)
        assistant.legacy_logs = True  # legacy clients keep the log text they always got

        if user_guid:
            assistant.user_guid = user_guid
            assistant._initialize_context_memory(user_guid)
        elif is_guid_only:
            assistant.user_guid = user_input.strip()
            assistant._initialize_context_memory(user_input.strip())

        assistant_response, voice_response, agent_logs = assistant.run(user_input, conversation_history)

        response = {
            # kernel-conformant /chat envelope (rapp-runtime-parity/1.0 — stem/function_app parity):
            "response": str(assistant_response),
            "session_id": str(assistant.user_guid),
            "agent_logs": str(agent_logs),
            "voice_mode": bool(voice_response),
            "model": assistant.responded_model,
            "requested_model": assistant.requested_model,
            # T2 legacy keys (back-compat for existing clients):
            "assistant_response": str(assistant_response),
            "voice_response": str(voice_response),
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