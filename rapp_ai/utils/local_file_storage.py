"""
Local File Storage Manager

Provides a local file system fallback that implements the same interface
as AzureFileStorageManager for seamless local development.
"""

import json
import os
import logging
import re
from typing import Optional, Union, Any, List
from datetime import datetime


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


class LocalFileItem:
    """Mock object to match Azure File Storage list_files return type"""
    def __init__(self, name: str, is_directory: bool = False):
        self.name = name
        self.is_directory = is_directory


class LocalFileStorageManager:
    """
    Local file system storage manager that mirrors AzureFileStorageManager interface.

    Uses local filesystem under .local_storage/ directory for development.
    """

    # Intentionally invalid default GUID - contains non-hex chars to prevent DB insertion
    # See function_app.py DEFAULT_USER_GUID for full design rationale
    DEFAULT_MARKER_GUID = "c0p110t0-aaaa-bbbb-cccc-123456789abc"

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the local storage manager.

        Args:
            base_path: Optional custom base path. Defaults to .local_storage in project root.
        """
        if base_path:
            self.base_path = base_path
        else:
            # Use .local_storage in project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.base_path = os.path.join(project_root, '.local_storage')

        # Create base directory
        os.makedirs(self.base_path, exist_ok=True)
        logging.info(f"Initialized local storage at: {self.base_path}")

        # Memory context settings (matching Azure implementation)
        self.shared_memory_path = "shared_memories"
        self.default_file_name = 'memory.json'
        self.current_guid = None
        self.current_memory_path = self.shared_memory_path

        # Ensure default directories and files exist
        self._ensure_defaults()

    def _ensure_defaults(self):
        """Ensure default directories and files exist."""
        try:
            # Create shared memories directory
            shared_dir = os.path.join(self.base_path, self.shared_memory_path)
            os.makedirs(shared_dir, exist_ok=True)

            # Create default memory file if it doesn't exist
            default_memory = os.path.join(shared_dir, self.default_file_name)
            if not os.path.exists(default_memory):
                with open(default_memory, 'w') as f:
                    json.dump({}, f)
                logging.info(f"Created default memory file: {default_memory}")

        except Exception as e:
            logging.error(f"Error ensuring defaults: {str(e)}")

    def _get_full_path(self, directory_name: str, file_name: str = None) -> str:
        """Get full filesystem path."""
        if file_name:
            return os.path.join(self.base_path, directory_name, file_name)
        return os.path.join(self.base_path, directory_name)

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
            file_path = self._get_full_path(guid_dir, guid_file)

            if os.path.exists(file_path):
                # File exists
                self.current_guid = guid
                self.current_memory_path = guid_dir
                return True
            else:
                # Create new GUID directory and file
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    json.dump({}, f)
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
            file_path = self._get_full_path(self.shared_memory_path, self.default_file_name)
            with open(file_path, 'r') as f:
                content = f.read()
            return safe_json_loads(content)
        except FileNotFoundError:
            logging.warning("Shared memory file not found, recreating...")
            self._ensure_defaults()
            return {}
        except Exception as e:
            logging.error(f"Error reading from shared memory: {str(e)}")
            return {}

    def _read_guid_memory(self) -> dict:
        """Read from GUID-specific memory location."""
        try:
            file_path = self._get_full_path(self.current_memory_path, "user_memory.json")
            with open(file_path, 'r') as f:
                content = f.read()
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
            file_path = self._get_full_path(self.shared_memory_path, self.default_file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logging.error(f"Error writing to shared memory: {str(e)}")
            raise

    def _write_guid_memory(self, data: dict):
        """Write to GUID-specific memory location."""
        try:
            file_path = self._get_full_path(self.current_memory_path, "user_memory.json")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
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

            full_path = self._get_full_path(directory_name)
            os.makedirs(full_path, exist_ok=True)
            logging.debug(f"Ensured directory exists: {full_path}")
            return True
        except Exception as e:
            logging.error(f"Error ensuring directory exists: {str(e)}")
            return False

    def write_file(self, directory_name: str, file_name: str, content: Union[str, bytes, Any]) -> bool:
        """
        Writes a file to local storage, properly handling binary data.

        Args:
            directory_name: The directory to write to
            file_name: The name of the file
            content: The content to write (can be str, bytes, or BytesIO)

        Returns:
            bool: Success or failure
        """
        try:
            file_path = self._get_full_path(directory_name, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Convert content to bytes
            if isinstance(content, (bytes, bytearray)):
                binary_content = content
                mode = 'wb'
            elif hasattr(content, 'read') and callable(content.read):
                # File-like object (like BytesIO)
                content.seek(0)
                binary_content = content.read()
                if isinstance(binary_content, (bytes, bytearray)):
                    mode = 'wb'
                else:
                    binary_content = str(binary_content)
                    mode = 'w'
            else:
                # String or other - write as text
                binary_content = str(content)
                mode = 'w'

            with open(file_path, mode) as f:
                f.write(binary_content)

            logging.debug(f"Wrote file: {file_path}")
            return True

        except Exception as e:
            logging.error(f"Error writing file: {str(e)}")
            return False

    def read_file(self, directory_name: str, file_name: str) -> Optional[Union[str, bytes]]:
        """
        Reads a file from local storage.

        For text files, returns the content as a string.
        For binary files, returns bytes.

        Args:
            directory_name: The directory to read from
            file_name: The name of the file

        Returns:
            str, bytes, or None if an error occurs
        """
        try:
            file_path = self._get_full_path(directory_name, file_name)

            # For known binary file types, return as bytes
            binary_extensions = ('.pptx', '.docx', '.xlsx', '.pdf', '.zip', '.jpg', '.png', '.gif', '.jpeg', '.webp')
            if file_name.lower().endswith(binary_extensions):
                return self.read_file_binary(directory_name, file_name)

            # Otherwise try to get as text
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        except UnicodeDecodeError:
            # Binary file, return as bytes
            return self.read_file_binary(directory_name, file_name)
        except FileNotFoundError:
            logging.warning(f"File not found: {directory_name}/{file_name}")
            return None
        except Exception as e:
            logging.error(f"Error reading file: {str(e)}")
            return None

    def read_file_binary(self, directory_name: str, file_name: str) -> Optional[bytes]:
        """
        Reads a file from local storage as binary data.

        Args:
            directory_name: The directory to read from
            file_name: The name of the file

        Returns:
            bytes or None if an error occurs
        """
        try:
            file_path = self._get_full_path(directory_name, file_name)
            with open(file_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            logging.warning(f"Binary file not found: {directory_name}/{file_name}")
            return None
        except Exception as e:
            logging.error(f"Error reading binary file: {str(e)}")
            return None

    def list_files(self, directory_name: str, auto_create: bool = True) -> List[LocalFileItem]:
        """
        List files and directories in a directory.

        Args:
            directory_name: The directory to list
            auto_create: If True, auto-create the directory if it doesn't exist (default: True)

        Returns:
            List of LocalFileItem objects with 'name' and 'is_directory' attributes
        """
        try:
            dir_path = self._get_full_path(directory_name)
            if not os.path.exists(dir_path):
                if auto_create:
                    logging.info(f"Directory not found, creating: {directory_name}")
                    os.makedirs(dir_path, exist_ok=True)
                    return []
                else:
                    logging.warning(f"Directory not found: {directory_name}")
                    return []

            items = []
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                is_dir = os.path.isdir(item_path)
                items.append(LocalFileItem(item, is_directory=is_dir))
            return items

        except Exception as e:
            logging.error(f"Error listing files: {str(e)}")
            return []

    def generate_download_url(self, directory: str, filename: str, expiry_minutes: int = 30) -> Optional[str]:
        """
        Generate a download URL (for local, just returns file path).

        Args:
            directory: The directory containing the file
            filename: The filename to download
            expiry_minutes: Ignored for local storage

        Returns:
            str: File path or None if not found
        """
        try:
            file_path = self._get_full_path(directory, filename)
            if os.path.exists(file_path):
                return f"file://{file_path}"
            return None
        except Exception as e:
            logging.error(f"Error generating download URL: {str(e)}")
            return None

    def delete_file(self, directory_name: str, file_name: str) -> bool:
        """
        Delete a file from local storage.

        Args:
            directory_name: The directory containing the file
            file_name: The name of the file to delete

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            file_path = self._get_full_path(directory_name, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Deleted file: {file_path}")
                return True
            else:
                logging.warning(f"File not found for deletion: {directory_name}/{file_name}")
                return False
        except Exception as e:
            logging.error(f"Error deleting file: {str(e)}")
            return False

    def file_exists(self, directory_name: str, file_name: str) -> bool:
        """
        Check if a file exists in local storage.

        Args:
            directory_name: The directory to check
            file_name: The name of the file

        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            file_path = self._get_full_path(directory_name, file_name)
            return os.path.exists(file_path)
        except Exception as e:
            logging.error(f"Error checking file existence: {str(e)}")
            return False

    def get_file_properties(self, directory_name: str, file_name: str) -> Optional[dict]:
        """
        Get properties of a file in local storage.

        Args:
            directory_name: The directory containing the file
            file_name: The name of the file

        Returns:
            dict with file properties or None if not found
        """
        try:
            file_path = self._get_full_path(directory_name, file_name)
            if not os.path.exists(file_path):
                return None

            stat = os.stat(file_path)
            return {
                'name': file_name,
                'size': stat.st_size,
                'content_type': None,  # Would need mimetypes module for this
                'last_modified': datetime.fromtimestamp(stat.st_mtime),
                'etag': None  # Not applicable for local files
            }
        except Exception as e:
            logging.error(f"Error getting file properties: {str(e)}")
            return None
