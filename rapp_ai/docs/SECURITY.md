# Security Best Practices

Comprehensive security guide for deploying and maintaining CommunityRAPP.

## Table of Contents

- [Overview](#overview)
- [Authentication & Authorization](#authentication--authorization)
- [Data Protection](#data-protection)
- [Network Security](#network-security)
- [Secrets Management](#secrets-management)
- [Compliance & Governance](#compliance--governance)
- [Monitoring & Auditing](#monitoring--auditing)
- [Incident Response](#incident-response)
- [Security Checklist](#security-checklist)

## Overview

Security is built into every layer of CommunityRAPP. This guide covers:
- Secure configuration and deployment
- Data protection and encryption
- Access control and authentication
- Compliance with industry standards
- Monitoring and incident response

### Security Principles

1. **Defense in Depth** - Multiple layers of security controls
2. **Least Privilege** - Minimal access rights for users and services
3. **Zero Trust** - Never trust, always verify
4. **Encryption Everywhere** - Data encrypted in transit and at rest
5. **Audit Everything** - Comprehensive logging and monitoring

## Authentication & Authorization

### Function Key Management

**Best Practices:**

1. **Use Function-Level Keys** (not master key)
2. **Rotate Keys Regularly** (every 90 days)
3. **Separate Keys per Environment** (dev, test, prod)
4. **Never Commit Keys to Git**

**Rotate Function Keys:**

```bash
# Regenerate function key
az functionapp keys renew \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --key-type functionKeys \
  --key-name default

# Get new key
NEW_KEY=$(az functionapp keys list \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --query functionKeys.default --output tsv)

echo "New function key: $NEW_KEY"
```

**Store Keys Securely:**

```bash
# Option 1: Azure Key Vault
az keyvault secret set \
  --vault-name YOUR_KEYVAULT \
  --name FunctionKey-Prod \
  --value "$NEW_KEY"

# Option 2: GitHub Secrets (for CI/CD)
# GitHub → Repository → Settings → Secrets → New repository secret
```

### Azure AD Authentication

**Enable Azure AD for Function App:**

```bash
# Configure authentication
az webapp auth update \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --enabled true \
  --action LoginWithAzureActiveDirectory \
  --aad-client-id YOUR_AAD_APP_ID \
  --aad-client-secret YOUR_AAD_SECRET \
  --aad-allowed-token-audiences https://YOUR_FUNCTION_APP.azurewebsites.net
```

**Require authentication for all requests:**

```bash
az webapp auth update \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --unauthenticated-client-action RedirectToLoginPage
```

### Managed Identity

**Enable System-Assigned Managed Identity:**

```bash
# Enable managed identity
az functionapp identity assign \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP

# Get principal ID
PRINCIPAL_ID=$(az functionapp identity show \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --query principalId --output tsv)

echo "Principal ID: $PRINCIPAL_ID"
```

**Grant Permissions:**

```bash
# Storage Blob Data Contributor
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Contributor" \
  --scope /subscriptions/YOUR_SUB/resourceGroups/YOUR_RG/providers/Microsoft.Storage/storageAccounts/YOUR_STORAGE

# Cognitive Services OpenAI User
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Cognitive Services OpenAI User" \
  --scope /subscriptions/YOUR_SUB/resourceGroups/YOUR_RG/providers/Microsoft.CognitiveServices/accounts/YOUR_OPENAI
```

**Update Code to Use Managed Identity:**

```python
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient

# Use managed identity instead of connection string
credential = DefaultAzureCredential()
service_client = DataLakeServiceClient(
    account_url=f"https://{STORAGE_ACCOUNT}.dfs.core.windows.net",
    credential=credential
)
```

### Role-Based Access Control (RBAC)

**Define Custom Roles:**

Create `custom-role.json`:
```json
{
  "Name": "Copilot365 Developer",
  "Description": "Can manage Copilot365 function app and storage",
  "Actions": [
    "Microsoft.Web/sites/functions/read",
    "Microsoft.Web/sites/functions/write",
    "Microsoft.Storage/storageAccounts/fileServices/read",
    "Microsoft.Storage/storageAccounts/fileServices/write"
  ],
  "NotActions": [
    "Microsoft.Web/sites/delete",
    "Microsoft.Storage/storageAccounts/delete"
  ],
  "AssignableScopes": [
    "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/YOUR_RESOURCE_GROUP"
  ]
}
```

```bash
# Create custom role
az role definition create --role-definition custom-role.json

# Assign to user
az role assignment create \
  --assignee user@company.com \
  --role "Copilot365 Developer" \
  --scope /subscriptions/YOUR_SUB/resourceGroups/YOUR_RG
```

## Data Protection

### Encryption at Rest

**Azure Storage Encryption:**
- Enabled by default (256-bit AES)
- Microsoft-managed keys (default)
- Customer-managed keys (optional)

**Enable Customer-Managed Keys:**

```bash
# Create Key Vault
az keyvault create \
  --name copilot365-keyvault \
  --resource-group YOUR_RESOURCE_GROUP \
  --location eastus

# Create encryption key
az keyvault key create \
  --vault-name copilot365-keyvault \
  --name storage-encryption-key \
  --protection software

# Update storage account
az storage account update \
  --name YOUR_STORAGE \
  --resource-group YOUR_RESOURCE_GROUP \
  --encryption-key-source Microsoft.Keyvault \
  --encryption-key-vault https://copilot365-keyvault.vault.azure.net \
  --encryption-key-name storage-encryption-key
```

### Encryption in Transit

**Enforce HTTPS:**

```bash
# Function App - enforce HTTPS
az functionapp update \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --set httpsOnly=true

# Storage Account - enforce HTTPS
az storage account update \
  --name YOUR_STORAGE \
  --resource-group YOUR_RESOURCE_GROUP \
  --https-only true

# Require TLS 1.2 minimum
az storage account update \
  --name YOUR_STORAGE \
  --resource-group YOUR_RESOURCE_GROUP \
  --min-tls-version TLS1_2
```

### Data Sanitization

**Input Validation:**

```python
import re
from html import escape

def sanitize_user_input(user_input: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        user_input: Raw user input

    Returns:
        Sanitized input
    """
    # Remove potential script tags
    user_input = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', user_input, flags=re.IGNORECASE)

    # Escape HTML
    user_input = escape(user_input)

    # Limit length
    max_length = 10000
    if len(user_input) > max_length:
        user_input = user_input[:max_length]

    return user_input
```

**Output Sanitization:**

```python
def sanitize_agent_output(output: str) -> str:
    """
    Sanitize agent output before returning to user.

    Args:
        output: Raw agent output

    Returns:
        Sanitized output
    """
    # Remove any API keys or secrets (simple pattern matching)
    patterns = [
        r'api[_-]?key["\']?\s*[:=]\s*["\']?[\w-]+',
        r'password["\']?\s*[:=]\s*["\']?[\w-]+',
        r'secret["\']?\s*[:=]\s*["\']?[\w-]+',
    ]

    for pattern in patterns:
        output = re.sub(pattern, '[REDACTED]', output, flags=re.IGNORECASE)

    return output
```

### Personally Identifiable Information (PII)

**Detect and Mask PII:**

```python
import re

def mask_pii(text: str) -> str:
    """
    Mask PII in text before logging or storing.

    Args:
        text: Input text potentially containing PII

    Returns:
        Text with PII masked
    """
    # Email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

    # Phone numbers (US format)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)

    # Social Security Numbers
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)

    # Credit card numbers (simple pattern)
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CREDIT_CARD]', text)

    return text


# Use in logging
import logging

class PIIMaskingFilter(logging.Filter):
    def filter(self, record):
        record.msg = mask_pii(str(record.msg))
        return True

# Add filter to logger
logger = logging.getLogger()
logger.addFilter(PIIMaskingFilter())
```

## Network Security

### IP Restrictions

**Restrict Function App Access:**

```bash
# Allow only specific IP ranges
az functionapp config access-restriction add \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --rule-name AllowCorporateNetwork \
  --priority 100 \
  --ip-address 203.0.113.0/24

# Allow Power Platform (regional IPs)
az functionapp config access-restriction add \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --rule-name AllowPowerPlatform \
  --priority 200 \
  --service-tag AzureCloud.eastus

# Deny all others (implicit)
```

**Get current restrictions:**
```bash
az functionapp config access-restriction show \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP
```

### Virtual Network Integration

**Enable VNet Integration:**

```bash
# Create VNet
az network vnet create \
  --name copilot365-vnet \
  --resource-group YOUR_RESOURCE_GROUP \
  --location eastus \
  --address-prefix 10.0.0.0/16

# Create subnet for function app
az network vnet subnet create \
  --name function-subnet \
  --vnet-name copilot365-vnet \
  --resource-group YOUR_RESOURCE_GROUP \
  --address-prefixes 10.0.1.0/24 \
  --delegations Microsoft.Web/serverFarms

# Enable VNet integration
az functionapp vnet-integration add \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --vnet copilot365-vnet \
  --subnet function-subnet
```

### Private Endpoints

**Create Private Endpoint for Storage:**

```bash
# Create subnet for private endpoint
az network vnet subnet create \
  --name private-endpoint-subnet \
  --vnet-name copilot365-vnet \
  --resource-group YOUR_RESOURCE_GROUP \
  --address-prefixes 10.0.2.0/24

# Create private endpoint
az network private-endpoint create \
  --name storage-private-endpoint \
  --resource-group YOUR_RESOURCE_GROUP \
  --vnet-name copilot365-vnet \
  --subnet private-endpoint-subnet \
  --private-connection-resource-id /subscriptions/YOUR_SUB/resourceGroups/YOUR_RG/providers/Microsoft.Storage/storageAccounts/YOUR_STORAGE \
  --group-id file \
  --connection-name storage-connection

# Disable public network access
az storage account update \
  --name YOUR_STORAGE \
  --resource-group YOUR_RESOURCE_GROUP \
  --public-network-access Disabled
```

### Web Application Firewall (WAF)

**Deploy Azure Front Door with WAF:**

```bash
# Create Front Door profile
az afd profile create \
  --profile-name copilot365-frontdoor \
  --resource-group YOUR_RESOURCE_GROUP \
  --sku Premium_AzureFrontDoor

# Create WAF policy
az network front-door waf-policy create \
  --name copilot365waf \
  --resource-group YOUR_RESOURCE_GROUP \
  --sku Premium_AzureFrontDoor \
  --mode Prevention

# Enable managed rules
az network front-door waf-policy managed-rules add \
  --policy-name copilot365waf \
  --resource-group YOUR_RESOURCE_GROUP \
  --type Microsoft_DefaultRuleSet \
  --version 2.1
```

## Secrets Management

### Azure Key Vault Integration

**Create Key Vault:**

```bash
az keyvault create \
  --name copilot365-keyvault \
  --resource-group YOUR_RESOURCE_GROUP \
  --location eastus \
  --enable-rbac-authorization false
```

**Store Secrets:**

```bash
# OpenAI API Key
az keyvault secret set \
  --vault-name copilot365-keyvault \
  --name OpenAI-API-Key \
  --value "YOUR_OPENAI_API_KEY"

# Storage connection string
az keyvault secret set \
  --vault-name copilot365-keyvault \
  --name Storage-Connection-String \
  --value "YOUR_STORAGE_CONNECTION_STRING"

# Function key
az keyvault secret set \
  --vault-name copilot365-keyvault \
  --name Function-Key-Prod \
  --value "YOUR_FUNCTION_KEY"
```

**Grant Function App Access:**

```bash
# Get function app identity
PRINCIPAL_ID=$(az functionapp identity show \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --query principalId --output tsv)

# Grant secret read permissions
az keyvault set-policy \
  --name copilot365-keyvault \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

**Reference in Function App:**

```bash
az functionapp config appsettings set \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --settings \
    "AZURE_OPENAI_API_KEY=@Microsoft.KeyVault(SecretUri=https://copilot365-keyvault.vault.azure.net/secrets/OpenAI-API-Key/)" \
    "AzureWebJobsStorage=@Microsoft.KeyVault(SecretUri=https://copilot365-keyvault.vault.azure.net/secrets/Storage-Connection-String/)"
```

### Secret Rotation

**Automate Key Rotation:**

Create an Azure Function to rotate keys automatically:

```python
import azure.functions as func
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def rotate_function_key(timer: func.TimerRequest):
    """
    Rotate function keys every 90 days.
    Schedule: 0 0 0 1 */3 * (first day of every 3 months)
    """
    # Generate new function key
    new_key = generate_secure_key()

    # Update in Key Vault
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://copilot365-keyvault.vault.azure.net", credential=credential)

    client.set_secret("Function-Key-Prod", new_key)

    # Notify administrators
    send_notification(f"Function key rotated successfully at {datetime.now()}")
```

## Compliance & Governance

### Data Residency

**Select Appropriate Region:**

```bash
# Deploy in specific region for compliance
az group create \
  --name rg-copilot365-eu \
  --location westeurope

# All resources will be in EU region
az functionapp create \
  --name copilot365-function-eu \
  --resource-group rg-copilot365-eu \
  --consumption-plan-location westeurope \
  ...
```

### Data Retention Policies

**Configure Storage Lifecycle:**

Create `lifecycle-policy.json`:
```json
{
  "rules": [
    {
      "enabled": true,
      "name": "DeleteOldLogs",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "delete": {
              "daysAfterModificationGreaterThan": 90
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["logs/"]
        }
      }
    },
    {
      "enabled": true,
      "name": "ArchiveOldMemory",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToCool": {
              "daysAfterModificationGreaterThan": 30
            },
            "tierToArchive": {
              "daysAfterModificationGreaterThan": 180
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["memory/"]
        }
      }
    }
  ]
}
```

```bash
az storage account management-policy create \
  --account-name YOUR_STORAGE \
  --resource-group YOUR_RESOURCE_GROUP \
  --policy @lifecycle-policy.json
```

### Audit Logging

**Enable Diagnostic Settings:**

```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --workspace-name copilot365-logs \
  --resource-group YOUR_RESOURCE_GROUP \
  --location eastus

# Get workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --workspace-name copilot365-logs \
  --resource-group YOUR_RESOURCE_GROUP \
  --query id --output tsv)

# Enable diagnostic settings for Function App
az monitor diagnostic-settings create \
  --name FunctionAppLogs \
  --resource /subscriptions/YOUR_SUB/resourceGroups/YOUR_RG/providers/Microsoft.Web/sites/YOUR_FUNCTION_APP \
  --workspace $WORKSPACE_ID \
  --logs '[{"category":"FunctionAppLogs","enabled":true}]' \
  --metrics '[{"category":"AllMetrics","enabled":true}]'

# Enable diagnostic settings for Storage
az monitor diagnostic-settings create \
  --name StorageLogs \
  --resource /subscriptions/YOUR_SUB/resourceGroups/YOUR_RG/providers/Microsoft.Storage/storageAccounts/YOUR_STORAGE \
  --workspace $WORKSPACE_ID \
  --logs '[{"category":"StorageRead","enabled":true},{"category":"StorageWrite","enabled":true}]'
```

## Monitoring & Auditing

### Security Monitoring

**Query for suspicious activity:**

```kusto
// Failed authentication attempts
AzureDiagnostics
| where Category == "FunctionAppLogs"
| where resultCode >= 400
| summarize FailedAttempts=count() by clientIP, bin(TimeGenerated, 5m)
| where FailedAttempts > 10
| order by FailedAttempts desc

// Unusual data access patterns
StorageFileLogs
| where OperationName == "GetFile"
| summarize FilesAccessed=dcount(Uri) by CallerIpAddress, bin(TimeGenerated, 1h)
| where FilesAccessed > 100
| order by FilesAccessed desc

// OpenAI API errors
traces
| where message contains "OpenAI"
| where severityLevel >= 3
| summarize ErrorCount=count() by message, bin(timestamp, 5m)
| order by ErrorCount desc
```

### Alerts

**Create security alerts:**

```bash
# Alert on failed authentication
az monitor metrics alert create \
  --name "High Failed Authentication Rate" \
  --resource-group YOUR_RESOURCE_GROUP \
  --scopes /subscriptions/YOUR_SUB/resourceGroups/YOUR_RG/providers/Microsoft.Web/sites/YOUR_FUNCTION_APP \
  --condition "total Http4xx > 50" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email YOUR_SECURITY_TEAM@company.com

# Alert on unusual activity
az monitor metrics alert create \
  --name "Unusual Request Volume" \
  --resource-group YOUR_RESOURCE_GROUP \
  --scopes /subscriptions/YOUR_SUB/resourceGroups/YOUR_RG/providers/Microsoft.Web/sites/YOUR_FUNCTION_APP \
  --condition "total Requests > 1000" \
  --window-size 5m
```

## Incident Response

### Security Incident Playbook

**1. Detection:**
- Monitor alerts from Application Insights
- Review audit logs regularly
- Investigate anomalies

**2. Containment:**
```bash
# Immediately disable function app if compromised
az functionapp stop \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP

# Revoke all function keys
az functionapp keys delete \
  --name YOUR_FUNCTION_APP \
  --resource-group YOUR_RESOURCE_GROUP \
  --key-type functionKeys \
  --key-name default

# Disable storage account public access
az storage account update \
  --name YOUR_STORAGE \
  --resource-group YOUR_RESOURCE_GROUP \
  --public-network-access Disabled
```

**3. Investigation:**
```bash
# Export audit logs
az monitor activity-log list \
  --resource-group YOUR_RESOURCE_GROUP \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-31T23:59:59Z \
  --output json > incident-logs.json

# Review access logs
az storage account show-connection-string \
  --name YOUR_STORAGE \
  --resource-group YOUR_RESOURCE_GROUP
```

**4. Recovery:**
```bash
# Restore from backup
az storage file download-batch \
  --source agents \
  --destination ./restore \
  --account-name YOUR_STORAGE_BACKUP

# Redeploy with new keys
func azure functionapp publish YOUR_FUNCTION_APP

# Update all keys
./scripts/rotate-all-keys.sh
```

**5. Post-Incident:**
- Document incident timeline
- Identify root cause
- Implement preventive measures
- Update security policies

## Security Checklist

### Deployment Checklist

- [ ] Azure AD authentication enabled
- [ ] Function keys rotated and stored in Key Vault
- [ ] HTTPS enforced on all endpoints
- [ ] TLS 1.2+ required
- [ ] IP restrictions configured
- [ ] Managed identity enabled
- [ ] RBAC roles assigned (least privilege)
- [ ] Private endpoints configured (if required)
- [ ] Diagnostic logging enabled
- [ ] Security alerts configured
- [ ] Data encryption at rest verified
- [ ] Backup strategy implemented
- [ ] Incident response plan documented

### Regular Security Tasks

**Weekly:**
- [ ] Review Application Insights for errors
- [ ] Check for failed authentication attempts
- [ ] Monitor unusual activity patterns

**Monthly:**
- [ ] Review access control lists
- [ ] Audit user permissions
- [ ] Check for outdated dependencies
- [ ] Review security alerts

**Quarterly:**
- [ ] Rotate function keys
- [ ] Rotate storage account keys
- [ ] Review and update security policies
- [ ] Conduct security training
- [ ] Penetration testing (if required)

**Annually:**
- [ ] Full security audit
- [ ] Disaster recovery drill
- [ ] Compliance certification renewal
- [ ] Review and update incident response plan

## Next Steps

- **[Deployment Guide](DEPLOYMENT.md)** - Deploy securely
- **[Monitoring Guide](TROUBLESHOOTING.md)** - Monitor your deployment
- **[Architecture Overview](ARCHITECTURE.md)** - Understand the system

---

**Security concerns?** [Report a security issue](https://github.com/kody-w/CommunityRAPP/security)
