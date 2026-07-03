# RAPP Brainstem Installer for Windows
# Usage: irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1 | iex
#
# Works on a factory Windows 11 install — auto-installs Python, Git, and GitHub CLI via winget.

$ErrorActionPreference = "Stop"

# Force TLS 1.2 for every web request in this session. Stock Windows PowerShell 5.1
# on older builds negotiates TLS 1.0 by default, which GitHub and raw.githubusercontent
# now refuse — the download would fail with an opaque "could not create SSL/TLS secure
# channel". Additive and harmless where 1.2 is already the default.
try {
    [Net.ServicePointManager]::SecurityProtocol = `
        [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
} catch {}

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

function Resolve-PythonExe {
    # Return a real Python 3 executable. Prefer the one Check-Prerequisites already
    # validated ($script:PythonExe); otherwise probe — this matters on the
    # "already up to date" fast path, which skips Check-Prerequisites and would
    # otherwise fall back to a bare "python" that may be the Windows Store alias
    # stub (it prints "Python was not found" and opens the Store instead of running).
    if ($script:PythonExe) { return $script:PythonExe }
    foreach ($cmd in @("python3", "python")) {
        try {
            $out = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $out -match "Python 3\.(\d+)") {
                $script:PythonExe = $cmd
                return $cmd
            }
        } catch {}
    }
    $direct = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    if (Test-Path $direct) { $script:PythonExe = $direct; return $direct }
    return "python"
}

function Test-PipWorks {
    param([string]$Py)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $Py -m pip --version 2>&1 | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    } finally {
        $ErrorActionPreference = $prev
    }
}

function Ensure-Pip {
    # A found Python is NOT guaranteed to have pip. Corp-managed images and
    # stripped/partial installs ship a working python.exe with no pip module —
    # seen in the wild on a fresh Windows 11 machine: every pip call printed
    # "No module named pip", then the server died at `import requests` behind a
    # dead localhost:7071 browser tab. Bootstrap order: ensurepip (stdlib,
    # works offline, restores the pip bundled with Python) -> get-pip.py (network).
    # Returns $true only when `python -m pip` actually works.
    $py = Resolve-PythonExe
    if (Test-PipWorks $py) { return $true }

    Write-Host "  [..] Python has no pip — bootstrapping via ensurepip..." -ForegroundColor Yellow
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        # Write-Host, not bare pipeline output: Ensure-Pip's return value is its
        # pipeline — stray tool output here would corrupt the caller's boolean.
        & $py -m ensurepip --upgrade --default-pip 2>&1 | ForEach-Object { Write-Host "$_" }
    } catch {
    } finally {
        $ErrorActionPreference = $prev
    }
    if (Test-PipWorks $py) {
        Write-Host "  [OK] pip bootstrapped via ensurepip" -ForegroundColor Green
        return $true
    }

    Write-Host "  [..] ensurepip unavailable — fetching get-pip.py..." -ForegroundColor Yellow
    $getPip = Join-Path $env:TEMP "rapp-get-pip.py"
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip -UseBasicParsing -TimeoutSec 120
        & $py $getPip 2>&1 | ForEach-Object { Write-Host "$_" }
    } catch {
    } finally {
        $ErrorActionPreference = $prev
        Remove-Item $getPip -Force -ErrorAction SilentlyContinue
    }
    if (Test-PipWorks $py) {
        Write-Host "  [OK] pip bootstrapped via get-pip.py" -ForegroundColor Green
        return $true
    }

    Write-Host "  [X] Python at '$py' has no pip and it could not be bootstrapped." -ForegroundColor Red
    Write-Host "      Fix it manually, then re-run this installer:" -ForegroundColor Yellow
    Write-Host "        `"$py`" -m ensurepip --upgrade --default-pip" -ForegroundColor Cyan
    Write-Host "      Or reinstall Python from https://python.org with 'pip' checked." -ForegroundColor Yellow
    return $false
}

