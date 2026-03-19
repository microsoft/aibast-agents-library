# Deployment Guide

Complete guide for deploying CommunityRAPP to production environments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
- [Azure Deployment](#azure-deployment)
- [Production Best Practices](#production-best-practices)
- [Scaling Strategies](#scaling-strategies)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [CI/CD Pipeline](#cicd-pipeline)

## Overview

This guide covers production deployment strategies for CommunityRAPP, including:
- Infrastructure provisioning
- Environment configuration
- Performance optimization
- Monitoring and maintenance

### Deployment Checklist

- [ ] Azure subscription with appropriate permissions
- [ ] Resource naming conventions defined
- [ ] Environment variables documented
- [ ] Security policies reviewed
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan documented

## Prerequisites

### Azure Requirements

**Subscriptions & Permissions:**
- Azure subscription (production)
- Contributor or Owner role
- Azure OpenAI Service quota approved
- Storage account creation permissions

**Services:**
- Azure Functions
- Azure OpenAI Service
- Azure Storage
- Application Insights
- Azure Key Vault (recommended)

### Development Requirements

**Local Tools:**
- Azure CLI (`az`)
- Azure Functions Core Tools v4
- Python 3.11
- Git

**Install Azure CLI:**
```bash
# Windows (PowerShell)
winget install Microsoft.AzureCLI

# Mac
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**Install Functions Core Tools:**
```bash
npm install -g azure-functions-core-tools@4
```

## Deployment Options

### Option 1: One-Click ARM Template (Recommended for New Deployments)

Deploy all resources with a single click:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fkody-w%2Frapp-installer%2Fmain%2Fazuredeploy.json)

**What Gets Deployed:**
- Function App (Consumption plan)
- Azure OpenAI Service
- Storage Account (3 file shares: agents, memory, multi_agents)
- Application Insights
- All configurations pre-set

### Option 2: Manual Azure Portal Deployment

Step-by-step manual deployment for customization.

### Option 3: Azure CLI Deployment

Automated deployment via command line.

### Option 4: Terraform/Bicep (Infrastructure as Code)

For enterprise environments requiring version control.

## Azure Deployment

### Step 1: Deploy Infrastructure

#### Using ARM Template

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="rg-copilot365-prod"
LOCATION="eastus"
PROJECT_NAME="copilot365-prod"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Deploy ARM template
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file azuredeploy.json \
  --parameters projectName=$PROJECT_NAME
```

#### Using Azure CLI (Manual)

**Create Resource Group:**
```bash
az group create \
  --name rg-copilot365-prod \
  --location eastus
```

**Create Storage Account:**
```bash
az storage account create \
  --name copilot365storage \
  --resource-group rg-copilot365-prod \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2
```

**Create File Shares:**
```bash
# Get connection string
CONNECTION_STRING=$(az storage account show-connection-string \
  --name copilot365storage \
  --resource-group rg-copilot365-prod \
  --output tsv)

# Create file shares
az storage share create --name agents --connection-string $CONNECTION_STRING
az storage share create --name memory --connection-string $CONNECTION_STRING
az storage share create --name multi_agents --connection-string $CONNECTION_STRING
```

**Create Application Insights:**
```bash
az monitor app-insights component create \
  --app copilot365-insights \
  --location eastus \
  --resource-group rg-copilot365-prod \
  --application-type web
```

**Create Function App:**
```bash
az functionapp create \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --storage-account copilot365storage \
  --app-insights copilot365-insights \
  --os-type Linux
```

**Create Azure OpenAI:**
```bash
az cognitiveservices account create \
  --name copilot365-openai \
  --resource-group rg-copilot365-prod \
  --location eastus \
  --kind OpenAI \
  --sku S0

# Deploy model
az cognitiveservices account deployment create \
  --name copilot365-openai \
  --resource-group rg-copilot365-prod \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-08-06" \
  --model-format OpenAI \
  --sku-capacity 50 \
  --sku-name Standard
```

### Step 2: Configure Application Settings

Get service keys and endpoints:

```bash
# Storage connection string
STORAGE_CONN=$(az storage account show-connection-string \
  --name copilot365storage \
  --resource-group rg-copilot365-prod \
  --output tsv)

# OpenAI key and endpoint
OPENAI_KEY=$(az cognitiveservices account keys list \
  --name copilot365-openai \
  --resource-group rg-copilot365-prod \
  --query key1 --output tsv)

OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name copilot365-openai \
  --resource-group rg-copilot365-prod \
  --query properties.endpoint --output tsv)

# Application Insights key
APP_INSIGHTS_KEY=$(az monitor app-insights component show \
  --app copilot365-insights \
  --resource-group rg-copilot365-prod \
  --query instrumentationKey --output tsv)
```

Configure Function App settings:

```bash
az functionapp config appsettings set \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --settings \
    "AzureWebJobsStorage=$STORAGE_CONN" \
    "AZURE_OPENAI_API_KEY=$OPENAI_KEY" \
    "AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT" \
    "AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o" \
    "AZURE_OPENAI_API_VERSION=2025-01-01-preview" \
    "APPINSIGHTS_INSTRUMENTATIONKEY=$APP_INSIGHTS_KEY" \
    "ASSISTANT_NAME=CommunityRAPP" \
    "CHARACTERISTIC_DESCRIPTION=Professional AI assistant with enterprise capabilities"
```

### Step 3: Deploy Function Code

```bash
# Navigate to project directory
cd CommunityRAPP

# Deploy to Azure
func azure functionapp publish copilot365-function-prod
```

### Step 4: Verify Deployment

```bash
# Test function endpoint
FUNCTION_URL="https://copilot365-function-prod.azurewebsites.net/api/businessinsightbot_function"
FUNCTION_KEY=$(az functionapp keys list \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --query functionKeys.default --output tsv)

curl -X POST "$FUNCTION_URL?code=$FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Hello", "conversation_history": []}'
```

## Production Best Practices

### 1. Use Premium or Dedicated Hosting Plan

For production workloads, upgrade from Consumption plan:

**Premium Plan Benefits:**
- Always-on instances (no cold start)
- VNet integration
- Unlimited execution duration
- More CPU and memory

```bash
# Create Premium plan
az functionapp plan create \
  --name copilot365-plan-premium \
  --resource-group rg-copilot365-prod \
  --location eastus \
  --sku EP1 \
  --is-linux

# Update function app to use Premium plan
az functionapp update \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --plan copilot365-plan-premium
```

### 2. Enable Managed Identity

Use managed identity instead of connection strings:

```bash
# Enable system-assigned identity
az functionapp identity assign \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod

# Get identity principal ID
PRINCIPAL_ID=$(az functionapp identity show \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --query principalId --output tsv)

# Grant Storage Blob Data Contributor role
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/rg-copilot365-prod/providers/Microsoft.Storage/storageAccounts/copilot365storage"
```

### 3. Use Azure Key Vault for Secrets

Store sensitive configuration in Key Vault:

```bash
# Create Key Vault
az keyvault create \
  --name copilot365-keyvault \
  --resource-group rg-copilot365-prod \
  --location eastus

# Add secrets
az keyvault secret set \
  --vault-name copilot365-keyvault \
  --name OpenAI-API-Key \
  --value $OPENAI_KEY

# Grant function app access
az keyvault set-policy \
  --name copilot365-keyvault \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list

# Update function app settings to reference Key Vault
az functionapp config appsettings set \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --settings \
    "AZURE_OPENAI_API_KEY=@Microsoft.KeyVault(SecretUri=https://copilot365-keyvault.vault.azure.net/secrets/OpenAI-API-Key/)"
```

### 4. Configure Custom Domain & SSL

```bash
# Add custom domain
az functionapp config hostname add \
  --webapp-name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --hostname copilot.yourcompany.com

# Bind SSL certificate (assumes certificate uploaded)
az functionapp config ssl bind \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --certificate-thumbprint YOUR_CERT_THUMBPRINT \
  --ssl-type SNI
```

### 5. Enable Application Insights Profiler

```bash
az monitor app-insights component update \
  --app copilot365-insights \
  --resource-group rg-copilot365-prod \
  --query-access Enabled
```

### 6. Set Up Deployment Slots

For blue-green deployments:

```bash
# Create staging slot
az functionapp deployment slot create \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --slot staging

# Deploy to staging
func azure functionapp publish copilot365-function-prod --slot staging

# Test staging slot
# https://copilot365-function-prod-staging.azurewebsites.net

# Swap to production
az functionapp deployment slot swap \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --slot staging
```

## Scaling Strategies

### Horizontal Scaling

**Consumption Plan:**
- Auto-scales up to 200 instances
- No configuration needed

**Premium/Dedicated Plan:**
```bash
# Set minimum and maximum instances
az functionapp plan update \
  --name copilot365-plan-premium \
  --resource-group rg-copilot365-prod \
  --min-instances 2 \
  --max-burst 10
```

### Vertical Scaling

**Upgrade Function App SKU:**
```bash
# Scale up to EP2 (more CPU/memory)
az functionapp plan update \
  --name copilot365-plan-premium \
  --resource-group rg-copilot365-prod \
  --sku EP2
```

### OpenAI Scaling

**Increase TPM (Tokens Per Minute) quota:**
1. Azure Portal → OpenAI Service → Quotas
2. Request quota increase
3. Update deployment capacity

```bash
az cognitiveservices account deployment update \
  --name copilot365-openai \
  --resource-group rg-copilot365-prod \
  --deployment-name gpt-4o \
  --sku-capacity 100
```

## Monitoring & Logging

### Application Insights Queries

**Request Volume:**
```kusto
requests
| where name == "businessinsightbot_function"
| summarize Count=count() by bin(timestamp, 5m)
| render timechart
```

**Error Rate:**
```kusto
requests
| where name == "businessinsightbot_function"
| summarize
    Total=count(),
    Errors=countif(success==false),
    ErrorRate=100.0*countif(success==false)/count()
    by bin(timestamp, 5m)
| render timechart
```

**Performance:**
```kusto
requests
| where name == "businessinsightbot_function"
| summarize
    AvgDuration=avg(duration),
    P50=percentile(duration, 50),
    P95=percentile(duration, 95),
    P99=percentile(duration, 99)
    by bin(timestamp, 1h)
| render timechart
```

### Alerts

**Create availability alert:**
```bash
az monitor metrics alert create \
  --name "Function App Down" \
  --resource-group rg-copilot365-prod \
  --scopes "/subscriptions/YOUR_SUB/resourceGroups/rg-copilot365-prod/providers/Microsoft.Web/sites/copilot365-function-prod" \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email YOUR_EMAIL@company.com
```

**Create error rate alert:**
```bash
az monitor metrics alert create \
  --name "High Error Rate" \
  --resource-group rg-copilot365-prod \
  --scopes "/subscriptions/YOUR_SUB/resourceGroups/rg-copilot365-prod/providers/Microsoft.Web/sites/copilot365-function-prod" \
  --condition "total Http5xx > 10" \
  --window-size 5m
```

## Backup & Recovery

### Backup Strategy

**1. Code & Configuration:**
- Store in Git repository
- Tag releases
- Document environment variables

**2. Memory/Data:**
```bash
# Backup Azure File Shares
az storage file download-batch \
  --destination ./backup \
  --source agents \
  --account-name copilot365storage

az storage file download-batch \
  --destination ./backup \
  --source memory \
  --account-name copilot365storage
```

**3. Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="./backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup file shares
az storage file download-batch \
  --destination "$BACKUP_DIR/agents" \
  --source agents \
  --account-name copilot365storage

az storage file download-batch \
  --destination "$BACKUP_DIR/memory" \
  --source memory \
  --account-name copilot365storage

echo "Backup completed: $BACKUP_DIR"
```

**Schedule with cron:**
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

### Disaster Recovery

**1. Export ARM Template:**
```bash
az group export \
  --name rg-copilot365-prod \
  --output json > infrastructure-backup.json
```

**2. Document Recovery Procedure:**
- Deploy infrastructure from ARM template
- Restore file shares from backup
- Deploy function code
- Update DNS/configuration
- Verify functionality

**Recovery Time Objective (RTO):** < 1 hour
**Recovery Point Objective (RPO):** < 24 hours

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure Functions

on:
  push:
    branches: [ main ]

env:
  AZURE_FUNCTIONAPP_NAME: copilot365-function-prod
  AZURE_FUNCTIONAPP_PACKAGE_PATH: '.'
  PYTHON_VERSION: '3.11'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: 'Checkout GitHub Action'
      uses: actions/checkout@v3

    - name: Setup Python ${{ env.PYTHON_VERSION }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: 'Install dependencies'
      shell: bash
      run: |
        pushd './${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}'
        python -m pip install --upgrade pip
        pip install -r requirements.txt --target=".python_packages/lib/site-packages"
        popd

    - name: 'Run tests'
      shell: bash
      run: |
        pip install pytest
        pytest tests/

    - name: 'Deploy to Azure Functions'
      uses: Azure/functions-action@v1
      with:
        app-name: ${{ env.AZURE_FUNCTIONAPP_NAME }}
        package: ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
        publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
        scm-do-build-during-deployment: true
        enable-oryx-build: true
```

**Get publish profile:**
```bash
az functionapp deployment list-publishing-profiles \
  --name copilot365-function-prod \
  --resource-group rg-copilot365-prod \
  --xml
```

Add to GitHub Secrets as `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`.

### Azure DevOps

Create `azure-pipelines.yml`:

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  azureSubscription: 'YOUR_SERVICE_CONNECTION'
  functionAppName: 'copilot365-function-prod'
  pythonVersion: '3.11'

stages:
- stage: Build
  jobs:
  - job: BuildJob
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'

    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt --target=".python_packages/lib/site-packages"
      displayName: 'Install dependencies'

    - script: |
        pip install pytest
        pytest tests/
      displayName: 'Run tests'

    - task: ArchiveFiles@2
      inputs:
        rootFolderOrFile: '$(System.DefaultWorkingDirectory)'
        includeRootFolder: false
        archiveType: 'zip'
        archiveFile: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'

    - publish: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
      artifact: drop

- stage: Deploy
  dependsOn: Build
  jobs:
  - job: DeployJob
    steps:
    - download: current
      artifact: drop

    - task: AzureFunctionApp@1
      inputs:
        azureSubscription: '$(azureSubscription)'
        appType: 'functionAppLinux'
        appName: '$(functionAppName)'
        package: '$(Pipeline.Workspace)/drop/*.zip'
        deploymentMethod: 'auto'
```

## Next Steps

- **[Security Guide](SECURITY.md)** - Secure your deployment
- **[Monitoring](TROUBLESHOOTING.md)** - Monitor and troubleshoot
- **[Scaling Guide](ARCHITECTURE.md)** - Performance optimization

---

**Need help?** [Open an issue](https://github.com/kody-w/CommunityRAPP/issues)
