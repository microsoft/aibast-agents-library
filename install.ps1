# RAPP Brainstem Installer for Windows
# Usage: irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1 | iex
#
# Works on a factory Windows 11 install — auto-installs Python, Git, and GitHub CLI via winget.

$ErrorActionPreference = "Stop"

$BRAINSTEM_HOME = "$env:USERPROFILE\.brainstem"
$BRAINSTEM_BIN = "$env:USERPROFILE\.local\bin"
$REPO_URL = "https://github.com/microsoft/aibast-agents-library.git"
$REMOTE_VERSION_URL = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/rapp_brainstem/VERSION"

function Print-Banner {
    Write-Host ""
    Write-Host "  🧠 RAPP Brainstem" -ForegroundColor Cyan
    Write-Host "  Local-first AI agent server" -ForegroundColor Gray
    Write-Host "  Powered by GitHub Copilot — no API keys needed" -ForegroundColor Gray
    Write-Host ""
}

function Compare-SemVer {
    param([string]$Local, [string]$Remote)
    $lParts = $Local.Split('.')
    $rParts = $Remote.Split('.')
    for ($i = 0; $i -lt [Math]::Max($lParts.Length, $rParts.Length); $i++) {
        $lv = if ($i -lt $lParts.Length) { [int]$lParts[$i] } else { 0 }
        $rv = if ($i -lt $rParts.Length) { [int]$rParts[$i] } else { 0 }
        if ($rv -gt $lv) { return 1 }   # remote is newer
        if ($rv -lt $lv) { return -1 }  # local is newer
    }
    return 0  # equal
}

function Check-ForUpgrade {
    $versionFile = "$BRAINSTEM_HOME\src\rapp_brainstem\VERSION"

    if (-not (Test-Path $versionFile)) { return $true }

    $localVersion = (Get-Content $versionFile -Raw).Trim()

    try {
        $remoteVersion = (Invoke-WebRequest -Uri $REMOTE_VERSION_URL -UseBasicParsing -TimeoutSec 10).Content.Trim()
    } catch {
        Write-Host "  [!] Could not check remote version — upgrading anyway" -ForegroundColor Yellow
        return $true
    }

    Write-Host "  Local version:  $localVersion" -ForegroundColor Cyan
    Write-Host "  Remote version: $remoteVersion" -ForegroundColor Cyan

    if ($localVersion -eq $remoteVersion) {
        Write-Host ""
        Write-Host "  [OK] Already up to date (v$localVersion)" -ForegroundColor Green
        Write-Host ""
        return $false
    }

    $cmp = Compare-SemVer -Local $localVersion -Remote $remoteVersion
    if ($cmp -eq 1) {
        Write-Host "  [..] Upgrade available: $localVersion -> $remoteVersion" -ForegroundColor Yellow
        return $true
    }

    Write-Host ""
    Write-Host "  [OK] Already up to date (v$localVersion)" -ForegroundColor Green
    Write-Host ""
    return $false
}