function Check-Prerequisites {
    Write-Host "Checking prerequisites..."

    # winget (ships with Windows 11)
    try {
        winget --version 2>&1 | Out-Null
    } catch {
        Write-Host "  [X] winget not found — this installer requires Windows 10 1709+ or Windows 11" -ForegroundColor Red
        throw "winget not found"
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
            throw "Git install failed"
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
            throw "Python 3.11+ install failed"
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

            # Pull latest from THIS installer's repo. A prior install may have cloned from a
            # different origin (fork/mirror); repoint origin and hard-reset to it so the upgrade
            # is reliable even across unrelated histories. User files (soul, agents, .env) were
            # backed up above and are restored below; tokens and .brainstem_data are gitignored.
            Push-Location "$BRAINSTEM_HOME\src"
            $prevEAP = $ErrorActionPreference
            $ErrorActionPreference = 'Continue'
            git remote set-url origin $REPO_URL 2>&1 | Out-Null
            git fetch --quiet origin main 2>&1 | Out-Null
            $pullOk = ($LASTEXITCODE -eq 0)
            if ($pullOk) {
                git reset --hard --quiet FETCH_HEAD 2>&1 | Out-Null
                $pullOk = ($LASTEXITCODE -eq 0)
            }
            $ErrorActionPreference = $prevEAP
            Pop-Location
            if ($pullOk) {
                Write-Host "  [OK] Framework updated" -ForegroundColor Green
            } else {
                Write-Host "  [!] Update download failed — keeping existing files (v$LocalVer)" -ForegroundColor Yellow
            }

            # Restore user files
            if (Test-Path "$Backup\soul.md") { Copy-Item "$Backup\soul.md" $SoulFile -Force }
            if (Test-Path "$Backup\.env") { Copy-Item "$Backup\.env" $EnvFile -Force }
            Get-ChildItem "$Backup\*.py" -ErrorAction SilentlyContinue | ForEach-Object {
                if ($_.Name -notin @("basic_agent.py", "__init__.py")) {
                    Copy-Item $_.FullName "$AgentsDir\$($_.Name)" -Force
                }
            }
            Remove-Item -Recurse -Force $Backup -ErrorAction SilentlyContinue
            # Report the version actually on disk after the pull, not the remote string —
            # if the pull failed the banner must not claim a successful upgrade.
            $NewVer = $LocalVer
            if (Test-Path $VerFile) { $NewVer = (Get-Content $VerFile -Raw).Trim() }
            if ($pullOk -and $NewVer -ne $LocalVer) {
                Write-Host "  [OK] Upgrade complete: v$LocalVer -> v$NewVer" -ForegroundColor Green
            } elseif ($pullOk) {
                Write-Host "  [OK] Already at the latest framework (v$NewVer)" -ForegroundColor Green
            }
        }
    } else {
        if (Test-Path "$BRAINSTEM_HOME\src") {
            Remove-Item -Recurse -Force "$BRAINSTEM_HOME\src" -ErrorAction SilentlyContinue
        }
        Write-Host "  Cloning repository..."
        git clone --quiet $REPO_URL "$BRAINSTEM_HOME\src" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [X] Failed to clone repository" -ForegroundColor Red
            throw "git clone failed"
        }
    }
    Write-Host "  [OK] Source code ready" -ForegroundColor Green
}

function Run-PipInstall {
    $reqFile = "$BRAINSTEM_HOME\src\rapp_brainstem\requirements.txt"
    $py = Resolve-PythonExe
    # Without pip every install below is guaranteed noise — bootstrap it first.
    # On $false, Ensure-Pip already printed the actionable fix; the dep gates in
    # Setup-Dependencies / Launch-Brainstem turn that into an honest failure.
    if (-not (Ensure-Pip)) { return }
    # Use the call operator, NOT Start-Process (same reasoning as Check-PythonDeps):
    # the call operator quotes a $reqFile path containing spaces correctly, and it
    # needs no console attachment — Start-Process -NoNewWindow -Wait can block
    # forever in consoleless sessions (CI, some terminal hosts). Drop
    # ErrorActionPreference to Continue locally so pip's stderr progress lines are
    # not promoted to a terminating NativeCommandError under the script's global
    # $ErrorActionPreference = 'Stop'.
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $py -m pip install -r $reqFile 2>&1 | ForEach-Object { "$_" }
        if ($LASTEXITCODE -ne 0) {
            & $py -m pip install -r $reqFile --user 2>&1 | ForEach-Object { "$_" }
        }
    } finally {
        $ErrorActionPreference = $prev
    }
}

function Check-PythonDeps {
    $py = Resolve-PythonExe
    # Use the call operator, NOT Start-Process -ArgumentList. Start-Process joins array
    # arguments with spaces but does not re-quote an element that itself contains spaces,
    # so "-c", "import flask, flask_cors, ..." reached python as the tokens
    # "-c import flask, flask_cors, ..." — python's -c got only "import" -> SyntaxError.
    # The call operator quotes arguments correctly. Drop ErrorActionPreference to Continue
    # locally so python's stderr (e.g. when a module is missing) is not promoted to a
    # terminating NativeCommandError under the script's global $ErrorActionPreference='Stop'.
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $py -c "import flask, flask_cors, requests, dotenv" 2>&1 | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    } finally {
        $ErrorActionPreference = $prev
    }
}

