"""
Storage Factory

Provides a factory function to get the appropriate storage manager
based on the environment (Azure vs Local).

Uses singleton pattern with TTL to avoid expensive re-initialization of Azure credentials
and redundant directory creation attempts on each request, while ensuring credentials
stay fresh (don't expire after overnight idle).
"""

import logging
import time
from typing import Union, Optional

from utils.environment import should_use_azure_storage, is_running_in_azure
from utils.local_file_storage import LocalFileStorageManager

# Singleton instance cache - avoids expensive re-initialization per request
_storage_manager_instance: Optional[Union['AzureFileStorageManager', LocalFileStorageManager]] = None

# Track when the singleton was created to implement TTL refresh
_storage_manager_created_at: Optional[float] = None

# TTL for credential refresh - 30 minutes (Managed Identity tokens typically last 1 hour)
# Refreshing at 30 min ensures we always have valid tokens with margin
CREDENTIAL_TTL_SECONDS = 30 * 60


def _is_credential_expired() -> bool:
    """Check if the cached storage manager credentials have exceeded TTL."""
    global _storage_manager_created_at

    if _storage_manager_created_at is None:
        return True

    elapsed = time.time() - _storage_manager_created_at
    if elapsed >= CREDENTIAL_TTL_SECONDS:
        logging.info(f"Storage manager TTL expired ({elapsed:.0f}s >= {CREDENTIAL_TTL_SECONDS}s) - refreshing credentials")
        return True

    return False


def get_storage_manager() -> Union['AzureFileStorageManager', LocalFileStorageManager]:
    """
    Get the appropriate storage manager based on environment.

    Uses singleton pattern with TTL - returns cached instance if available and fresh.
    Automatically refreshes credentials every 30 minutes to prevent token expiration
    issues after overnight idle periods.

    Returns:
        AzureFileStorageManager if in Azure or fully configured for local dev,
        LocalFileStorageManager as fallback for local development.
    """
    global _storage_manager_instance, _storage_manager_created_at

    # Return cached instance if available AND credentials not expired
    if _storage_manager_instance is not None:
        # For Azure storage, check TTL to ensure credentials are fresh
        if isinstance(_storage_manager_instance, LocalFileStorageManager):
            # Local storage doesn't need credential refresh
            return _storage_manager_instance

        if not _is_credential_expired():
            return _storage_manager_instance

        # TTL expired - reset and create new instance with fresh credentials
        logging.info("Refreshing Azure storage credentials due to TTL expiration")
        _storage_manager_instance = None
        _storage_manager_created_at = None

    if should_use_azure_storage():
        try:
            # Import here to avoid issues if Azure SDK not available
            from utils.azure_file_storage import AzureFileStorageManager

            logging.info("Using Azure File Storage")
            _storage_manager_instance = AzureFileStorageManager()
            _storage_manager_created_at = time.time()
            return _storage_manager_instance

        except Exception as e:
            # If running in Azure, this is a critical error
            if is_running_in_azure():
                logging.error("CRITICAL: Azure storage failed in Azure environment!")
                raise

            # For local development, fall back gracefully with concise message
            error_str = str(e)
            if "AuthorizationFailure" in error_str or "AuthenticationFailed" in error_str:
                logging.info("Azure Storage requires RBAC role - using local storage (this is fine for dev)")
            else:
                logging.warning(f"Azure Storage unavailable: {error_str[:100]}...")

            logging.info("Using local file storage at .local_storage/")
            _storage_manager_instance = LocalFileStorageManager()
            return _storage_manager_instance
    else:
        logging.info("Using local file storage for development")
        _storage_manager_instance = LocalFileStorageManager()
        return _storage_manager_instance


def create_storage_manager_safe() -> Union['AzureFileStorageManager', LocalFileStorageManager, None]:
    """
    Safely create a storage manager, returning None if all methods fail.

    Use this when storage is truly optional (e.g., for caching).
    Uses singleton pattern - same instance returned on subsequent calls.

    Returns:
        Storage manager instance or None if initialization fails
    """
    try:
        return get_storage_manager()
    except Exception as e:
        logging.error(f"Failed to create any storage manager: {str(e)}")
        return None


def reset_storage_manager() -> None:
    """
    Reset the singleton storage manager instance.

    Useful for testing or when you need to force re-initialization
    (e.g., after changing environment variables or credential refresh).
    """
    global _storage_manager_instance, _storage_manager_created_at
    _storage_manager_instance = None
    _storage_manager_created_at = None
    logging.debug("Storage manager singleton reset")