function Install-WithWinget {
    param([string]$PackageId, [string]$Name)
    Write-Host "  [..] Installing $Name via winget..." -ForegroundColor Yellow
    winget install --id $PackageId --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null
    # Refresh PATH for this session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

function Check-Prerequisites {
    Write-Host "Checking prerequisites..."

    # winget (ships with Windows 11)
    try {
        winget --version 2>&1 | Out-Null
    } catch {
        Write-Host "  [X] winget not found — this installer requires Windows 10 1709+ or Windows 11" -ForegroundColor Red
        exit 1
    }

    # Git
    $gitOk = $false
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] $gitVersion" -ForegroundColor Green
            $gitOk = $true
        }
    } catch {}
    if (-not $gitOk) {
        Install-WithWinget "Git.Git" "Git"
        try {
            git --version 2>&1 | Out-Null
            Write-Host "  [OK] Git installed" -ForegroundColor Green
        } catch {
            Write-Host "  [X] Git install failed — install manually from https://git-scm.com" -ForegroundColor Red
            exit 1
        }
    }

    # Python 3.11+
    $pythonOk = $false
    $pythonCmd = $null

    # Try multiple python command names (python3 first on some systems, then python)
    foreach ($cmd in @("python3", "python")) {
        try {
            $out = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $out -match "Python 3\.(\d+)") {
                $minor = [int]$Matches[1]
                if ($minor -ge 11) {
                    Write-Host "  [OK] $out" -ForegroundColor Green
                    $pythonOk = $true
                    $pythonCmd = $cmd
                    break
                }
            }
        } catch {}
    }

    if (-not $pythonOk) {
        # Disable Windows App Execution Aliases that shadow real python
        # These stubs print "Python was not found" and prevent detection
        $aliasDir = "$env:LOCALAPPDATA\Microsoft\WindowsApps"
        foreach ($stub in @("python.exe", "python3.exe")) {
            $stubPath = Join-Path $aliasDir $stub
            if (Test-Path $stubPath) {
                try {
                    $target = (Get-Item $stubPath).Target
                    if (-not $target) {
                        # It's an App Execution Alias stub — rename it out of the way
                        Rename-Item $stubPath "$stub.disabled" -ErrorAction SilentlyContinue
                        Write-Host "  [..] Disabled Windows Store python stub" -ForegroundColor Yellow
                    }
                } catch {}
            }
        }

        Install-WithWinget "Python.Python.3.11" "Python 3.11"

        # winget installs to a known path — add it explicitly
        $pyBase = "$env:LOCALAPPDATA\Programs\Python\Python311"
        if (Test-Path $pyBase) {
            $env:Path = "$pyBase;$pyBase\Scripts;$env:Path"
        }
        # Also refresh from registry
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        # Verify the REAL python is now reachable
        $pythonOk = $false
        foreach ($cmd in @("python3", "python")) {
            try {
                $out = & $cmd --version 2>&1
                if ($LASTEXITCODE -eq 0 -and $out -match "Python 3\.(\d+)") {
                    Write-Host "  [OK] $out installed" -ForegroundColor Green
                    $pythonOk = $true
                    $pythonCmd = $cmd
                    break
                }
            } catch {}
        }

        # Last resort: try the known install path directly
        if (-not $pythonOk) {
            $directPy = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
            if (Test-Path $directPy) {
                $out = & $directPy --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  [OK] $out installed (direct path)" -ForegroundColor Green
                    $pythonOk = $true
                    $pythonCmd = $directPy
                }
            }
        }

        if (-not $pythonOk) {
            Write-Host "  [X] Python install failed — install from https://python.org" -ForegroundColor Red
            Write-Host "      Make sure to check 'Add Python to PATH' during install" -ForegroundColor Yellow
            exit 1
        }
    }

    # Store the working python command for later use
    $script:PythonExe = $pythonCmd

    # GitHub CLI (optional but recommended)
    try {
        gh --version 2>&1 | Out-Null
        Write-Host "  [OK] GitHub CLI installed" -ForegroundColor Green
    } catch {
        Write-Host "  [..] Installing GitHub CLI..." -ForegroundColor Yellow
        Install-WithWinget "GitHub.cli" "GitHub CLI"
        try {
            gh --version 2>&1 | Out-Null
            Write-Host "  [OK] GitHub CLI installed" -ForegroundColor Green
        } catch {
            Write-Host "  [!] GitHub CLI not installed (optional — you can authenticate later)" -ForegroundColor Yellow
        }
    }
}