function Setup-Dependencies {
    Write-Host ""
    Write-Host "Installing dependencies..."
    Push-Location "$BRAINSTEM_HOME\src\rapp_brainstem"
    Run-PipInstall
    $depsOk = Check-PythonDeps
    if (-not $depsOk) {
        # v0.6.2 accidentally self-healed transient pip failures via the second
        # Run-PipInstall in Launch-Brainstem. Keep one deliberate retry here so
        # a PyPI/DNS blip doesn't hard-abort a fresh install.
        Write-Host "  [..] Dependency check failed — retrying pip install once..." -ForegroundColor Yellow
        Run-PipInstall
        $depsOk = Check-PythonDeps
    }
    Pop-Location
    if (-not $depsOk) {
        # Never print [OK] and continue toward a server that will die at
        # `import requests` behind a dead browser tab — stop here, honestly,
        # with the guidance Ensure-Pip/pip printed above.
        throw "Python dependencies failed to install (see messages above)"
    }
    Write-Host "  [OK] Dependencies installed" -ForegroundColor Green
}

function Install-CLI {
    Write-Host ""
    Write-Host "Installing CLI..."

    if (-not (Test-Path $BRAINSTEM_BIN)) {
        New-Item -ItemType Directory -Force -Path $BRAINSTEM_BIN | Out-Null
    }

    # Batch wrapper (works in cmd.exe and PowerShell). Quote the interpreter path —
    # the direct-path fallback (…\First Last\AppData\…\python.exe) contains spaces and
    # would otherwise split into a broken command.
    $py = Resolve-PythonExe
    $cmdContent = @"
@echo off
cd /d "$BRAINSTEM_HOME\src\rapp_brainstem"
"$py" brainstem.py %*
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
    # Refresh from this installer's repo before launching (no-op if already current).
    if (Test-Path "$BRAINSTEM_HOME\src\.git") {
        Push-Location "$BRAINSTEM_HOME\src"
        $prevEAP = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        git remote set-url origin $REPO_URL 2>&1 | Out-Null
        git pull --quiet origin main 2>&1 | Out-Null
        $ErrorActionPreference = $prevEAP
        Pop-Location
    }

    # Dependencies BEFORE auth: if they cannot be installed, fail now — not after
    # walking the user through a GitHub device-code authorization they can't use.
    Push-Location "$BRAINSTEM_HOME\src\rapp_brainstem"
    if (-not (Check-PythonDeps)) {
        Write-Host "  [..] Installing missing dependencies..." -ForegroundColor Yellow
        Run-PipInstall
        if (-not (Check-PythonDeps)) {
            Pop-Location
            # Launching anyway would crash at `import requests` and strand the user
            # on a browser tab pointing at a server that never bound port 7071.
            throw "Python dependencies are missing and could not be installed (see messages above)"
        }
    }
    Pop-Location

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

    # Open browser after a delay
    Start-Job -ScriptBlock { Start-Sleep -Seconds 3; Start-Process "http://localhost:7071" } | Out-Null

    $py = Resolve-PythonExe
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
    # CLI wrappers and .env before dependencies: they are cheap, offline-safe and
    # idempotent. If Setup-Dependencies throws, VERSION already matches remote, so
    # a re-run takes the fast path and would otherwise never come back for them.
    Install-CLI
    Create-Env
    Setup-Dependencies

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

# Invoked as `irm … | iex`, a bare `exit`/uncaught throw terminates the USER'S whole
# PowerShell session — the window closes and the error vanishes. Catch here so a
# failure prints an actionable message and control returns to their prompt instead.
try {
    Main
} catch {
    Write-Host ""
    Write-Host "  [X] Install failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "      Nothing was launched. Fix the issue above and re-run the installer." -ForegroundColor Yellow
    Write-Host "      Need help? Open an issue at https://github.com/microsoft/aibast-agents-library/issues" -ForegroundColor Gray
    Write-Host ""
    # `irm | iex` has no $PSCommandPath — return to the prompt quietly. A file-based
    # run (CI, a saved script) must still report failure through the exit code.
    if ($PSCommandPath) { exit 1 }
}
