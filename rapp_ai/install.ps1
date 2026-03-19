# ═══════════════════════════════════════════════════════════════════════════════
#  RAPP Hippocampus — Windows Installer (PowerShell)
#  Usage: irm https://raw.githubusercontent.com/kody-w/m365-agents-for-python/main/CommunityRAPP/install.ps1 | iex
#  Or:    .\install.ps1
# ═══════════════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"

# ── Constants ─────────────────────────────────────────────────────────────────
$Version        = "1.0.0"
$InstallDir     = Join-Path $env:USERPROFILE ".communityrapp"
$RepoDir        = Join-Path $InstallDir "src"
$SourceDir      = Join-Path $RepoDir "CommunityRAPP"
$VenvDir        = Join-Path $InstallDir "venv"
$BinDir         = Join-Path $env:USERPROFILE ".local\bin"
$RepoUrl        = "https://github.com/kody-w/m365-agents-for-python.git"
$ServerPort     = 7071
$ServerUrl      = "http://localhost:$ServerPort"

# ── Helpers ───────────────────────────────────────────────────────────────────
function Write-Info    { param($Msg) Write-Host "  i " -ForegroundColor Cyan -NoNewline; Write-Host $Msg }
function Write-Ok      { param($Msg) Write-Host "  ✓ " -ForegroundColor Green -NoNewline; Write-Host $Msg }
function Write-Warn    { param($Msg) Write-Host "  ⚠ " -ForegroundColor Yellow -NoNewline; Write-Host $Msg }
function Write-Err     { param($Msg) Write-Host "  ✗ " -ForegroundColor Red -NoNewline; Write-Host $Msg; exit 1 }
function Write-Step    { param($Msg) Write-Host ""; Write-Host "  ▸ $Msg" -ForegroundColor Cyan }

function Prompt-User {
    param(
        [string]$Prompt,
        [string]$Default = ""
    )
    if ($Default) {
        Write-Host "  ? $Prompt [$Default]: " -ForegroundColor Cyan -NoNewline
    } else {
        Write-Host "  ? ${Prompt}: " -ForegroundColor Cyan -NoNewline
    }
    $answer = Read-Host
    if ([string]::IsNullOrWhiteSpace($answer) -and $Default) {
        return $Default
    }
    return $answer
}