function Install-Brainstem {
    Write-Host ""
    Write-Host "Installing RAPP Brainstem..."

    if (-not (Test-Path $BRAINSTEM_HOME)) {
        New-Item -ItemType Directory -Force -Path $BRAINSTEM_HOME | Out-Null
    }

    if (Test-Path "$BRAINSTEM_HOME\src\.git") {
        # Smart update — preserve soul, agents, config
        $LocalVer = "0.0.0"
        $VerFile = "$BRAINSTEM_HOME\src\rapp_brainstem\VERSION"
        if (Test-Path $VerFile) { $LocalVer = (Get-Content $VerFile -Raw).Trim() }
        try { $RemoteVer = (Invoke-WebRequest -Uri $REMOTE_VERSION_URL -UseBasicParsing -TimeoutSec 5).Content.Trim() } catch { $RemoteVer = "0.0.0" }

        Write-Host "  Local:  v$LocalVer"
        Write-Host "  Remote: v$RemoteVer"

        if ($LocalVer -eq $RemoteVer) {
            Write-Host "  [OK] Already up to date (v$LocalVer)" -ForegroundColor Green
        } else {
            Write-Host "  Upgrading v$LocalVer -> v$RemoteVer..."
            $Backup = "$env:TEMP\brainstem-upgrade-$(Get-Random)"
            New-Item -ItemType Directory -Force -Path $Backup | Out-Null

            # Backup user files
            $AgentsDir = "$BRAINSTEM_HOME\src\rapp_brainstem\agents"
            $SoulFile = "$BRAINSTEM_HOME\src\rapp_brainstem\soul.md"
            $EnvFile = "$BRAINSTEM_HOME\src\rapp_brainstem\.env"
            if (Test-Path $SoulFile) { Copy-Item $SoulFile "$Backup\soul.md" }
            if (Test-Path $EnvFile) { Copy-Item $EnvFile "$Backup\.env" }
            if (Test-Path $AgentsDir) { Copy-Item "$AgentsDir\*.py" "$Backup\" -ErrorAction SilentlyContinue }
            Write-Host "  [OK] Backed up soul, agents, config" -ForegroundColor Green

            # Pull latest
            Push-Location "$BRAINSTEM_HOME\src"
            try { git stash --quiet 2>&1 | Out-Null } catch {}
            try { git pull --quiet 2>&1 | Out-Null } catch {}
            Pop-Location
            Write-Host "  [OK] Framework updated" -ForegroundColor Green

            # Restore user files
            if (Test-Path "$Backup\soul.md") { Copy-Item "$Backup\soul.md" $SoulFile -Force }
            if (Test-Path "$Backup\.env") { Copy-Item "$Backup\.env" $EnvFile -Force }
            Get-ChildItem "$Backup\*.py" -ErrorAction SilentlyContinue | ForEach-Object {
                if ($_.Name -notin @("basic_agent.py", "__init__.py")) {
                    Copy-Item $_.FullName "$AgentsDir\$($_.Name)" -Force
                }
            }
            Remove-Item -Recurse -Force $Backup -ErrorAction SilentlyContinue
            Write-Host "  [OK] Upgrade complete: v$LocalVer -> v$RemoteVer" -ForegroundColor Green
        }
    } else {
        if (Test-Path "$BRAINSTEM_HOME\src") {
            Remove-Item -Recurse -Force "$BRAINSTEM_HOME\src" -ErrorAction SilentlyContinue
        }
        Write-Host "  Cloning repository..."
        git clone --quiet $REPO_URL "$BRAINSTEM_HOME\src" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [X] Failed to clone repository" -ForegroundColor Red
            exit 1
        }
    }
    Write-Host "  [OK] Source code ready" -ForegroundColor Green
}

function Run-PipInstall {
    $reqFile = "$BRAINSTEM_HOME\src\rapp_brainstem\requirements.txt"
    $py = if ($script:PythonExe) { $script:PythonExe } else { "python" }
    & $py -m pip install -r $reqFile
    if ($LASTEXITCODE -ne 0) {
        & $py -m pip install -r $reqFile --user
    }
}

function Check-PythonDeps {
    $py = if ($script:PythonExe) { $script:PythonExe } else { "python" }
    & $py -c "import flask, flask_cors, requests, dotenv" *> $null
    return $LASTEXITCODE -eq 0
}

function Setup-Dependencies {
    Write-Host ""
    Write-Host "Installing dependencies..."
    Push-Location "$BRAINSTEM_HOME\src\rapp_brainstem"
    Run-PipInstall
    if (-not (Check-PythonDeps)) {
        Write-Host "  [!] Some dependencies may not have installed correctly" -ForegroundColor Yellow
    }
    Pop-Location
    Write-Host "  [OK] Dependencies installed" -ForegroundColor Green
}

function Install-CLI {
    Write-Host ""
    Write-Host "Installing CLI..."

    if (-not (Test-Path $BRAINSTEM_BIN)) {
        New-Item -ItemType Directory -Force -Path $BRAINSTEM_BIN | Out-Null
    }

    # Batch wrapper (works in cmd.exe and PowerShell)
    $py = if ($script:PythonExe) { $script:PythonExe } else { "python" }
    $cmdContent = @"
@echo off
cd /d "$BRAINSTEM_HOME\src\rapp_brainstem"
$py brainstem.py %*
"@
    Set-Content -Path "$BRAINSTEM_BIN\brainstem.cmd" -Value $cmdContent

    # PowerShell wrapper
    $psContent = @"
Set-Location "$BRAINSTEM_HOME\src\rapp_brainstem"
& "$py" brainstem.py @args
"@
    Set-Content -Path "$BRAINSTEM_BIN\brainstem.ps1" -Value $psContent

    # Add to PATH if not already there
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$BRAINSTEM_BIN*") {
        [Environment]::SetEnvironmentVariable("Path", "$BRAINSTEM_BIN;$userPath", "User")
        $env:Path = "$BRAINSTEM_BIN;$env:Path"
        Write-Host "  Added to PATH" -ForegroundColor Green
    }

    Write-Host "  [OK] CLI installed" -ForegroundColor Green
}

