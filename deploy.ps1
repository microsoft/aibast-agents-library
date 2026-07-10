# RAPP Azure Deployment Script for Windows
# Deploy Azure resources needed for RAPP
#
# Usage:
#   irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/deploy.ps1 | iex
#   Or: .\deploy.ps1 [-ResourceGroup "rapp-rg"] [-Location "eastus2"] [-OpenAILocation "eastus2"]

param(
    [string]$ResourceGroup = "",
    [string]$Location = "",
    [string]$OpenAILocation = ""
)

$ErrorActionPreference = "Stop"

$TemplateUrl = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/azuredeploy.json"

# Available OpenAI regions
$OpenAIRegions = @(
    "australiaeast", "canadaeast", "eastus", "eastus2", "francecentral",
    "japaneast", "northcentralus", "norwayeast", "southcentralus",
    "swedencentral", "switzerlandnorth", "uksouth", "westeurope", "westus", "westus3"
)

function Select-OpenAIRegion {
    param([string]$Current)

    Write-Host ""
    Write-Host "Available Azure OpenAI regions:" -ForegroundColor Yellow
    Write-Host "  1) australiaeast     6) japaneast        11) swedencentral"
    Write-Host "  2) canadaeast        7) northcentralus   12) switzerlandnorth"
    Write-Host "  3) eastus            8) norwayeast       13) uksouth"
    Write-Host "  4) eastus2           9) southcentralus   14) westeurope"
    Write-Host "  5) francecentral    10) swedencentral    15) westus"
    Write-Host "                                           16) westus3"
    Write-Host ""

    if ($Current) {
        Write-Host "  Current selection: $Current" -ForegroundColor Cyan
        Write-Host ""
    }

    $selection = Read-Host "Enter region name or number [eastus2]"
    if (-not $selection) { $selection = "eastus2" }

    # Map number to region name
    $regionMap = @{
        "1" = "australiaeast"
        "2" = "canadaeast"
        "3" = "eastus"
        "4" = "eastus2"
        "5" = "francecentral"
        "6" = "japaneast"
        "7" = "northcentralus"
        "8" = "norwayeast"
        "9" = "southcentralus"
        "10" = "swedencentral"
        "11" = "swedencentral"
        "12" = "switzerlandnorth"
        "13" = "uksouth"
        "14" = "westeurope"
        "15" = "westus"
        "16" = "westus3"
    }

    if ($regionMap.ContainsKey($selection)) {
        return $regionMap[$selection]
    }
    return $selection
}

Write-Host ""
Write-Host "RAPP Azure Deployment" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

# Check Azure CLI
try {
    $null = az --version 2>&1
} catch {
    Write-Host "Error: Azure CLI not found" -ForegroundColor Red
    Write-Host "Install from: https://aka.ms/installazurecli"
    exit 1
}

# Check Azure login
try {
    $account = az account show 2>&1 | ConvertFrom-Json
    if (-not $account) { throw "Not logged in" }
    Write-Host "Logged in to: $($account.name)" -ForegroundColor Green
} catch {
    Write-Host "Not logged into Azure. Running 'az login'..." -ForegroundColor Yellow
    az login
    $account = az account show | ConvertFrom-Json
    Write-Host "Logged in to: $($account.name)" -ForegroundColor Green
}

Write-Host ""

# Get parameters
if (-not $ResourceGroup) {
    $ResourceGroup = Read-Host "Resource group name [rapp-rg]"
    if (-not $ResourceGroup) { $ResourceGroup = "rapp-rg" }
}

if (-not $Location) {
    $Location = Read-Host "Azure region [eastus2]"
    if (-not $Location) { $Location = "eastus2" }
}

if (-not $OpenAILocation) {
    $OpenAILocation = Select-OpenAIRegion -Current ""
}

Write-Host ""
Write-Host "Deployment Configuration:" -ForegroundColor Yellow
Write-Host "  Resource Group:  $ResourceGroup"
Write-Host "  Location:        $Location"
Write-Host "  OpenAI Location: $OpenAILocation"
Write-Host ""

$confirm = Read-Host "Proceed with deployment? (y/n) [y]"
if (-not $confirm) { $confirm = "y" }

