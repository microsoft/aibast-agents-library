"""
Azure File Storage Manager with Flexible Authentication

This module provides Azure File Storage access with support for both:
1. Identity-based authentication (Managed Identity / Azure CLI) - Recommended
2. Key-based authentication (Connection strings) - Legacy

Feature Flag: USE_IDENTITY_BASED_STORAGE
- When 'true': Uses Managed Identity (Azure) or Azure CLI (local dev)
- When 'false' or unset: Uses connection string/account key if available

Authentication Priority (Identity-based mode):
1. App Registration (if AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET set)
2. ChainedTokenCredential:
   - ManagedIdentityCredential (for Azure deployments - Function App, VM, etc.)
   - AzureCliCredential (for local development - requires 'az login')

Authentication (Key-based mode):
- Uses AZURE_STORAGE_CONNECTION_STRING or constructs from account name/key

Environment Variables Required:
- AZURE_STORAGE_ACCOUNT_NAME: Storage account name
- AZURE_FILES_SHARE_NAME: File share name
- USE_IDENTITY_BASED_STORAGE: Set to 'true' to use Managed Identity

For Identity-Based Local Development:
1. Run 'az login' to authenticate with Azure CLI
2. Ensure your user account has 'Storage File Data Privileged Contributor' role
   on the storage account

For Azure Deployment (Identity-based):
- The Function App's managed identity must have 'Storage File Data Privileged Contributor' role
- Set USE_IDENTITY_BASED_STORAGE=true in app settings
"""

import json
import os
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any, List

from azure.identity import (
    ChainedTokenCredential,
    ManagedIdentityCredential,
    AzureCliCredential,
    ClientSecretCredential
)
from azure.storage.fileshare import ShareServiceClient, ShareFileClient, ShareDirectoryClient
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError, AzureError

from utils.environment import use_identity_based_storage


def safe_json_loads(json_str):
    """
    Safely loads JSON string, handling potential errors.
    """
    if not json_str:
        return {}
    try:
        if isinstance(json_str, (dict, list)):
            return json_str
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON: {json_str}"}


