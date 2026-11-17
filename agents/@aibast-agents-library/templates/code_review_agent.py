import os
import yaml
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re
import ast
from agents.basic_agent import BasicAgent
from utils.azure_file_storage import AzureFileStorageManager
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ToolSet, CodeInterpreterTool, FunctionTool, MessageRole

# Import opentelemetry components
from opentelemetry import trace
from opentelemetry.trace import Span
from azure.monitor.opentelemetry import configure_azure_monitor

# Import the AgentTeam components from the provided code
try:
    from utils.agent_team import AgentTeam, _create_task
    AGENT_TEAM_AVAILABLE = True
except ImportError:
    AGENT_TEAM_AVAILABLE = False
    logging.warning("AgentTeam module not available. Please ensure agent_team.py is in utils folder.")

tracer = trace.get_tracer(__name__)

class CodeReviewAgent(BasicAgent):
    def __init__(self):
        self.name = 'CodeReview'
        self.metadata = {
            "name": self.name,
            "description": "Performs comprehensive code reviews using a team of specialized language experts. Analyzes code for bugs, security, performance, and best practices across multiple programming languages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code_files": {
                        "type": "object",
                        "description": "Dictionary mapping filenames to code content. Example: {'main.py': 'code here', 'app.js': 'code here'}"
                    },
                    "review_from_inbox": {
                        "type": "boolean",
                        "description": "If true, reviews all files in the code-review-inbox folder. Default is false.",
                        "default": False
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional. Specific languages to review. Auto-detects if not provided.",
                        "enum": ["python", "javascript", "typescript", "java", "cpp", "csharp", "go", "rust", "ruby", "php"]
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas to focus the review on.",
                        "enum": ["bugs", "security", "performance", "style", "documentation", "testing", "best_practices"]
                    },
                    "generate_report": {
                        "type": "boolean",
                        "description": "Whether to generate and save a detailed report. Default is true.",
                        "default": True
                    }
                },
                "required": []
            }
        }
        self.storage_manager = AzureFileStorageManager()
        self.inbox_folder = "code-review-inbox"
        self.reports_folder = "code-review-reports"
        self._ensure_folders_exist()
        self.language_configs = self._get_language_configs()
        self.extension_mapping = self._get_extension_mapping()
        
        # Log configuration status
        self._check_configuration()
        
        super().__init__(name=self.name, metadata=self.metadata)

    def _ensure_folders_exist(self):
        """Ensure required folders exist"""
        try:
            self.storage_manager.ensure_directory_exists(self.inbox_folder)
            self.storage_manager.ensure_directory_exists(self.reports_folder)
            
            # Also ensure utils folder exists for agent_team files
            self.storage_manager.ensure_directory_exists("utils")
            
        except Exception as e:
            logging.error(f"Error creating folders: {str(e)}")

    def _check_configuration(self):
        """Check and log configuration status"""
        project_endpoint = os.getenv('CODE_REVIEW_PROJECT_ENDPOINT') or os.getenv('AZURE_AI_PROJECT_ENDPOINT')
        model_deployment = os.getenv('CODE_REVIEW_MODEL_DEPLOYMENT') or os.getenv('CODE_REVIEW_MODEL_DEPLOYMENT_NAME')
        
        if project_endpoint:
            logging.info("CodeReviewAgent: Azure AI Project endpoint configured ✓")
        else:
            logging.warning("CodeReviewAgent: Missing CODE_REVIEW_PROJECT_ENDPOINT or AZURE_AI_PROJECT_ENDPOINT")
            
        if model_deployment:
            logging.info(f"CodeReviewAgent: Using model deployment '{model_deployment}' ✓")
        else:
            logging.info("CodeReviewAgent: No model deployment specified, will use default 'gpt-4.1'")

    def _get_language_configs(self):
        """Language-specific reviewer configurations"""
        return {
            "python": {
                "name": "python-reviewer",
                "instructions": "You are a Python code review expert. Focus on PEP8 compliance, type hints, error handling, docstrings, and Pythonic patterns. Check for common issues like mutable default arguments, proper exception handling, and efficient data structures."
            },
            "javascript": {
                "name": "javascript-reviewer",
                "instructions": "You are a JavaScript code review expert. Focus on ES6+ features, async/await patterns, error handling, performance, and modern JavaScript best practices. Check for common issues like callback hell, promise handling, and proper use of const/let."
            },
            "typescript": {
                "name": "typescript-reviewer",
                "instructions": "You are a TypeScript code review expert. Focus on type safety, interfaces, generics, proper use of any/unknown types, and TypeScript best practices. Ensure types are properly defined and used consistently."
            },
            "java": {
                "name": "java-reviewer",
                "instructions": "You are a Java code review expert. Focus on OOP principles, design patterns, exception handling, thread safety, and Java conventions. Check for proper use of collections, generics, and modern Java features."
            },
            "cpp": {
                "name": "cpp-reviewer",
                "instructions": "You are a C++ code review expert. Focus on memory management, RAII, modern C++ features (C++11/14/17/20), const correctness, and performance. Check for memory leaks, undefined behavior, and proper resource management."
            },
            "csharp": {
                "name": "csharp-reviewer",
                "instructions": "You are a C# code review expert. Focus on .NET best practices, LINQ usage, async/await patterns, proper disposal of resources, and C# conventions. Check for proper use of nullable reference types and modern C# features."
            },
            "go": {
                "name": "go-reviewer",
                "instructions": "You are a Go code review expert. Focus on idiomatic Go, error handling, goroutine safety, channel usage, and simplicity. Check for proper error handling, resource cleanup, and concurrent programming patterns."
            },
            "rust": {
                "name": "rust-reviewer",
                "instructions": "You are a Rust code review expert. Focus on ownership, borrowing, lifetimes, error handling with Result/Option, and Rust idioms. Check for proper use of traits, memory safety, and concurrent programming."
            },
            "ruby": {
                "name": "ruby-reviewer",
                "instructions": "You are a Ruby code review expert. Focus on Ruby idioms, proper use of blocks/procs/lambdas, metaprogramming, testing, and Rails best practices if applicable. Check for code clarity and Ruby conventions."
            },
            "php": {
                "name": "php-reviewer",
                "instructions": "You are a PHP code review expert. Focus on modern PHP practices (PHP 7/8), security (SQL injection, XSS), PSR standards, and framework best practices. Check for proper error handling and type declarations."
            }
        }

    def _get_extension_mapping(self):
        """Map file extensions to languages"""
        return {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }

    def perform(self, **kwargs):
        """Main entry point - creates and manages an AgentTeam for code review"""
        if not AGENT_TEAM_AVAILABLE:
            return "Error: AgentTeam module is not available. Please ensure agent_team.py is properly set up in the utils folder."
        
        code_files = kwargs.get('code_files', {})
        review_from_inbox = kwargs.get('review_from_inbox', False)
        languages_filter = kwargs.get('languages', [])
        focus_areas = kwargs.get('focus_areas', ['bugs', 'performance', 'security', 'best_practices'])
        generate_report = kwargs.get('generate_report', True)
        
        try:
            # If review_from_inbox is true, load files from inbox
            if review_from_inbox or not code_files:
                code_files = self._load_files_from_inbox()
                if not code_files:
                    return "No code files found in the code-review-inbox folder. Please add files to review or provide code directly."
            
            # Check for required environment variables (using separate vars for code review)
            project_endpoint = os.getenv('CODE_REVIEW_PROJECT_ENDPOINT') or os.getenv('AZURE_AI_PROJECT_ENDPOINT')
            model_deployment = os.getenv('CODE_REVIEW_MODEL_DEPLOYMENT') or os.getenv('CODE_REVIEW_MODEL_DEPLOYMENT_NAME') or 'gpt-4.1'
            
            if not project_endpoint:
                return """Error: Code Review environment variables are not configured. 

Please set the following environment variables:
- CODE_REVIEW_PROJECT_ENDPOINT: Your Azure AI Foundry project endpoint
- CODE_REVIEW_MODEL_DEPLOYMENT: Your model deployment name (e.g., 'gpt-4-1106-preview')

Alternative variable names also supported:
- AZURE_AI_PROJECT_ENDPOINT (for project endpoint)
- CODE_REVIEW_MODEL_DEPLOYMENT_NAME (for model deployment)

These are separate from other service configurations to avoid conflicts."""
            
            # Setup tracing if available
            with tracer.start_as_current_span("code-review-agent") as main_span:
                main_span.set_attribute("files.count", len(code_files))
                main_span.set_attribute("languages.filter", languages_filter)
                
                # Perform the review using AgentTeam
                result = self._perform_team_review(
                    code_files, 
                    project_endpoint, 
                    model_deployment, 
                    languages_filter, 
                    focus_areas,
                    main_span
                )
                
                # Generate and save report if requested
                if generate_report:
                    report_path = self._save_review_report(result, code_files)
                    result += f"\n\n📄 Report saved to: {report_path}"
                
                return result
                
        except Exception as e:
            logging.error(f"Error in CodeReviewAgent: {str(e)}")
            return f"Error performing code review: {str(e)}"

    def _load_files_from_inbox(self):
        """Load code files from the inbox folder"""
        code_files = {}
        try:
            files = self.storage_manager.list_files(self.inbox_folder)
            
            for file_info in files:
                filename = file_info.name
                # Skip non-code files
                if filename == 'README.md' or filename.startswith('.'):
                    continue
                
                ext = Path(filename).suffix.lower()
                if ext in self.extension_mapping:
                    content = self.storage_manager.read_file(self.inbox_folder, filename)
                    if content:
                        code_files[filename] = content
                        
        except Exception as e:
            logging.error(f"Error loading files from inbox: {str(e)}")
            
        return code_files

    def _detect_language(self, filename):
        """Detect language from filename"""
        ext = Path(filename).suffix.lower()
        return self.extension_mapping.get(ext, 'unknown')

    def _perform_team_review(self, code_files, project_endpoint, model_deployment, languages_filter, focus_areas, span):
        """Perform code review using AgentTeam"""
        # Check for Code Review specific Azure AD credentials FIRST
        tenant_id = os.getenv('CODE_REVIEW_AZURE_TENANT_ID')
        client_id = os.getenv('CODE_REVIEW_AZURE_CLIENT_ID')
        client_secret = os.getenv('CODE_REVIEW_AZURE_CLIENT_SECRET')
        
        # Use specific credentials if available
        if all([tenant_id, client_id, client_secret]):
            from azure.identity import ClientSecretCredential
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            logging.info("Using Code Review specific Azure AD credentials")
        else:
            # For DefaultAzureCredential, we need to exclude the generic AZURE_* variables
            # to prevent conflicts with other agents
            from azure.identity import DefaultAzureCredential, CredentialUnavailableError
            
            # Temporarily clear generic AZURE_* variables if they exist
            original_azure_vars = {}
            for var in ['AZURE_CLIENT_ID', 'AZURE_TENANT_ID', 'AZURE_CLIENT_SECRET']:
                if var in os.environ:
                    original_azure_vars[var] = os.environ.pop(var)
            
            try:
                # In Azure Functions, this will use Managed Identity
                # Locally, it will use Azure CLI credentials
                credential = DefaultAzureCredential()
                logging.info("Using DefaultAzureCredential (Managed Identity in Azure Functions)")
            finally:
                # Restore the original AZURE_* variables for other agents
                for var, value in original_azure_vars.items():
                    os.environ[var] = value
        
        agents_client = AgentsClient(endpoint=project_endpoint, credential=credential)
        
        # Register _create_task for function calling
        agents_client.enable_auto_function_calls({_create_task})
        
        # Clean up any existing teams with similar names (optional cleanup step)
        try:
            from utils.agent_team import AgentTeam
            # Get and remove any existing teams
            existing_teams = AgentTeam._teams.copy()
            for team_name in existing_teams:
                if "code_review_team" in team_name:
                    try:
                        AgentTeam._remove_team(team_name)
                        logging.info(f"Cleaned up existing team: {team_name}")
                    except:
                        pass
        except:
            pass
        
        with agents_client:
            # Create the agent team with a unique name to avoid conflicts
            team_name = f"code_review_team_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            team = AgentTeam(team_name, agents_client=agents_client)
            
            # Group files by language
            language_files = {}
            for filename, content in code_files.items():
                language = self._detect_language(filename)
                if language != 'unknown':
                    if not languages_filter or language in languages_filter:
                        language_files.setdefault(language, {})[filename] = content
            
            if not language_files:
                return "No supported code files found or no files match the language filter."
            
            span.set_attribute("languages.detected", list(language_files.keys()))
            
            # Add specialized review agents for each language
            for language in language_files.keys():
                if language in self.language_configs:
                    config = self.language_configs[language]
                    
                    # Enhance instructions with focus areas
                    instructions = config['instructions']
                    if focus_areas:
                        instructions += f"\n\nPlease focus particularly on: {', '.join(focus_areas)}"
                    
                    # Create toolset with code interpreter
                    toolset = ToolSet()
                    toolset.add(CodeInterpreterTool())
                    
                    team.add_agent(
                        model=model_deployment,
                        name=config['name'],
                        instructions=instructions,
                        toolset=toolset,
                        can_delegate=False
                    )
            
            # Add documentation consolidation agent
            doc_instructions = """You are a technical documentation expert. Your task is to:
1. Consolidate all code review feedback into a clear, well-structured markdown document
2. Organize findings by severity (Critical, High, Medium, Low)
3. Include specific code examples and line references where applicable
4. Provide actionable recommendations
5. Create an executive summary at the top
6. Use proper markdown formatting with clear sections"""
            
            doc_toolset = ToolSet()
            doc_toolset.add(CodeInterpreterTool())
            
            team.add_agent(
                model=model_deployment,
                name="documentation-agent",
                instructions=doc_instructions,
                toolset=doc_toolset,
                can_delegate=False
            )
            
            # Assemble the team
            team.assemble_team()
            
            # Prepare the review request
            review_requests = []
            for language, files in language_files.items():
                file_contents = []
                for filename, content in files.items():
                    file_contents.append(f"File: {filename}\n```{language}\n{content}\n```")
                review_requests.append(f"Review the following {language} files:\n\n" + "\n\n".join(file_contents))
            
            full_request = "\n\n".join(review_requests)
            full_request += "\n\nAfter all language-specific reviews are complete, please consolidate all findings into a comprehensive markdown report."
            
            # Process the request
            span.add_event("Starting team review process")
            try:
                team.process_request(full_request)
                
                # Extract results from the thread
                thread_id = team._agent_thread.id
                messages = list(agents_client.messages.list(thread_id=thread_id))
                
                # Find the consolidated report
                result = self._extract_review_report(messages)
            finally:
                # Always clean up the team, even if an error occurs
                try:
                    team.dismantle_team()
                    logging.info(f"Successfully dismantled team: {team_name}")
                except Exception as cleanup_error:
                    logging.error(f"Error dismantling team: {str(cleanup_error)}")
            
            return result

    def _extract_review_report(self, messages):
        """Extract the final review report from agent messages"""
        # Look for the documentation agent's final report
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content:
                # Check if this is from an agent/assistant
                if msg.role in ("agent", "assistant"):
                    content = self._extract_content(msg.content)
                    # Look for markdown-formatted content that appears to be a report
                    if content and ('Review' in content or '#' in content or 'Summary' in content):
                        return content
        
        # Fallback: concatenate all agent responses
        agent_responses = []
        for msg in messages:
            if msg.role in ("agent", "assistant") and hasattr(msg, 'content') and msg.content:
                content = self._extract_content(msg.content)
                if content:
                    agent_responses.append(content)
        
        if agent_responses:
            return "\n\n---\n\n".join(agent_responses)
        
        return "Code review completed but no detailed report was generated."

    def _extract_content(self, content):
        """Extract text content from various message formats"""
        # Handle list of content items
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    if isinstance(item['text'], dict) and 'value' in item['text']:
                        texts.append(item['text']['value'])
                    elif isinstance(item['text'], str):
                        texts.append(item['text'])
            return "\n\n".join(texts) if texts else ""
        
        # Handle direct dict with text
        if isinstance(content, dict) and 'text' in content:
            if isinstance(content['text'], dict) and 'value' in content['text']:
                return content['text']['value']
            return str(content['text'])
        
        # Handle string that might be JSON
        if isinstance(content, str):
            # Try to parse if it looks like JSON
            if content.strip().startswith('[{'):
                try:
                    parsed = ast.literal_eval(content)
                    return self._extract_content(parsed)
                except:
                    pass
            return content
        
        return str(content)

    def _save_review_report(self, report_content, code_files):
        """Save the review report to storage"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"code_review_report_{timestamp}.md"
        
        # Add metadata to the report
        full_report = f"""# Code Review Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Files Reviewed: {len(code_files)}

## Files Analyzed:
{chr(10).join(f"- {f}" for f in code_files.keys())}

---

{report_content}

---
*Generated by CodeReviewAgent using AgentTeam*
"""
        
        self.storage_manager.write_file(self.reports_folder, report_filename, full_report)
        return f"{self.reports_folder}/{report_filename}"