if ($confirm -notin @("y", "Y")) {
    Write-Host "Deployment cancelled."
    exit 0
}

# Create resource group
Write-Host ""
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location --output none
Write-Host "Resource group created" -ForegroundColor Green

# Deploy ARM template with retry loop for OpenAI region
$deploymentSuccess = $false
$maxRetries = 5
$retryCount = 0
$deploymentOutput = $null

while (-not $deploymentSuccess -and $retryCount -lt $maxRetries) {
    Write-Host ""
    Write-Host "Deploying Azure resources (this may take 5-10 minutes)..." -ForegroundColor Yellow
    Write-Host "  - Function App (Flex Consumption)"
    Write-Host "  - Storage Account"
    Write-Host "  - Azure OpenAI Service (region: $OpenAILocation)"
    Write-Host "  - Application Insights"
    Write-Host ""

    try {
        $deploymentOutput = az deployment group create `
            --resource-group $ResourceGroup `
            --template-uri $TemplateUrl `
            --parameters openAILocation=$OpenAILocation `
            --query "properties.outputs" `
            --output json 2>&1

        # Check if output is valid JSON (success)
        $null = $deploymentOutput | ConvertFrom-Json
        $deploymentSuccess = $true
    } catch {
        $retryCount++
        Write-Host ""
        Write-Host "Deployment failed!" -ForegroundColor Red

        $errorMessage = $deploymentOutput -join "`n"

        # Check if it's a quota/capacity error
        if ($errorMessage -match "quota|capacity|InsufficientQuota|sku.*not available|not available in") {
            Write-Host "This appears to be a quota or capacity issue for region: $OpenAILocation" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Error details:"
            $errorMessage | Select-String -Pattern "message|error" | Select-Object -First 5 | ForEach-Object { Write-Host $_.Line }
            Write-Host ""

            if ($retryCount -lt $maxRetries) {
                $retry = Read-Host "Would you like to try a different OpenAI region? (y/n) [y]"
                if (-not $retry) { $retry = "y" }

                if ($retry -in @("y", "Y")) {
                    $OpenAILocation = Select-OpenAIRegion -Current $OpenAILocation
                    Write-Host ""
                    Write-Host "Retrying with region: $OpenAILocation" -ForegroundColor Cyan
                } else {
                    Write-Host "Deployment cancelled."
                    exit 1
                }
            }
        } else {
            # Not a quota error, show full error and exit
            Write-Host "Error details:"
            Write-Host $errorMessage
            exit 1
        }
    }
}

if (-not $deploymentSuccess) {
    Write-Host "Deployment failed after $maxRetries attempts." -ForegroundColor Red
    Write-Host "Please check your Azure subscription quotas or try again later."
    exit 1
}

$deploymentOutput = $deploymentOutput | ConvertFrom-Json

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host ""

# Extract outputs
$functionAppName = $deploymentOutput.functionAppName.value
$functionUrl = $deploymentOutput.functionEndpoint.value
$storageAccount = $deploymentOutput.storageAccountName.value
$openAIEndpoint = $deploymentOutput.openAIEndpoint.value

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  RAPP Azure Resources Deployed!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Resource Group:    $ResourceGroup"
Write-Host "  Function App:      $functionAppName"
Write-Host "  Storage Account:   $storageAccount"
Write-Host "  OpenAI Endpoint:   $openAIEndpoint"
Write-Host "  OpenAI Region:     $OpenAILocation"
Write-Host ""
Write-Host "  Function URL:"
Write-Host "  $functionUrl"
Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Install RAPP:"
Write-Host "     irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1 | iex"
Write-Host ""
Write-Host "  2. Run setup and select 'existing' to connect:"
Write-Host "     rapp setup"
Write-Host ""
Write-Host "  3. Or deploy code to your Function App:"
Write-Host "     func azure functionapp publish $functionAppName --build remote"
Write-Host ""

# Save outputs to file
$outputFile = "rapp-deployment-outputs.json"
$deploymentOutput | ConvertTo-Json -Depth 10 | Set-Content -Path $outputFile
Write-Host "Full deployment outputs saved to: $outputFile"
