# CommunityRAPP — One-line installer for Windows (Hippocampus / Tier 2)
# Usage: irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/community_rapp/install.ps1 | iex
#
# Creates a ready-to-run CommunityRAPP project with persistent memory,
# auto-discovered agents, and GitHub Copilot device-code auth through the UI.
# No API keys, no Azure account, no cloud services needed to start.

$ErrorActionPreference = "Stop"
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RAPP Hippocampus - Local Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ── Helpers ─────────────────────────────────────────────────

function Find-Python {
    foreach ($cmd in @("python3.11", "python3.12", "python311", "python312")) {
        $fullPath = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($fullPath) {
            $ver = & $fullPath.Source --version 2>&1
            if ($ver -match "Python 3\.(11|12)") { return $fullPath.Source }
        }
    }
    # Try py launcher
    try {
        $ver = & py -3.11 --version 2>&1
        if ($ver -match "Python 3\.11") { return "py -3.11" }
    } catch {}
    try {
        $ver = & py -3.12 --version 2>&1
        if ($ver -match "Python 3\.12") { return "py -3.12" }
    } catch {}
    # Check standard install locations
    foreach ($p in @(
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python312\python.exe"
    )) {
        if (Test-Path $p) {
            $ver = & $p --version 2>&1
            if ($ver -match "Python 3\.(11|12)") { return $p }
        }
    }
    return $null
}

# ── Prerequisites ───────────────────────────────────────────
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    winget install Git.Git --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}
Write-Host "[OK] Git" -ForegroundColor Green

# Python
$PYTHON_CMD = Find-Python
if (-not $PYTHON_CMD) {
    Write-Host "Installing Python 3.11..." -ForegroundColor Yellow
    winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Start-Sleep -Seconds 3
    $PYTHON_CMD = Find-Python
    if (-not $PYTHON_CMD) {
        Write-Host "[X] Python 3.11+ required (3.13+ not supported). Install from https://python.org" -ForegroundColor Red
        exit 1
    }
}
$pyVer = if ($PYTHON_CMD -match "^py ") { & py $PYTHON_CMD.Substring(3) --version 2>&1 } else { & $PYTHON_CMD --version 2>&1 }
Write-Host "[OK] $pyVer" -ForegroundColor Green