function Test-CommandExists {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# ── Banner ────────────────────────────────────────────────────────────────────
function Show-Banner {
    Write-Host ""
    Write-Host "  ╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║                                                   ║" -ForegroundColor Cyan
    Write-Host "  ║   🧠 RAPP Hippocampus         ║" -ForegroundColor Cyan
    Write-Host "  ║                                                   ║" -ForegroundColor Cyan
    Write-Host "  ║   The memory center for your AI agents            ║" -ForegroundColor Cyan
    Write-Host "  ║   Local-first — deploy to Azure when ready        ║" -ForegroundColor Cyan
    Write-Host "  ║                                                   ║" -ForegroundColor Cyan
    Write-Host "  ╚═══════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Installer v$Version — Windows $([System.Environment]::OSVersion.Version)" -ForegroundColor DarkGray
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Prerequisites
# ═══════════════════════════════════════════════════════════════════════════════

function Test-WingetAvailable {
    try {
        $null = Get-Command winget -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Check-Python {
    Write-Step "Checking Python 3.11+..."

    $pythonCmd = $null
    foreach ($cmd in @("python3.11", "python3.12", "python3.13", "python3", "python")) {
        try {
            $ver = & $cmd --version 2>&1
            if ($ver -match '(\d+)\.(\d+)') {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                if ($major -ge 3 -and $minor -ge 11) {
                    $pythonCmd = $cmd
                    break
                }
            }
        } catch { }
    }

    if ($pythonCmd) {
        $script:PythonCmd = $pythonCmd
        $verStr = & $pythonCmd --version 2>&1
        Write-Ok "Python $($verStr -replace 'Python ','')"
        return
    }

    Write-Warn "Python 3.11+ not found — installing..."
    if (Test-WingetAvailable) {
        winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements --silent
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    } else {
        Write-Err "winget not available. Please install Python 3.11+ from https://python.org and re-run."
    }

    # Re-check
    foreach ($cmd in @("python3.11", "python3", "python")) {
        try {
            $ver = & $cmd --version 2>&1
            if ($ver -match '(\d+)\.(\d+)' -and [int]$Matches[1] -ge 3 -and [int]$Matches[2] -ge 11) {
                $script:PythonCmd = $cmd
                Write-Ok "Python installed: $ver"
                return
            }
        } catch { }
    }
    Write-Err "Could not install Python 3.11+. Please install manually from https://python.org"
}

function Check-Git {
    Write-Step "Checking Git..."

    if (Test-CommandExists "git") {
        $gitVer = git --version
        Write-Ok $gitVer
        return
    }

    Write-Warn "Git not found — installing..."
    if (Test-WingetAvailable) {
        winget install Git.Git --accept-source-agreements --accept-package-agreements --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    } else {
        Write-Err "Please install Git from https://git-scm.com and re-run."
    }

    if (Test-CommandExists "git") {
        Write-Ok "Git installed: $(git --version)"
    } else {
        Write-Err "Could not install Git. Please install manually from https://git-scm.com"
    }
}

function Check-Node {
    Write-Step "Checking Node.js 18+..."

    if (Test-CommandExists "node") {
        $nodeVer = node --version
        $nodeMajor = [int]($nodeVer -replace 'v(\d+)\..*', '$1')
        if ($nodeMajor -ge 18) {
            Write-Ok "Node.js $nodeVer"
            return
        }
        Write-Warn "Node.js $nodeVer found but need 18+ — upgrading..."
    } else {
        Write-Warn "Node.js not found — installing..."
    }

    if (Test-WingetAvailable) {
        winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    } else {
        Write-Err "Please install Node.js LTS from https://nodejs.org and re-run."
    }

    if (Test-CommandExists "node") {
        $nodeVer = node --version
        $nodeMajor = [int]($nodeVer -replace 'v(\d+)\..*', '$1')
        if ($nodeMajor -ge 18) {
            Write-Ok "Node.js $nodeVer"
        } else {
            Write-Err "Node.js 18+ required but got $nodeVer. Please update manually."
        }
    } else {
        Write-Err "Could not install Node.js. Please install from https://nodejs.org"
    }
}

function Check-FuncTools {
    Write-Step "Checking Azure Functions Core Tools v4..."

    if (Test-CommandExists "func") {
        $funcVer = func --version 2>$null | Select-Object -First 1
        $funcMajor = [int]($funcVer -replace '(\d+)\..*', '$1')
        if ($funcMajor -ge 4) {
            Write-Ok "Azure Functions Core Tools v$funcVer"
            return
        }
        Write-Warn "Azure Functions Core Tools v$funcVer found but need v4+ — upgrading..."
    } else {
        Write-Warn "Azure Functions Core Tools not found — installing..."
    }

    npm install -g azure-functions-core-tools@4 --unsafe-perm true 2>&1 | Select-Object -Last 1
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

    if (Test-CommandExists "func") {
        $funcVer = func --version 2>$null | Select-Object -First 1
        Write-Ok "Azure Functions Core Tools v$funcVer"
    } else {
        Write-Err "Could not install Azure Functions Core Tools. Run: npm install -g azure-functions-core-tools@4"
    }
}

function Check-Prerequisites {
    Write-Host ""
    Write-Host "  ── Prerequisites ──────────────────────────────────" -ForegroundColor White
    Write-Info "Detected: Windows $([System.Environment]::OSVersion.Version)"

    Check-Python
    Check-Git
    Check-Node
    Check-FuncTools

    Write-Host ""
    Write-Ok "All prerequisites satisfied!"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Install / Update Repository
# ═══════════════════════════════════════════════════════════════════════════════

function Install-CommunityRAPP {
    Write-Host ""
    Write-Host "  ── Installing CommunityRAPP ───────────────────────" -ForegroundColor White

    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }

    if (Test-Path (Join-Path $RepoDir ".git")) {
        Write-Step "Existing installation found — checking for updates..."

        $localVersion = "0.0.0"
        $versionFile = Join-Path $SourceDir "VERSION"
        if (Test-Path $versionFile) {
            $localVersion = (Get-Content $versionFile -Raw).Trim()
        }

        Push-Location $RepoDir
        try {
            git fetch origin main --quiet 2>$null
            $remoteVersion = git show origin/main:CommunityRAPP/VERSION 2>$null
            if (-not $remoteVersion) { $remoteVersion = $localVersion }
            $remoteVersion = $remoteVersion.Trim()

            if ($localVersion -ne $remoteVersion) {
                Write-Info "Upgrading: v$localVersion -> v$remoteVersion"
                git pull origin main --quiet
                Write-Ok "Updated to v$remoteVersion"
            } else {
                Write-Ok "Already up to date (v$localVersion)"
            }
        } finally {
            Pop-Location
        }
    } else {
        Write-Step "Cloning repository..."
        if (Test-Path $RepoDir) {
            Remove-Item $RepoDir -Recurse -Force
        }
        git clone --depth 1 $RepoUrl $RepoDir 2>&1 | Select-Object -Last 1
        Write-Ok "Repository cloned"
    }

    # Verify
    if (-not (Test-Path (Join-Path $SourceDir "function_app.py"))) {
        Write-Err "Installation failed — CommunityRAPP source not found at $SourceDir"
    }

    # Write version marker
    $Version | Set-Content (Join-Path $SourceDir "VERSION") -NoNewline
    Write-Ok "CommunityRAPP v$Version ready at $SourceDir"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Virtual Environment
# ═══════════════════════════════════════════════════════════════════════════════

function Setup-Venv {
    Write-Host ""
    Write-Host "  ── Setting up Python environment ──────────────────" -ForegroundColor White

    $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"

    if ((Test-Path $VenvDir) -and (Test-Path $activateScript)) {
        Write-Step "Existing virtual environment found — updating packages..."
    } else {
        Write-Step "Creating virtual environment..."
        & $script:PythonCmd -m venv $VenvDir
        Write-Ok "Virtual environment created"
    }

    # Activate
    & $activateScript

    Write-Step "Installing dependencies..."
    pip install --upgrade pip --quiet 2>&1 | Select-Object -Last 1
    pip install -r (Join-Path $SourceDir "requirements.txt") --quiet 2>&1 | Select-Object -Last 3

    $pkgCount = (pip list --format=columns 2>$null | Select-Object -Skip 2).Count
    Write-Ok "$pkgCount packages installed in virtual environment"

    deactivate 2>$null
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Azure OpenAI Configuration
# ═══════════════════════════════════════════════════════════════════════════════

function Configure-OpenAI {
    Write-Host ""
    Write-Host "  ── Azure OpenAI Configuration ─────────────────────" -ForegroundColor White

    $settingsFile = Join-Path $SourceDir "local.settings.json"

    # Check existing
    if (Test-Path $settingsFile) {
        Write-Warn "local.settings.json already exists"
        $overwrite = Prompt-User "Overwrite with new configuration? (y/N)" "N"
        if ($overwrite -notmatch '^[Yy]') {
            Write-Ok "Keeping existing configuration"
            return
        }
    }

    Write-Host ""
    Write-Host "  How would you like to connect to Azure OpenAI?" -ForegroundColor White
    Write-Host ""
    Write-Host "    1) " -ForegroundColor Cyan -NoNewline; Write-Host "Enter API key manually"
    Write-Host "    2) " -ForegroundColor Cyan -NoNewline; Write-Host "Use Azure CLI login (az login) — " -NoNewline; Write-Host "recommended for Azure users" -ForegroundColor DarkGray
    Write-Host "    3) " -ForegroundColor Cyan -NoNewline; Write-Host "Skip for now " -NoNewline; Write-Host "(configure later)" -ForegroundColor DarkGray
    Write-Host ""

    $authChoice = Prompt-User "Choose [1/2/3]" "3"

    $apiKey      = ""
    $endpoint    = ""
    $deployment  = "gpt-4o"
    $apiVersion  = "2024-08-01-preview"

    switch ($authChoice) {
        "1" {
            Write-Step "Manual API key configuration"
            Write-Host ""
            $apiKey = Prompt-User "Azure OpenAI API key"
            if ([string]::IsNullOrWhiteSpace($apiKey)) {
                Write-Warn "No API key provided — using placeholder"
                $apiKey = "<your-openai-api-key>"
            }
            $endpoint = Prompt-User "Azure OpenAI endpoint (e.g. https://your-resource.openai.azure.com/)"
            if ([string]::IsNullOrWhiteSpace($endpoint)) {
                $endpoint = "https://<your-openai-resource>.openai.azure.com/"
            }
            $deployment = Prompt-User "Deployment name" "gpt-4o"
            $apiVersion = Prompt-User "API version" "2024-08-01-preview"
            Write-Ok "API key configured"
        }
        "2" {
            Write-Step "Azure CLI authentication"
            if (Test-CommandExists "az") {
                try {
                    $null = az account show 2>$null
                } catch {
                    Write-Info "Opening Azure login..."
                    az login 2>&1 | Select-Object -Last 3
                }
                $userName = az account show --query user.name -o tsv 2>$null
                Write-Ok "Azure CLI authenticated as $userName"

                Write-Info "Searching for Azure OpenAI resources in your subscription..."
                $oaiResources = az cognitiveservices account list --query "[?kind=='OpenAI'].{name:name, endpoint:properties.endpoint}" -o table 2>$null
                if ($oaiResources) {
                    Write-Host "  Found Azure OpenAI resources:" -ForegroundColor Green
                    $oaiResources | ForEach-Object { Write-Host "    $_" }
                    Write-Host ""
                }

                $endpoint = Prompt-User "Azure OpenAI endpoint (e.g. https://your-resource.openai.azure.com/)"
                if ([string]::IsNullOrWhiteSpace($endpoint)) {
                    $endpoint = "https://<your-openai-resource>.openai.azure.com/"
                }
                $deployment = Prompt-User "Deployment name" "gpt-4o"
                $apiKey = ""
                Write-Ok "Will use Azure CLI (Entra ID) authentication — no API key needed"
            } else {
                Write-Warn "Azure CLI not found. Install from: https://aka.ms/installazurecli"
                Write-Warn "Falling back to placeholder configuration"
                $apiKey = "<your-openai-api-key>"
                $endpoint = "https://<your-openai-resource>.openai.azure.com/"
            }
        }
        default {
            Write-Info "Skipping Azure OpenAI configuration"
            Write-Info "Edit $settingsFile later"
            $apiKey = "<your-openai-api-key>"
            $endpoint = "https://<your-openai-resource>.openai.azure.com/"
        }
    }

    Write-Step "Generating local.settings.json..."

    $settings = @{
        IsEncrypted = $false
        Values = @{
            FUNCTIONS_WORKER_RUNTIME        = "python"
            AzureWebJobsStorage             = "UseDevelopmentStorage=true"
            AZURE_OPENAI_API_KEY            = $apiKey
            AZURE_OPENAI_ENDPOINT           = $endpoint
            AZURE_OPENAI_API_VERSION        = $apiVersion
            AZURE_OPENAI_DEPLOYMENT_NAME    = $deployment
            ASSISTANT_NAME                  = "Memory Agent"
            CHARACTERISTIC_DESCRIPTION      = "An AI assistant with persistent memory across conversations"
            USE_CLOUD_STORAGE               = "false"
        }
        Host = @{
            CORS            = "*"
            CORSCredentials = $false
        }
    }

    $settings | ConvertTo-Json -Depth 3 | Set-Content $settingsFile -Encoding UTF8
    Write-Ok "Configuration saved to local.settings.json"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  CLI Launcher
# ═══════════════════════════════════════════════════════════════════════════════

function Install-CLI {
    Write-Host ""
    Write-Host "  ── Installing CLI commands ────────────────────────" -ForegroundColor White

    if (-not (Test-Path $BinDir)) {
        New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
    }

    # ── communityrapp.cmd ─────────────────────────────────────────────────────
    $launcherCmd = Join-Path $BinDir "communityrapp.cmd"
    $launcherContent = @"
@echo off
REM RAPP Hippocampus — CLI Launcher
setlocal

set INSTALL_DIR=%USERPROFILE%\.communityrapp
set SOURCE_DIR=%INSTALL_DIR%\src\CommunityRAPP
set VENV_DIR=%INSTALL_DIR%\venv

if not exist "%SOURCE_DIR%" (
    echo Error: CommunityRAPP not found at %SOURCE_DIR%
    echo Run the installer: .\install.ps1
    exit /b 1
)

cd /d "%SOURCE_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

if "%1"=="" goto start
if "%1"=="start" goto start
if "%1"=="status" goto status
if "%1"=="test" goto test_msg
if "%1"=="update" goto update
if "%1"=="version" goto version
if "%1"=="help" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help
echo Unknown command: %1 (try 'communityrapp help')
exit /b 1

:start
echo Starting Hippocampus on http://localhost:7071
echo Press Ctrl+C to stop
echo.
start "" "%SOURCE_DIR%\index.html"
func start
goto end

:status
curl -sf http://localhost:7071/api/health && echo. || echo Server not running
goto end

:test_msg
echo Sending test message...
curl -s -X POST http://localhost:7071/api/businessinsightbot_function -H "Content-Type: application/json" -d "{\"user_input\": \"Hello! What can you do?\", \"conversation_history\": []}"
echo.
goto end

:update
cd /d "%INSTALL_DIR%\src"
git pull origin main
call "%VENV_DIR%\Scripts\activate.bat"
pip install -r "%SOURCE_DIR%\requirements.txt" --quiet
if exist "%SOURCE_DIR%\VERSION" (type "%SOURCE_DIR%\VERSION") else (echo latest)
echo Updated!
goto end

:version
if exist "%SOURCE_DIR%\VERSION" (type "%SOURCE_DIR%\VERSION") else (echo unknown)
echo.
goto end

:help
echo RAPP Hippocampus
echo.
echo Usage: communityrapp [command]
echo.
echo Commands:
echo   start     Start the server (default)
echo   status    Check if server is running
echo   test      Send a test message
echo   update    Pull latest updates
echo   version   Show installed version
echo   help      Show this help
goto end

:end
endlocal
"@
    Set-Content -Path $launcherCmd -Value $launcherContent -Encoding ASCII
    Write-Ok "Created: communityrapp.cmd"

    # ── crapp.cmd (alias) ─────────────────────────────────────────────────────
    $aliasCmd = Join-Path $BinDir "crapp.cmd"
    $aliasContent = @"
@echo off
REM Alias for communityrapp
"%USERPROFILE%\.local\bin\communityrapp.cmd" %*
"@
    Set-Content -Path $aliasCmd -Value $aliasContent -Encoding ASCII
    Write-Ok "Created: crapp.cmd (alias)"

    # ── Add to User PATH ─────────────────────────────────────────────────────
    $currentPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$BinDir*") {
        [System.Environment]::SetEnvironmentVariable("Path", "$BinDir;$currentPath", "User")
        $env:Path = "$BinDir;$env:Path"
        Write-Info "Added $BinDir to User PATH"
        Write-Info "Restart your terminal for PATH changes to take effect"
    }

    Write-Ok "CLI commands installed to $BinDir"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Launch
# ═══════════════════════════════════════════════════════════════════════════════

function Launch-CommunityRAPP {
    Write-Host ""
    Write-Host "  ── Launching CommunityRAPP ────────────────────────" -ForegroundColor White

    Push-Location $SourceDir
    try {
        $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
        & $activateScript

        Write-Step "Starting Azure Functions host..."

        # Start func in background
        $funcJob = Start-Job -ScriptBlock {
            param($dir, $venv)
            Set-Location $dir
            & (Join-Path $venv "Scripts\Activate.ps1")
            func start
        } -ArgumentList $SourceDir, $VenvDir

        # Wait for server (max 30s)
        $maxWait = 30
        $waited = 0
        $ready = $false

        while ($waited -lt $maxWait) {
            try {
                $response = Invoke-WebRequest -Uri "$ServerUrl/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    $ready = $true
                    break
                }
            } catch { }
            Start-Sleep -Seconds 1
            $waited++
            Write-Host "." -NoNewline
        }
        Write-Host ""

        if ($ready) {
            Write-Ok "Server is running on $ServerUrl"

            # Open the chat UI in the default browser
            $chatFile = Join-Path $SourceDir "index.html"
            if (Test-Path $chatFile) {
                Write-Step "Opening chat UI..."
                Start-Process $chatFile
                Write-Ok "Chat UI opened in browser"
            }
        } else {
            Write-Warn "Server started but health check timed out (it may still be initializing)"
        }

        # Stop the background job — user will start it themselves
        Stop-Job $funcJob -ErrorAction SilentlyContinue
        Remove-Job $funcJob -Force -ErrorAction SilentlyContinue

        deactivate 2>$null
    } finally {
        Pop-Location
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Success Banner
# ═══════════════════════════════════════════════════════════════════════════════

function Show-Success {
    $installedVersion = $Version
    $versionFile = Join-Path $SourceDir "VERSION"
    if (Test-Path $versionFile) {
        $installedVersion = (Get-Content $versionFile -Raw).Trim()
    }

    Write-Host ""
    Write-Host "  ═══════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  ✓ CommunityRAPP v$installedVersion installed!" -ForegroundColor Green
    Write-Host "  ═══════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Start the server:" -ForegroundColor White
    Write-Host "    communityrapp" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Test memory:" -ForegroundColor White
    Write-Host "    curl -X POST http://localhost:7071/api/businessinsightbot_function \" -ForegroundColor DarkGray
    Write-Host "      -H `"Content-Type: application/json`" \" -ForegroundColor DarkGray
    Write-Host "      -d '{`"user_input`": `"Remember that I love coding`", `"conversation_history`": []}'" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  Other commands:" -ForegroundColor White
    Write-Host "    communityrapp status" -ForegroundColor Cyan -NoNewline; Write-Host "   — Check server health"
    Write-Host "    communityrapp test" -ForegroundColor Cyan -NoNewline; Write-Host "     — Send a test message"
    Write-Host "    communityrapp update" -ForegroundColor Cyan -NoNewline; Write-Host "   — Pull latest version"
    Write-Host "    crapp" -ForegroundColor Cyan -NoNewline; Write-Host "                  — Short alias"
    Write-Host ""
    Write-Host "  Next steps:" -ForegroundColor White
    Write-Host "    • " -NoNewline; Write-Host "Deploy to Azure:" -ForegroundColor Green -NoNewline; Write-Host " see docs/DEPLOYMENT.md"
    Write-Host "    • " -NoNewline; Write-Host "Add custom agents:" -ForegroundColor Green -NoNewline; Write-Host " drop *_agent.py files in agents/"
    Write-Host "    • " -NoNewline; Write-Host "Configure memory:" -ForegroundColor Green -NoNewline; Write-Host " edit local.settings.json"
    Write-Host ""
    Write-Host "  Installation: ~/.communityrapp/" -ForegroundColor DarkGray
    Write-Host "  Need help?  communityrapp help" -ForegroundColor DarkGray
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════════════

function Main {
    Show-Banner
    Check-Prerequisites
    Install-CommunityRAPP
    Setup-Venv
    Configure-OpenAI
    Install-CLI
    Launch-CommunityRAPP
    Show-Success
}

# Handle --help
if ($args -contains "--help" -or $args -contains "-h") {
    Write-Host "CommunityRAPP Installer"
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  irm https://raw.githubusercontent.com/kody-w/m365-agents-for-python/main/CommunityRAPP/install.ps1 | iex"
    Write-Host "  .\install.ps1"
    Write-Host ""
    Write-Host "This script installs RAPP Hippocampus to ~/.communityrapp/"
    Write-Host "and creates CLI commands: communityrapp, crapp"
    exit 0
}

Main
