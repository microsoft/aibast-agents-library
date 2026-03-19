"""
Environment Detection Utilities

Provides functions to detect the runtime environment (Azure vs Local)
and adjust behavior accordingly for optimal development experience.

Feature Flags:
- USE_IDENTITY_BASED_STORAGE: When 'true', uses Managed Identity for Azure Storage access.
  When 'false' or unset, uses connection string/key-based access.
"""

import os
import logging


def use_identity_based_storage() -> bool:
    """
    Determine if identity-based (Managed Identity) storage access should be used.
    
    This is a feature flag to toggle between:
    - Identity-based: Uses Managed Identity or Azure CLI credentials (more secure)
    - Key-based: Uses connection strings with account keys (legacy)
    
    Set USE_IDENTITY_BASED_STORAGE=true in app settings to enable identity-based access.
    This is required when the storage account has allowSharedKeyAccess=false.
    
    Returns:
        bool: True if identity-based storage should be used, False for key-based
    """
    use_identity = os.environ.get('USE_IDENTITY_BASED_STORAGE', '').lower() in ('true', '1', 'yes')
    
    if use_identity:
        logging.info("USE_IDENTITY_BASED_STORAGE=true - using Managed Identity for storage")
    else:
        logging.debug("USE_IDENTITY_BASED_STORAGE not set - using key-based storage (if available)")
    
    return use_identity


def is_running_in_azure() -> bool:
    """
    Detect if the code is running in Azure (Functions or App Service).

    Azure environments set specific environment variables that we can check:
    - WEBSITE_INSTANCE_ID: Set ONLY by Azure App Service and Azure Functions in cloud
    - WEBSITE_SITE_NAME: Azure App Service site name (cloud only)

    Note: FUNCTIONS_WORKER_RUNTIME is NOT a reliable indicator because it's also
    set by local.settings.json during local development.

    Returns:
        bool: True if running in Azure, False if running locally
    """
    # These are only set in actual Azure cloud deployments, not local dev
    azure_cloud_indicators = [
        'WEBSITE_INSTANCE_ID',      # Azure cloud only
        'WEBSITE_SITE_NAME',        # Azure cloud only
        'APPSETTING_WEBSITE_SITE_NAME'  # Azure cloud only
    ]

    for indicator in azure_cloud_indicators:
        if os.environ.get(indicator):
            logging.info(f"Detected Azure environment via {indicator}")
            return True

    logging.info("Detected local development environment")
    return False


def should_use_azure_storage() -> bool:
    """
    Determine if Azure File Storage should be used.

    Returns True if:
    1. USE_CLOUD_STORAGE=true is set (force cloud storage), OR
    2. Running in Azure environment, OR
    3. Storage account and share name are configured (with az login for auth)

    Returns:
        bool: True if Azure storage should be used, False for local fallback
    """
    # Check for explicit override to force cloud storage
    force_cloud = os.environ.get('USE_CLOUD_STORAGE', '').lower() in ('true', '1', 'yes')
    if force_cloud:
        logging.info("USE_CLOUD_STORAGE=true - forcing Azure storage")
        return True

    # Always use Azure storage when running in Azure
    if is_running_in_azure():
        return True

    # For local development, use Azure storage if account and share are configured
    # (authentication will use az login via AzureCliCredential)
    storage_account = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
    share_name = os.environ.get('AZURE_FILES_SHARE_NAME')

    if storage_account and share_name:
        logging.info("Azure storage configured - using cloud storage (auth via az login)")
        return True

    logging.info("Azure storage not configured - using local fallback")
    return False


def get_local_storage_path() -> str:
    """
    Get the path for local file storage fallback.

    Creates the directory if it doesn't exist.

    Returns:
        str: Absolute path to local storage directory
    """
    # Use .local_storage in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_storage = os.path.join(project_root, '.local_storage')

    # Create directory if it doesn't exist
    os.makedirs(local_storage, exist_ok=True)

    return local_storage