# Azure Functions Core Tools
if (-not (Get-Command func -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Azure Functions Core Tools..." -ForegroundColor Yellow
    winget install Microsoft.Azure.FunctionsCoreTools --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}
Write-Host "[OK] Azure Functions Core Tools" -ForegroundColor Green

# ── Project name ────────────────────────────────────────────

$ProjectName = $args[0]
if (-not $ProjectName) {
    Write-Host ""
    $ProjectName = Read-Host "Project name (e.g. my-project)"
    if (-not $ProjectName) { Write-Host "[X] Project name is required." -ForegroundColor Red; exit 1 }
}

if ($ProjectName -notmatch '^[a-z0-9][a-z0-9-]*$') {
    Write-Host "[X] Invalid name '$ProjectName'. Use lowercase letters, numbers, and hyphens." -ForegroundColor Red
    exit 1
}

$ProjectsDir = if ($env:RAPP_PROJECTS_DIR) { $env:RAPP_PROJECTS_DIR } else { Join-Path $HOME "rapp-projects" }
$ProjectDir = Join-Path $ProjectsDir $ProjectName

if (Test-Path $ProjectDir) {
    Write-Host "[X] Project '$ProjectName' already exists at $ProjectDir" -ForegroundColor Red
    exit 1
}

# ── Clone ───────────────────────────────────────────────────
Write-Host ""
Write-Host "Creating project '$ProjectName'..." -ForegroundColor Yellow

if (-not (Test-Path $ProjectsDir)) { New-Item -ItemType Directory -Path $ProjectsDir -Force | Out-Null }

Write-Host "Cloning CommunityRAPP..." -ForegroundColor Yellow
git clone --depth 1 --quiet https://github.com/kody-w/CommunityRAPP.git $ProjectDir
Write-Host "[OK] Cloned" -ForegroundColor Green

# ── Venv + deps ─────────────────────────────────────────────
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if ($PYTHON_CMD -match "^py ") {
    & py $PYTHON_CMD.Substring(3) -m venv "$ProjectDir\.venv"
} else {
    & $PYTHON_CMD -m venv "$ProjectDir\.venv"
}

Write-Host "Installing dependencies..." -ForegroundColor Yellow
& "$ProjectDir\.venv\Scripts\pip.exe" install -r "$ProjectDir\requirements.txt" --quiet 2>$null
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# ── Settings ────────────────────────────────────────────────
$template = Join-Path $ProjectDir "local.settings.template.json"
$settings = Join-Path $ProjectDir "local.settings.json"
if (Test-Path $template) { Copy-Item $template $settings }

# ── Port + start script ────────────────────────────────────
$Port = 7072
$Manifest = Join-Path $ProjectsDir ".hatchery.json"

if (Test-Path $Manifest) {
    try {
        $data = Get-Content $Manifest -Raw | ConvertFrom-Json
        $maxPort = ($data.projects.PSObject.Properties | ForEach-Object { $_.Value.port } | Sort-Object | Select-Object -Last 1)
        if ($maxPort -ge $Port) { $Port = $maxPort + 1 }
    } catch {}
}

$startSh = @"
#!/usr/bin/env bash
cd "`$(dirname "`$0")"
source .venv/bin/activate
func start --port $Port
"@
[System.IO.File]::WriteAllText("$ProjectDir\start.sh", $startSh, $Utf8NoBom)

$startPs1 = @"
`$ErrorActionPreference = 'Stop'
Set-Location `$PSScriptRoot
.venv\Scripts\Activate.ps1
func start --port $Port
"@
[System.IO.File]::WriteAllText("$ProjectDir\start.ps1", $startPs1, $Utf8NoBom)

# Inject port into chat UI
$indexHtml = Join-Path $ProjectDir "index.html"
if (Test-Path $indexHtml) {
    $content = Get-Content $indexHtml -Raw
    $content = $content -replace '</head>', "<script>window.__RAPP_PORT__='$Port';</script></head>"
    [System.IO.File]::WriteAllText($indexHtml, $content, $Utf8NoBom)
}

# Remove hatchery/ (brainstem distribution only)
$hatcheryDir = Join-Path $ProjectDir "hatchery"
if (Test-Path $hatcheryDir) { Remove-Item -Recurse -Force $hatcheryDir }

# ── Business Mode UI ────────────────────────────────────────
$BizHtml = Join-Path $ProjectsDir "business.html"
if (-not (Test-Path $BizHtml)) {
    try {
        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kody-w/CommunityRAPP/main/business.html" -OutFile $BizHtml -UseBasicParsing
    } catch {}
}

# ── Update manifest ─────────────────────────────────────────
$Timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

if (Test-Path $Manifest) {
    $data = Get-Content $Manifest -Raw | ConvertFrom-Json
} else {
    $data = @{ projects = @{} }
}

$data.projects | Add-Member -NotePropertyName $ProjectName -NotePropertyValue @{
    path = $ProjectDir
    port = $Port
    created_at = $Timestamp
    python = $PYTHON_CMD
} -Force

    $manifestJson = $data | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText($Manifest, $manifestJson, $Utf8NoBom)

# ── Done ────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Project '$ProjectName' is ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Location:  $ProjectDir"
Write-Host "  Port:      $Port"
Write-Host "  Python:    $PYTHON_CMD"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host ""
Write-Host "  1. Start it:"
Write-Host "     cd $ProjectDir; .\start.ps1"
Write-Host ""
Write-Host "  2. Open the chat UI:"
Write-Host "     Start-Process `"$ProjectDir\index.html`""
Write-Host ""
Write-Host "  3. Send a message - the UI walks you through GitHub auth."
Write-Host "     No API keys needed."
Write-Host ""
if (Test-Path $BizHtml) {
    Write-Host "  4. Business Mode (multi-instance side-by-side):"
    Write-Host "     Start-Process `"$BizHtml`""
    Write-Host ""
}
Write-Host "  When you're ready for Azure:" -ForegroundColor White
Write-Host "     Edit $ProjectDir\local.settings.json"
Write-Host "     Then: func azure functionapp publish YOUR_APP --build remote"
Write-Host ""