function Create-Env {
    $envFile = "$BRAINSTEM_HOME\src\rapp_brainstem\.env"
    $exampleFile = "$BRAINSTEM_HOME\src\rapp_brainstem\.env.example"
    if (-not (Test-Path $envFile) -and (Test-Path $exampleFile)) {
        Copy-Item $exampleFile $envFile
    }
}

function Launch-Brainstem {
    # Always pull latest before launching
    if (Test-Path "$BRAINSTEM_HOME\src\.git") {
        Push-Location "$BRAINSTEM_HOME\src"
        try { git pull --quiet 2>&1 | Out-Null } catch {}
        Pop-Location
    }

    $tokenFile = "$BRAINSTEM_HOME\src\rapp_brainstem\.copilot_token"
    $clientId = "Iv1.b507a08c87ecfe98"

    # Check if already authenticated
    $needsAuth = $true
    if (Test-Path $tokenFile) {
        try {
            $tokenData = Get-Content $tokenFile -Raw | ConvertFrom-Json
            $savedToken = $tokenData.access_token
            if ($savedToken) {
                $authPrefix = if ($savedToken.StartsWith("ghu_")) { "token" } else { "Bearer" }
                $headers = @{
                    "Authorization" = "$authPrefix $savedToken"
                    "Accept" = "application/json"
                    "Editor-Version" = "vscode/1.95.0"
                    "Editor-Plugin-Version" = "copilot/1.0.0"
                }
                try {
                    $checkResp = Invoke-WebRequest -Uri "https://api.github.com/copilot_internal/v2/token" -Headers $headers -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
                    if ($checkResp.StatusCode -eq 200) {
                        Write-Host "  [OK] Already authenticated with GitHub Copilot" -ForegroundColor Green
                        $needsAuth = $false
                    }
                } catch {
                    Write-Host "  [..] Saved token expired — re-authenticating..." -ForegroundColor Yellow
                    Remove-Item $tokenFile -Force -ErrorAction SilentlyContinue
                }
            }
        } catch {
            Remove-Item $tokenFile -Force -ErrorAction SilentlyContinue
        }
    }

    if ($needsAuth) {
        Write-Host ""
        Write-Host "  Authenticating with GitHub Copilot..." -ForegroundColor Cyan
        Write-Host ""

        try {
            $deviceResp = Invoke-RestMethod -Uri "https://github.com/login/device/code" -Method Post -ContentType "application/x-www-form-urlencoded" -Body "client_id=$clientId" -Headers @{"Accept"="application/json"} -TimeoutSec 10

            $userCode = $deviceResp.user_code
            $deviceCode = $deviceResp.device_code
            $interval = if ($deviceResp.interval) { $deviceResp.interval } else { 5 }
            $verifyUri = $deviceResp.verification_uri

            if (-not $userCode -or -not $deviceCode) {
                Write-Host "  [!] Could not start auth — sign in at http://localhost:7071/login" -ForegroundColor Yellow
            } else {
                Write-Host "  ┌─────────────────────────────────────────┐"
                Write-Host "  │  Your code: " -NoNewline; Write-Host $userCode -ForegroundColor Cyan -NoNewline; Write-Host "                  │"
                Write-Host "  └─────────────────────────────────────────┘"
                Write-Host ""
                Write-Host "  Opening browser to authorize..."

                Start-Process $verifyUri
                Write-Host "  Waiting for authorization..."
                Write-Host ""

                for ($i = 0; $i -lt 60; $i++) {
                    Start-Sleep -Seconds $interval
                    try {
                        $pollResp = Invoke-RestMethod -Uri "https://github.com/login/oauth/access_token" -Method Post -ContentType "application/x-www-form-urlencoded" -Body "client_id=$clientId&device_code=$deviceCode&grant_type=urn:ietf:params:oauth:grant-type:device_code" -Headers @{"Accept"="application/json"} -TimeoutSec 10

                        if ($pollResp.access_token) {
                            $tokenJson = @{ access_token = $pollResp.access_token }
                            if ($pollResp.refresh_token) { $tokenJson.refresh_token = $pollResp.refresh_token }
                            $tokenJson | ConvertTo-Json | Set-Content $tokenFile

                            # Validate Copilot access
                            $authPrefix = if ($pollResp.access_token.StartsWith("ghu_")) { "token" } else { "Bearer" }
                            $headers = @{
                                "Authorization" = "$authPrefix $($pollResp.access_token)"
                                "Accept" = "application/json"
                                "Editor-Version" = "vscode/1.95.0"
                                "Editor-Plugin-Version" = "copilot/1.0.0"
                            }
                            try {
                                $copilotCheck = Invoke-WebRequest -Uri "https://api.github.com/copilot_internal/v2/token" -Headers $headers -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
                                if ($copilotCheck.StatusCode -eq 200) {
                                    Write-Host "  [OK] Authenticated — Copilot access confirmed" -ForegroundColor Green
                                }
                            } catch {
                                $statusCode = $_.Exception.Response.StatusCode.value__
                                if ($statusCode -eq 403) {
                                    Write-Host ""
                                    Write-Host "  [X] This GitHub account does NOT have Copilot access." -ForegroundColor Red
                                    Write-Host ""
                                    Write-Host "  Either:"
                                    Write-Host "    1. Sign up for Copilot: " -NoNewline; Write-Host "https://github.com/github-copilot/signup" -ForegroundColor Cyan
                                    Write-Host "    2. Re-run this installer and sign in with a different account"
                                    Write-Host ""
                                    Remove-Item $tokenFile -Force -ErrorAction SilentlyContinue
                                } else {
                                    Write-Host "  [OK] Authenticated with GitHub" -ForegroundColor Green
                                }
                            }
                            break
                        }

                        $error_code = $pollResp.error
                        if ($error_code -eq "expired_token") {
                            Write-Host "  [!] Auth timed out — sign in at http://localhost:7071/login" -ForegroundColor Yellow
                            break
                        }
                        if ($error_code -ne "authorization_pending" -and $error_code -ne "slow_down" -and $error_code) {
                            Write-Host "  [!] Auth error: $error_code" -ForegroundColor Yellow
                            break
                        }
                    } catch {}
                }
            }
        } catch {
            Write-Host "  [!] Could not start auth — sign in at http://localhost:7071/login" -ForegroundColor Yellow
        }
    }

    # Launch the server
    Write-Host ""
    Write-Host "  Starting RAPP Brainstem..." -ForegroundColor Cyan
    Write-Host ""

    Push-Location "$BRAINSTEM_HOME\src\rapp_brainstem"

    # Ensure deps are installed (handles first-run failure or stale install)
    if (-not (Check-PythonDeps)) {
        Write-Host "  [..] Installing missing dependencies..." -ForegroundColor Yellow
        Run-PipInstall
    }

    # Open browser after a delay
    Start-Job -ScriptBlock { Start-Sleep -Seconds 3; Start-Process "http://localhost:7071" } | Out-Null

    $py = if ($script:PythonExe) { $script:PythonExe } else { "python" }
    & $py brainstem.py
}

function Main {
    Print-Banner

    # Check if this is an upgrade of an existing install
    if (Test-Path "$BRAINSTEM_HOME\src\.git") {
        Write-Host "Checking for updates..."
        if (-not (Check-ForUpgrade)) {
            # Already up to date — just launch
            Launch-Brainstem
            return
        }
    }

    Check-Prerequisites
    Install-Brainstem
    Setup-Dependencies
    Install-CLI
    Create-Env

    $installedVersion = ""
    $vf = "$BRAINSTEM_HOME\src\rapp_brainstem\VERSION"
    if (Test-Path $vf) { $installedVersion = (Get-Content $vf -Raw).Trim() }

    Write-Host ""
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "  [OK] RAPP Brainstem v$installedVersion installed!" -ForegroundColor Green
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host ""

    Launch-Brainstem
}

Main