class AzureFileStorageManager:
    """
    Azure File Storage Manager with Entra ID authentication.

    Supports Managed Identity for Azure deployments and App Registration
    or Azure CLI for local development.
    """

    # Intentionally invalid default GUID - contains non-hex chars to prevent DB insertion
    # See function_app.py DEFAULT_USER_GUID for full design rationale
    DEFAULT_MARKER_GUID = "c0p110t0-aaaa-bbbb-cccc-123456789abc"

    def __init__(self):
        """
        Initialize the storage manager with Entra ID authentication.
        """
        # Get required configuration
        self.account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
        if not self.account_name:
            raise ValueError("AZURE_STORAGE_ACCOUNT_NAME environment variable is required")
        
        self.share_name = os.environ.get('AZURE_FILES_SHARE_NAME')
        if not self.share_name:
            raise ValueError("AZURE_FILES_SHARE_NAME environment variable is required")
        
        # Memory context settings
        self.shared_memory_path = "shared_memories"
        self.default_file_name = 'memory.json'
        self.current_guid = None
        self.current_memory_path = self.shared_memory_path
        
        # Initialize authentication
        self._init_auth()
        
        # Ensure share and directories exist
        self._ensure_share_exists()
    
    def _init_auth(self):
        """
        Initialize authentication for Azure Files.

        Supports two modes based on USE_IDENTITY_BASED_STORAGE feature flag:
        
        Identity-based mode (USE_IDENTITY_BASED_STORAGE=true):
        - Uses Managed Identity (Azure) or Azure CLI (local dev)
        - Required when storage account has allowSharedKeyAccess=false
        - Priority: App Registration -> ManagedIdentity -> AzureCli
        
        Key-based mode (USE_IDENTITY_BASED_STORAGE=false or unset):
        - Uses connection string or account key
        - Traditional authentication method
        """
        self.use_identity = use_identity_based_storage()
        
        if self.use_identity:
            self._init_identity_auth()
        else:
            self._init_key_auth()
    
    def _init_identity_auth(self):
        """
        Initialize identity-based (Managed Identity / Azure CLI) authentication.
        
        Priority:
        1. App Registration (if AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET set)
        2. ChainedTokenCredential (ManagedIdentity -> AzureCli)
        """
        # Try App Registration credentials first (explicit service principal)
        tenant_id = os.environ.get('AZURE_TENANT_ID')
        client_id = os.environ.get('AZURE_CLIENT_ID')
        client_secret = os.environ.get('AZURE_CLIENT_SECRET')

        if tenant_id and client_id and client_secret:
            logging.info("Using App Registration (Client Secret) credentials for storage")
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        else:
            # Use ChainedTokenCredential - much faster and more predictable than DefaultAzureCredential
            # Order: ManagedIdentity first (Azure), then AzureCli (local dev with 'az login')
            logging.info("Using ChainedTokenCredential (ManagedIdentity -> AzureCli) for storage")
            self.credential = ChainedTokenCredential(
                ManagedIdentityCredential(),  # Works in Azure (Function App, VM, etc.)
                AzureCliCredential()          # Works locally after 'az login'
            )

        # Initialize File Share client with token credential
        # token_intent="backup" is REQUIRED for token auth - bypasses file/directory ACLs
        account_url = f"https://{self.account_name}.file.core.windows.net"
        self.share_service = ShareServiceClient(
            account_url=account_url,
            credential=self.credential,
            token_intent="backup"
        )
        self.share_client = self.share_service.get_share_client(self.share_name)

        # Initialize Blob client (for URL generation with User Delegation SAS)
        blob_url = f"https://{self.account_name}.blob.core.windows.net"
        self.blob_service = BlobServiceClient(
            account_url=blob_url,
            credential=self.credential
        )

        logging.info(f"Initialized IDENTITY-BASED auth for storage account: {self.account_name}")
    
    def _init_key_auth(self):
        """
        Initialize key-based (connection string) authentication.
        
        Uses connection string from environment or constructs from account name/key.
        This is the legacy authentication method.
        """
        # Try connection string first
        connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        
        if not connection_string:
            # Try to construct from account name and key
            account_key = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
            if account_key:
                connection_string = (
                    f"DefaultEndpointsProtocol=https;"
                    f"AccountName={self.account_name};"
                    f"AccountKey={account_key};"
                    f"EndpointSuffix=core.windows.net"
                )
                logging.info("Constructed connection string from account name and key")
        
        if not connection_string:
            # Fall back to identity-based if no key available
            logging.warning("No connection string or account key found, falling back to identity-based auth")
            self._init_identity_auth()
            return

        # Initialize File Share client with connection string
        self.share_service = ShareServiceClient.from_connection_string(connection_string)
        self.share_client = self.share_service.get_share_client(self.share_name)

        # Initialize Blob client with connection string
        self.blob_service = BlobServiceClient.from_connection_string(connection_string)
        
        # Store credential as None for key-based auth (used in SAS generation check)
        self.credential = None

        logging.info(f"Initialized KEY-BASED auth for storage account: {self.account_name}")

    def refresh_credentials(self):
        """
        Refresh authentication credentials.

        Call this method if you encounter authentication errors to get fresh tokens.
        This reinitializes the credential chain and recreates all service clients.
        """
        logging.info("Refreshing Azure Storage credentials")
        self._init_auth()
        logging.info("Azure Storage credentials refreshed successfully")

    def _ensure_share_exists(self):
        """
        Ensure the file share and default directories exist.

        Optimized to check existence before attempting creation to avoid
        redundant 409 ResourceAlreadyExists responses.
        """
        try:
            # Check if share exists first (cheaper than trying to create)
            try:
                self.share_client.get_share_properties()
                logging.debug(f"File share exists: {self.share_name}")
            except ResourceNotFoundError:
                # Only try to create if it doesn't exist
                self.share_client.create_share()
                logging.info(f"Created file share: {self.share_name}")

            # Check if default memory file exists - this also verifies the directory structure
            file_path = f"{self.shared_memory_path}/{self.default_file_name}"
            try:
                file_client = self.share_client.get_file_client(file_path)
                file_client.get_file_properties()
                logging.debug(f"Default memory file exists: {file_path}")
                # If file exists, directories must exist - skip redundant creation
                return
            except ResourceNotFoundError:
                # Need to create directories and file
                pass

            # Only create directories if the memory file didn't exist
            self.ensure_directory_exists(self.shared_memory_path)

            # Ensure all required directories exist (agents, multi_agents, demos, agent_config)
            required_directories = ['agents', 'multi_agents', 'demos', 'agent_config']
            for directory in required_directories:
                self.ensure_directory_exists(directory)

            # Create default memory file
            file_client = self.share_client.get_file_client(file_path)
            file_client.upload_file(b'{}')
            logging.info(f"Created new {self.default_file_name} in shared memories directory")

        except AzureError as e:
            # Check for auth errors - these are expected in local dev without proper RBAC
            error_str = str(e)
            if "AuthorizationFailure" in error_str or "AuthenticationFailed" in error_str:
                logging.warning(f"Azure Storage auth failed (expected in local dev without RBAC): {e.error_code if hasattr(e, 'error_code') else 'AuthError'}")
            else:
                logging.error(f"Error ensuring share exists: {error_str}")
            raise
        except Exception as e:
            logging.error(f"Error ensuring share exists: {str(e)}")
            raise

    def set_memory_context(self, guid: Optional[str] = None) -> bool:
        """
        Set the memory context - only create new directories if valid GUID is provided.

        Args:
            guid: Optional GUID for user-specific memory

        Returns:
            bool: True if context was set successfully
        """
        if not guid:
            self.current_guid = None
            self.current_memory_path = self.shared_memory_path
            return True

        # Check for intentionally invalid default marker GUID
        # This GUID contains non-hex chars by design to prevent DB insertion
        # It signals "anonymous/unauthenticated session" - use shared memory silently
        if guid == self.DEFAULT_MARKER_GUID:
            logging.debug(f"Default marker GUID detected - using shared memory (this is expected)")
            self.current_guid = None
            self.current_memory_path = self.shared_memory_path
            return True  # Return True - this is intentional, not a failure

        # Validate GUID format
        guid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        if not guid_pattern.match(guid):
            logging.warning(f"Invalid GUID format: {guid}. Using shared memory.")
            self.current_guid = None
            self.current_memory_path = self.shared_memory_path
            return False
        
        try:
            guid_dir = f"memory/{guid}"
            guid_file = "user_memory.json"
            file_path = f"{guid_dir}/{guid_file}"
            
            try:
                file_client = self.share_client.get_file_client(file_path)
                file_client.get_file_properties()
                # File exists
                self.current_guid = guid
                self.current_memory_path = guid_dir
                return True
            except ResourceNotFoundError:
                # Create new GUID directory and file
                self.ensure_directory_exists(guid_dir)
                file_client = self.share_client.get_file_client(file_path)
                file_client.upload_file(b'{}')
                logging.info(f"Created new memory file for GUID: {guid}")
                self.current_guid = guid
                self.current_memory_path = guid_dir
                return True
            
        except Exception as e:
            logging.error(f"Error setting memory context for GUID {guid}: {str(e)}")
            self.current_guid = None
            self.current_memory_path = self.shared_memory_path
            return False

    def read_json(self) -> dict:
        """Read from either GUID-specific memory or shared memories."""
        if self.current_guid and self.current_memory_path != self.shared_memory_path:
            try:
                return self._read_guid_memory()
            except Exception:
                # Fall back to shared memory on any error
                self.current_guid = None
                self.current_memory_path = self.shared_memory_path
                return self._read_shared_memory()
        else:
            return self._read_shared_memory()

    def _read_shared_memory(self) -> dict:
        """Read from shared memory location."""
        try:
            file_path = f"{self.shared_memory_path}/{self.default_file_name}"
            file_client = self.share_client.get_file_client(file_path)
            download = file_client.download_file()
            content = download.readall().decode('utf-8')
            return safe_json_loads(content)
        except ResourceNotFoundError:
            logging.warning("Shared memory file not found, recreating...")
            self._ensure_share_exists()
            return {}
        except Exception as e:
            logging.error(f"Error reading from shared memory: {str(e)}")
            return {}

    def _read_guid_memory(self) -> dict:
        """Read from GUID-specific memory location."""
        try:
            file_path = f"{self.current_memory_path}/user_memory.json"
            file_client = self.share_client.get_file_client(file_path)
            download = file_client.download_file()
            content = download.readall().decode('utf-8')
            return safe_json_loads(content)
        except Exception as e:
            logging.error(f"Error reading from GUID memory: {str(e)}")
            raise  # Let read_json handle the fallback

    def write_json(self, data: dict):
        """Write to either GUID-specific memory or shared memories."""
        if self.current_guid and self.current_memory_path != self.shared_memory_path:
            try:
                self._write_guid_memory(data)
            except Exception:
                # Fall back to shared memory on any error
                self.current_guid = None
                self.current_memory_path = self.shared_memory_path
                self._write_shared_memory(data)
        else:
            self._write_shared_memory(data)

    def _write_shared_memory(self, data: dict):
        """Write to shared memory location."""
        try:
            json_content = json.dumps(data, indent=4)
            file_path = f"{self.shared_memory_path}/{self.default_file_name}"
            file_client = self.share_client.get_file_client(file_path)
            file_client.upload_file(json_content.encode('utf-8'))
        except ResourceNotFoundError:
            logging.warning("Shared memory path not found, recreating...")
            self._ensure_share_exists()
            self._write_shared_memory(data)
        except Exception as e:
            logging.error(f"Error writing to shared memory: {str(e)}")
            raise

    def _write_guid_memory(self, data: dict):
        """Write to GUID-specific memory location."""
        try:
            json_content = json.dumps(data, indent=4)
            file_path = f"{self.current_memory_path}/user_memory.json"
            file_client = self.share_client.get_file_client(file_path)
            file_client.upload_file(json_content.encode('utf-8'))
        except Exception as e:
            logging.error(f"Error writing to GUID memory: {str(e)}")
            raise  # Let write_json handle the fallback

    def ensure_directory_exists(self, directory_name: str) -> bool:
        """
        Creates directories that are explicitly needed.
        
        Args:
            directory_name: Path of directory to create (can be nested like "a/b/c")
            
        Returns:
            bool: True if successful
        """
        try:
            if not directory_name:
                return False
            
            parts = directory_name.split('/')
            current_path = ""
            
            for part in parts:
                if part:
                    current_path = f"{current_path}/{part}" if current_path else part
                    try:
                        dir_client = self.share_client.get_directory_client(current_path)
                        dir_client.create_directory()
                        logging.debug(f"Created directory: {current_path}")
                    except ResourceExistsError:
                        logging.debug(f"Directory already exists: {current_path}")
                    except AzureError as e:
                        if "ResourceAlreadyExists" not in str(e):
                            raise
            return True
        except Exception as e:
            logging.error(f"Error ensuring directory exists: {str(e)}")
            return False

    def write_file(self, directory_name: str, file_name: str, content: Union[str, bytes, Any]) -> bool:
        """
        Writes a file to Azure File Storage, properly handling binary data.
        
        Args:
            directory_name: The directory to write to
            file_name: The name of the file
            content: The content to write (can be str, bytes, or BytesIO)
            
        Returns:
            bool: Success or failure
        """
        try:
            self.ensure_directory_exists(directory_name)
            
            file_path = f"{directory_name}/{file_name}"
            file_client = self.share_client.get_file_client(file_path)
            
            # Convert content to bytes
            if isinstance(content, (bytes, bytearray)):
                binary_content = content
            elif hasattr(content, 'read') and callable(content.read):
                # File-like object (like BytesIO)
                content.seek(0)
                binary_content = content.read()
                if not isinstance(binary_content, (bytes, bytearray)):
                    binary_content = str(binary_content).encode('utf-8')
            else:
                # String or other - encode to bytes
                binary_content = str(content).encode('utf-8')
            
            file_client.upload_file(binary_content)
            logging.debug(f"Wrote file: {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error writing file: {str(e)}")
            return False

    def read_file(self, directory_name: str, file_name: str) -> Optional[Union[str, bytes]]:
        """
        Reads a file from Azure File Storage.
        
        For text files, returns the content as a string.
        For binary files, returns bytes.
        
        Args:
            directory_name: The directory to read from
            file_name: The name of the file
            
        Returns:
            str, bytes, or None if an error occurs
        """
        try:
            # For known binary file types, return as bytes
            binary_extensions = ('.pptx', '.docx', '.xlsx', '.pdf', '.zip', '.jpg', '.png', '.gif', '.jpeg', '.webp')
            if file_name.lower().endswith(binary_extensions):
                return self.read_file_binary(directory_name, file_name)
            
            # Otherwise try to get as text
            file_path = f"{directory_name}/{file_name}"
            file_client = self.share_client.get_file_client(file_path)
            download = file_client.download_file()
            content = download.readall()
            
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                # Binary file, return as bytes
                return content
                
        except ResourceNotFoundError:
            logging.warning(f"File not found: {directory_name}/{file_name}")
            return None
        except Exception as e:
            logging.error(f"Error reading file: {str(e)}")
            return None
            
    def read_file_binary(self, directory_name: str, file_name: str) -> Optional[bytes]:
        """
        Reads a file from Azure File Storage as binary data.
        
        Args:
            directory_name: The directory to read from
            file_name: The name of the file
            
        Returns:
            bytes or None if an error occurs
        """
        try:
            file_path = f"{directory_name}/{file_name}"
            file_client = self.share_client.get_file_client(file_path)
            download = file_client.download_file()
            return download.readall()
        except ResourceNotFoundError:
            logging.warning(f"Binary file not found: {directory_name}/{file_name}")
            return None
        except Exception as e:
            logging.error(f"Error reading binary file: {str(e)}")
            return None

    def list_files(self, directory_name: str, auto_create: bool = True) -> List:
        """
        List files and directories in a directory.

        Args:
            directory_name: The directory to list
            auto_create: If True, auto-create the directory if it doesn't exist (default: True)

        Returns:
            List of file/directory objects with 'name' attribute
        """
        try:
            dir_client = self.share_client.get_directory_client(directory_name)
            items = list(dir_client.list_directories_and_files())
            return items
        except ResourceNotFoundError:
            if auto_create:
                logging.info(f"Directory not found, creating: {directory_name}")
                if self.ensure_directory_exists(directory_name):
                    logging.info(f"Created directory: {directory_name}")
                    return []  # Directory now exists but is empty
            logging.warning(f"Directory not found: {directory_name}")
            return []
        except Exception as e:
            logging.error(f"Error listing files: {str(e)}")
            return []
            
    def generate_download_url(self, directory: str, filename: str, expiry_minutes: int = 30) -> Optional[str]:
        """
        Generates a temporary download URL using User Delegation SAS.
        
        This method uses Entra ID to get a user delegation key, then generates
        a SAS token that can be shared with others for temporary access.
        
        Args:
            directory: The directory containing the file
            filename: The filename to download
            expiry_minutes: How long the URL should be valid (default 30 minutes)
            
        Returns:
            str: The download URL with SAS token, or None if failed
        """
        try:
            # Build the file path
            if directory.endswith('/'):
                file_path = f"{directory}{filename}"
            else:
                file_path = f"{directory}/{filename}"
            
            # For File Share, we need to generate a file-level SAS
            file_client = self.share_client.get_file_client(file_path)
            
            # Get file properties to ensure it exists
            file_client.get_file_properties()
            
            # Generate SAS token using user delegation
            start_time = datetime.utcnow()
            expiry_time = start_time + timedelta(minutes=expiry_minutes)
            
            # For Azure Files with Entra ID, we use generate_file_sas from the share
            from azure.storage.fileshare import generate_file_sas, FileSasPermissions
            
            # Get user delegation key from blob service (works for file share too)
            delegation_key = self.blob_service.get_user_delegation_key(
                key_start_time=start_time,
                key_expiry_time=expiry_time + timedelta(hours=1)  # Key valid longer than SAS
            )
            
            # Parse directory and file name
            directory_path = '/'.join(file_path.split('/')[:-1])
            file_name_only = file_path.split('/')[-1]
            
            sas_token = generate_file_sas(
                account_name=self.account_name,
                share_name=self.share_name,
                directory_name=directory_path,
                file_name=file_name_only,
                user_delegation_key=delegation_key,
                permission=FileSasPermissions(read=True),
                expiry=expiry_time,
                start=start_time
            )
            
            # Create the full URL with SAS token
            file_url = f"https://{self.account_name}.file.core.windows.net/{self.share_name}/{file_path}"
            download_url = f"{file_url}?{sas_token}"
            
            logging.info(f"Generated download URL for: {file_path}")
            return download_url
            
        except Exception as e:
            logging.error(f"Error generating download URL: {str(e)}")
            logging.error(f"Directory: {directory}, Filename: {filename}")
            
            # Fallback: return direct URL (requires authentication)
            try:
                if directory.endswith('/'):
                    file_path = f"{directory}{filename}"
                else:
                    file_path = f"{directory}/{filename}"
                direct_url = f"https://{self.account_name}.file.core.windows.net/{self.share_name}/{file_path}"
                logging.warning(f"Returning direct URL (requires auth): {direct_url}")
                return direct_url
            except:
                return None

    def delete_file(self, directory_name: str, file_name: str) -> bool:
        """
        Delete a file from Azure File Storage.
        
        Args:
            directory_name: The directory containing the file
            file_name: The name of the file to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            file_path = f"{directory_name}/{file_name}"
            file_client = self.share_client.get_file_client(file_path)
            file_client.delete_file()
            logging.info(f"Deleted file: {file_path}")
            return True
        except ResourceNotFoundError:
            logging.warning(f"File not found for deletion: {directory_name}/{file_name}")
            return False
        except Exception as e:
            logging.error(f"Error deleting file: {str(e)}")
            return False

    def file_exists(self, directory_name: str, file_name: str) -> bool:
        """
        Check if a file exists in Azure File Storage.
        
        Args:
            directory_name: The directory to check
            file_name: The name of the file
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            file_path = f"{directory_name}/{file_name}"
            file_client = self.share_client.get_file_client(file_path)
            file_client.get_file_properties()
            return True
        except ResourceNotFoundError:
            return False
        except Exception as e:
            logging.error(f"Error checking file existence: {str(e)}")
            return False

    def get_file_properties(self, directory_name: str, file_name: str) -> Optional[dict]:
        """
        Get properties of a file in Azure File Storage.
        
        Args:
            directory_name: The directory containing the file
            file_name: The name of the file
            
        Returns:
            dict with file properties or None if not found
        """
        try:
            file_path = f"{directory_name}/{file_name}"
            file_client = self.share_client.get_file_client(file_path)
            props = file_client.get_file_properties()
            return {
                'name': file_name,
                'size': props.size,
                'content_type': props.content_settings.content_type if props.content_settings else None,
                'last_modified': props.last_modified,
                'etag': props.etag
            }
        except ResourceNotFoundError:
            return None
        except Exception as e:
            logging.error(f"Error getting file properties: {str(e)}")
            return None
