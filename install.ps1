# RAPP Brainstem Installer for Windows
# Usage: irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1 | iex
#
# Works on a factory Windows 11 install — auto-installs Python and Git via winget.

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
$SOURCE_OVERRIDE_REQUESTED = [bool](
    $env:BRAINSTEM_REPO_URL -or
    $env:BRAINSTEM_REPO_REF -or
    $env:BRAINSTEM_VERSION_URL
)
$REPO_URL = if ($env:BRAINSTEM_REPO_URL) { $env:BRAINSTEM_REPO_URL } else { "https://github.com/microsoft/aibast-agents-library.git" }
$REPO_REF = if ($env:BRAINSTEM_REPO_REF) { $env:BRAINSTEM_REPO_REF } else { "main" }
$REMOTE_VERSION_URL = if ($env:BRAINSTEM_VERSION_URL) { $env:BRAINSTEM_VERSION_URL } else { "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/rapp_brainstem/VERSION" }
$VENV_DIR = "$env:USERPROFILE\.brainstem\venv"
$NO_LAUNCH = $false

# Optional version pin: `--version vX.Y.Z` (also accepts a bare 0.6.14 or the release
# tag form brainstem-v0.6.14). Parsed from the script arguments so a user can pin or
# RC-test a specific release on Windows, e.g.
#   & ([scriptblock]::Create((irm https://.../install.ps1))) --version v0.6.14
$PIN_VERSION = ""
$argList = @($args)
for ($i = 0; $i -lt $argList.Count; $i++) {
    if ($argList[$i] -eq "--version" -and ($i + 1) -lt $argList.Count) {
        $PIN_VERSION = [string]$argList[$i + 1]
        $i++
    } elseif ($argList[$i] -eq "--no-launch") {
        $NO_LAUNCH = $true
    }
}

function Print-Banner {
    Write-Host ""
    Write-Host "  RAPP Brainstem" -ForegroundColor Cyan
    Write-Host "  Local-first AI agent server" -ForegroundColor Gray
    Write-Host "  Powered by GitHub Copilot - no API keys needed" -ForegroundColor Gray
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
        Write-Host "  [!] Could not check remote version - upgrading anyway" -ForegroundColor Yellow
        return $true
    }

    Write-Host "  Local version:  $localVersion" -ForegroundColor Cyan
    Write-Host "  Remote version: $remoteVersion" -ForegroundColor Cyan

    if ($SOURCE_OVERRIDE_REQUESTED) {
        Write-Host "  [..] Refreshing the explicitly requested repository/ref" -ForegroundColor Yellow
        return $true
    }

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
    Write-Host "       This can take several minutes; winget progress will appear below." -ForegroundColor Gray
    winget install --id $PackageId --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity --silent 2>&1 |
        ForEach-Object { Write-Host "       $_" }
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

function Get-VenvPython {
    # Path to the venv interpreter (Windows layout: venv\Scripts\python.exe).
    return "$VENV_DIR\Scripts\python.exe"
}

function Resolve-RunPython {
    # The interpreter used to install deps, check deps, and launch the server: the
    # venv python when it exists (issue #29 — install and launch must resolve the
    # SAME interpreter), otherwise the system python as a safe fallback.
    $venvPy = Get-VenvPython
    if (Test-Path $venvPy) { return $venvPy }
    return (Resolve-PythonExe)
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

    Write-Host "  [..] Python has no pip - bootstrapping via ensurepip..." -ForegroundColor Yellow
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

    Write-Host "  [..] ensurepip unavailable - fetching get-pip.py..." -ForegroundColor Yellow
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

function Setup-Venv {
    # Create ~/.brainstem/venv so dependencies are isolated from system/user Python
    # and the launcher always resolves the SAME interpreter that install used
    # (issue #29). Idempotent: a healthy existing venv is reused; a broken one is
    # recreated. Mirrors install.sh's setup_venv.
    $venvPy = Get-VenvPython
    if (Test-Path $venvPy) {
        $prev = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        & $venvPy -c "import sys" 2>&1 | Out-Null
        $ok = ($LASTEXITCODE -eq 0)
        $ErrorActionPreference = $prev
        if ($ok) {
            Write-Host "  [OK] Virtual environment OK" -ForegroundColor Green
            return
        }
        Write-Host "  [..] Virtual environment broken - recreating..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $VENV_DIR -ErrorAction SilentlyContinue
    }

    $sysPy = Resolve-PythonExe
    Write-Host "  Creating Python virtual environment (this can take a minute)..."
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & $sysPy -m venv $VENV_DIR 2>&1 | Out-Null
    if (-not (Test-Path (Get-VenvPython))) {
        # Some minimal Python installs need ensurepip primed before venv works.
        & $sysPy -m ensurepip --upgrade 2>&1 | Out-Null
        & $sysPy -m venv $VENV_DIR 2>&1 | Out-Null
    }
    $ErrorActionPreference = $prev

    if (-not (Test-Path (Get-VenvPython))) {
        Write-Host "  [X] Failed to create virtual environment at $VENV_DIR" -ForegroundColor Red
        throw "venv creation failed"
    }

    Write-Host "  [OK] Virtual environment ready" -ForegroundColor Green
}

function Check-Prerequisites {
    Write-Host "Checking prerequisites..."

    # winget (ships with Windows 11)
    try {
        winget --version 2>&1 | Out-Null
    } catch {
        Write-Host "  [X] winget not found - this installer requires Windows 10 1709+ or Windows 11" -ForegroundColor Red
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
            Write-Host "  [X] Git install failed - install manually from https://git-scm.com" -ForegroundColor Red
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
            Write-Host "  [X] Python install failed - install from https://python.org" -ForegroundColor Red
            Write-Host "      Make sure to check 'Add Python to PATH' during install" -ForegroundColor Yellow
            throw "Python 3.11+ install failed"
        }
    }

    # Store the working python command for later use
    $script:PythonExe = $pythonCmd

    # GitHub CLI is optional. Do not add another winget/UAC wait to the critical
    # path: Brainstem has its own browser device-code flow and can start without gh.
    try {
        gh --version 2>&1 | Out-Null
        Write-Host "  [OK] GitHub CLI available" -ForegroundColor Green
    } catch {
        Write-Host "  [..] GitHub CLI not found (optional - browser sign-in will be used)" -ForegroundColor Gray
    }
}

# ── soul refresh on upgrade (issue #40) ──────────────────────────────────────────
# Normalized SHA-256 of a soul.md, computed IDENTICALLY to rapp_brainstem/tests/soul_hash.py
# so the shipped soul_defaults.sha256 manifest works for both installers. Normalize:
# strip a UTF-8 BOM, CRLF->LF, strip trailing space/tab per line, exactly one trailing
# newline; then Get-FileHash a UTF-8 (no BOM) temp copy. Returns lowercase hex, or $null
# if the file cannot be read/decoded (the caller then preserves the soul untouched).
function Get-NormalizedSoulHash {
    param([string]$Path)
    try {
        # ReadAllText(UTF8) auto-detects and strips a UTF-8 BOM, matching soul_hash.py.
        $text = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    } catch { return $null }
    $text = $text.Replace("`r`n", "`n").Replace("`r", "`n")
    $lines = $text.Split([char]10)
    for ($i = 0; $i -lt $lines.Length; $i++) {
        $lines[$i] = $lines[$i].TrimEnd([char]32, [char]9)
    }
    $text = [string]::Join([string][char]10, $lines).TrimEnd([char]10) + [string][char]10
    $tmp = [System.IO.Path]::GetTempFileName()
    try {
        [System.IO.File]::WriteAllText($tmp, $text, (New-Object System.Text.UTF8Encoding($false)))
        return (Get-FileHash -Path $tmp -Algorithm SHA256).Hash.ToLower()
    } catch {
        return $null
    } finally {
        Remove-Item $tmp -Force -ErrorAction SilentlyContinue
    }
}

# True if $Hash is the first token of some non-comment line in the manifest.
function Test-SoulHashInManifest {
    param([string]$Hash, [string]$ManifestPath)
    if (-not $Hash) { return $false }
    if (-not (Test-Path $ManifestPath)) { return $false }
    foreach ($line in [System.IO.File]::ReadAllLines($ManifestPath)) {
        $trimmed = $line.Trim()
        if ($trimmed -eq "" -or $trimmed.StartsWith("#")) { continue }
        if (($trimmed -split '\s+')[0].ToLower() -eq $Hash.ToLower()) { return $true }
    }
    return $false
}

function Resolve-PinnedTag {
    # Resolve a --version pin against every tag form we ship: the documented v0.6.14
    # UX, a bare 0.6.14, and the actual release tag brainstem-v0.6.14. Returns the
    # matching git ref, or $null. Assumes the current directory is the repo.
    param([string]$Pin)
    $bare = $Pin -replace '^v', ''
    foreach ($cand in @($Pin, "v$bare", "brainstem-$bare", "brainstem-v$bare")) {
        $prev = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        git rev-parse $cand 2>&1 | Out-Null
        $ok = ($LASTEXITCODE -eq 0)
        $ErrorActionPreference = $prev
        if ($ok) { return $cand }
    }
    return $null
}

function Enable-BrainstemSparseCheckout {
    param([string]$RepoPath)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    Push-Location $RepoPath
    try {
        git sparse-checkout init --cone 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { return $false }
        git sparse-checkout set rapp_brainstem 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { return $false }
        git config remote.origin.promisor true 2>&1 | Out-Null
        git config remote.origin.partialclonefilter blob:none 2>&1 | Out-Null
        return ($LASTEXITCODE -eq 0)
    } finally {
        Pop-Location
        $ErrorActionPreference = $prev
    }
}

function Test-BrainstemSourceReady {
    param([string]$RepoPath)
    $runtime = Join-Path $RepoPath "rapp_brainstem"
    return (
        (Test-Path (Join-Path $runtime "brainstem.py")) -and
        (Test-Path (Join-Path $runtime "requirements.txt")) -and
        (Test-Path (Join-Path $runtime "VERSION"))
    )
}

function Repair-BrainstemSource {
    param([string]$RepoPath)
    $repairPath = "$RepoPath-repair-$(Get-Random)"
    $oldPath = "$RepoPath-broken-$(Get-Random)"
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        Write-Host "  [..] Existing checkout is incomplete - downloading a clean Brainstem copy..." -ForegroundColor Yellow
        git clone --progress --filter=blob:none --sparse --depth 1 --single-branch --no-tags --branch $REPO_REF $REPO_URL $repairPath 2>&1 |
            ForEach-Object { Write-Host "$_" }
        if ($LASTEXITCODE -ne 0) { return $false }
        if (-not (Enable-BrainstemSparseCheckout $repairPath)) { return $false }

        if ($PIN_VERSION) {
            Push-Location $repairPath
            try {
                git fetch --filter=blob:none --tags --quiet origin 2>&1 | Out-Null
                if ($LASTEXITCODE -ne 0) { return $false }
                $repairTag = Resolve-PinnedTag $PIN_VERSION
                if (-not $repairTag) { return $false }
                git checkout --quiet $repairTag 2>&1 | Out-Null
                if ($LASTEXITCODE -ne 0) { return $false }
            } finally {
                Pop-Location
            }
        }

        if (-not (Test-BrainstemSourceReady $repairPath)) { return $false }
        Move-Item $RepoPath $oldPath -ErrorAction Stop
        try {
            Move-Item $repairPath $RepoPath -ErrorAction Stop
        } catch {
            Move-Item $oldPath $RepoPath -ErrorAction SilentlyContinue
            return $false
        }
        Remove-Item -Recurse -Force $oldPath -ErrorAction SilentlyContinue
        Write-Host "  [OK] Clean sparse repair completed" -ForegroundColor Green
        return $true
    } finally {
        if (Test-Path $repairPath) {
            Remove-Item -Recurse -Force $repairPath -ErrorAction SilentlyContinue
        }
        $ErrorActionPreference = $prev
    }
}

function Install-Brainstem {
    Write-Host ""
    Write-Host "Installing RAPP Brainstem..."

    if (-not (Test-Path $BRAINSTEM_HOME)) {
        New-Item -ItemType Directory -Force -Path $BRAINSTEM_HOME | Out-Null
    }

    if (Test-Path "$BRAINSTEM_HOME\src\.git") {
        Write-Host "  Limiting the install source to the Brainstem runtime..."
        if (-not (Enable-BrainstemSparseCheckout "$BRAINSTEM_HOME\src")) {
            throw "Git 2.25+ is required for the lightweight Brainstem checkout"
        }
        Write-Host "  [OK] Solution bundles excluded from installer updates" -ForegroundColor Green

        # Smart update — preserve soul, agents, config
        $LocalVer = "0.0.0"
        $VerFile = "$BRAINSTEM_HOME\src\rapp_brainstem\VERSION"
        if (Test-Path $VerFile) { $LocalVer = (Get-Content $VerFile -Raw).Trim() }
        if ($PIN_VERSION) {
            $RemoteVer = ($PIN_VERSION -replace '^v', '')
        } else {
            try { $RemoteVer = (Invoke-WebRequest -Uri $REMOTE_VERSION_URL -UseBasicParsing -TimeoutSec 5).Content.Trim() } catch { $RemoteVer = "0.0.0" }
        }

        Write-Host "  Local:  v$LocalVer"
        if ($PIN_VERSION) {
            Write-Host "  Target: v$RemoteVer (pinned)"
        } else {
            Write-Host "  Remote: v$RemoteVer"
        }

        if (
            ($LocalVer -eq $RemoteVer) -and
            (Test-BrainstemSourceReady "$BRAINSTEM_HOME\src") -and
            (-not $SOURCE_OVERRIDE_REQUESTED)
        ) {
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
            if (Test-Path "$BRAINSTEM_HOME\src\rapp_brainstem\.brainstem_data") {
                Copy-Item "$BRAINSTEM_HOME\src\rapp_brainstem\.brainstem_data" "$Backup\.brainstem_data" -Recurse -Force
            }
            foreach ($stateFile in @(
                ".copilot_token", ".copilot_session", ".copilot_pending",
                ".brainstem_model", ".brainstem_book.json", ".brainstem_secret",
                "voice.zip"
            )) {
                $statePath = "$BRAINSTEM_HOME\src\rapp_brainstem\$stateFile"
                if (Test-Path $statePath) { Copy-Item $statePath "$Backup\$stateFile" -Force }
            }
            Write-Host "  [OK] Backed up soul, agents, config" -ForegroundColor Green

            # Pull latest from THIS installer's repo. A prior install may have cloned from a
            # different origin (fork/mirror); repoint origin and hard-reset to it so the upgrade
            # is reliable even across unrelated histories. User files (soul, agents, .env) were
            # backed up above and are restored below; tokens and .brainstem_data are gitignored.
            Push-Location "$BRAINSTEM_HOME\src"
            $prevEAP = $ErrorActionPreference
            $ErrorActionPreference = 'Continue'
            git remote set-url origin $REPO_URL 2>&1 | Out-Null
            $TagRef = $null
            if ($PIN_VERSION) {
                # Pin/RC-test: fetch tags and check out the requested release tag
                # (accepts v0.6.14 / 0.6.14 / brainstem-v0.6.14 forms like install.sh).
                git stash 2>&1 | Out-Null
                git fetch --filter=blob:none --tags --quiet origin 2>&1 | Out-Null
                $TagRef = Resolve-PinnedTag $PIN_VERSION
                $pullOk = $false
                if ($TagRef) {
                    git checkout --quiet $TagRef 2>&1 | Out-Null
                    $pullOk = ($LASTEXITCODE -eq 0)
                } else {
                    Write-Host "  [X] Version $PIN_VERSION not found. Available versions:" -ForegroundColor Red
                    git tag -l 'brainstem-v*' 'v*' 2>&1 | Sort-Object | ForEach-Object { Write-Host "    $_" }
                }
            } else {
                git fetch --filter=blob:none --quiet origin $REPO_REF 2>&1 | Out-Null
                $pullOk = ($LASTEXITCODE -eq 0)
                if ($pullOk) {
                    git reset --hard --quiet FETCH_HEAD 2>&1 | Out-Null
                    $pullOk = ($LASTEXITCODE -eq 0)
                }
            }
            $ErrorActionPreference = $prevEAP
            Pop-Location
            if ($PIN_VERSION -and -not $TagRef) {
                throw "pinned version $PIN_VERSION not found"
            }
            if ((-not $pullOk) -and (-not (Test-BrainstemSourceReady "$BRAINSTEM_HOME\src"))) {
                $pullOk = Repair-BrainstemSource "$BRAINSTEM_HOME\src"
            }
            if ($pullOk) {
                if ($PIN_VERSION) {
                    Write-Host "  [OK] Checked out $TagRef" -ForegroundColor Green
                } else {
                    Write-Host "  [OK] Framework updated" -ForegroundColor Green
                }
            } else {
                Write-Host "  [!] Update download failed - keeping existing files (v$LocalVer)" -ForegroundColor Yellow
            }

            # Restore user files.
            # soul.md: refresh it only when the pre-upgrade file was an unmodified
            # historical default (issue #40) — its normalized hash is in the manifest
            # AND the new default differs; then back the old one up to soul.md.bak-<date>.
            # Otherwise (any customization, or anything we cannot hash) preserve it
            # byte-for-byte. Fail-safe: preserve, never clobber.
            if (Test-Path "$Backup\soul.md") {
                $soulRefreshed = $false
                if ($pullOk) {
                    $Manifest = "$BRAINSTEM_HOME\src\rapp_brainstem\tests\soul_defaults.sha256"
                    $OldHash = Get-NormalizedSoulHash "$Backup\soul.md"
                    $NewHash = Get-NormalizedSoulHash $SoulFile
                    if ($OldHash -and $NewHash -and ($OldHash -ne $NewHash) -and (Test-SoulHashInManifest $OldHash $Manifest)) {
                        $Bak = "$BRAINSTEM_HOME\src\rapp_brainstem\soul.md.bak-$(Get-Date -Format 'yyyyMMdd')"
                        # Don't clobber an earlier same-day backup (a second refresh on the same date).
                        if (Test-Path $Bak) {
                            $bn = 1
                            while (Test-Path "$Bak-$bn") { $bn++ }
                            $Bak = "$Bak-$bn"
                        }
                        Copy-Item "$Backup\soul.md" $Bak
                        Write-Host "  [OK] Refreshed default soul (yours was an unmodified default); backup at $Bak" -ForegroundColor Green
                        $soulRefreshed = $true
                    }
                }
                if (-not $soulRefreshed) { Copy-Item "$Backup\soul.md" $SoulFile -Force }
            }
            if (Test-Path "$Backup\.env") { Copy-Item "$Backup\.env" $EnvFile -Force }
            if (Test-Path "$Backup\.brainstem_data") {
                $dataTarget = "$BRAINSTEM_HOME\src\rapp_brainstem\.brainstem_data"
                New-Item -ItemType Directory -Force -Path $dataTarget | Out-Null
                Get-ChildItem "$Backup\.brainstem_data" -Force -ErrorAction SilentlyContinue |
                    Copy-Item -Destination $dataTarget -Recurse -Force
            }
            foreach ($stateFile in @(
                ".copilot_token", ".copilot_session", ".copilot_pending",
                ".brainstem_model", ".brainstem_book.json", ".brainstem_secret",
                "voice.zip"
            )) {
                if (Test-Path "$Backup\$stateFile") {
                    Copy-Item "$Backup\$stateFile" "$BRAINSTEM_HOME\src\rapp_brainstem\$stateFile" -Force
                }
            }
            # Only restore genuinely user-added agents. Compute the set the repo now
            # ships from the fresh checkout and skip-restore anything in it — otherwise
            # bundled agents (context_memory, manage_memory, hacker_news) get reverted
            # to the backed-up copies on every upgrade (issue #2).
            $Shipped = @()
            if (Test-Path $AgentsDir) {
                $Shipped = @(Get-ChildItem "$AgentsDir\*.py" -ErrorAction SilentlyContinue | ForEach-Object { $_.Name })
            }
            Get-ChildItem "$Backup\*.py" -ErrorAction SilentlyContinue | ForEach-Object {
                if ($_.Name -notin @("basic_agent.py", "__init__.py")) {
                    if ($_.Name -in $Shipped) {
                        $recovery = "$BRAINSTEM_HOME\recovery\agent-collisions-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
                        New-Item -ItemType Directory -Force -Path $recovery | Out-Null
                        Copy-Item $_.FullName "$recovery\$($_.Name)" -Force
                        Write-Host "  [!] Preserved custom-agent name collision at $recovery\$($_.Name)" -ForegroundColor Yellow
                    } else {
                        Copy-Item $_.FullName "$AgentsDir\$($_.Name)" -Force
                    }
                }
            }
            Remove-Item -Recurse -Force $Backup -ErrorAction SilentlyContinue
            if ((-not $pullOk) -and $SOURCE_OVERRIDE_REQUESTED) {
                throw "Could not refresh the requested repository/ref; existing files were restored"
            }
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
        # A broken prior install (src present but .git gone) may still hold the user's
        # soul, .env, custom agents, and memories — none of which are in git. Preserve
        # them before wiping so a re-run can't silently destroy the user's work
        # (issue #21). The common case (no existing src) skips all of this.
        $FreshBackup = $null
        $srcRapp = "$BRAINSTEM_HOME\src\rapp_brainstem"
        if (Test-Path $srcRapp) {
            $FreshBackup = "$env:TEMP\brainstem-fresh-$(Get-Random)"
            New-Item -ItemType Directory -Force -Path "$FreshBackup\agents" | Out-Null
            if (Test-Path "$srcRapp\soul.md") { Copy-Item "$srcRapp\soul.md" "$FreshBackup\soul.md" -Force -ErrorAction SilentlyContinue }
            if (Test-Path "$srcRapp\.env") { Copy-Item "$srcRapp\.env" "$FreshBackup\.env" -Force -ErrorAction SilentlyContinue }
            if (Test-Path "$srcRapp\agents") { Copy-Item "$srcRapp\agents\*.py" "$FreshBackup\agents\" -Force -ErrorAction SilentlyContinue }
            if (Test-Path "$srcRapp\.brainstem_data") { Copy-Item "$srcRapp\.brainstem_data" "$FreshBackup\.brainstem_data" -Recurse -Force -ErrorAction SilentlyContinue }
            foreach ($stateFile in @(
                ".copilot_token", ".copilot_session", ".copilot_pending",
                ".brainstem_model", ".brainstem_book.json", ".brainstem_secret",
                "voice.zip"
            )) {
                if (Test-Path "$srcRapp\$stateFile") {
                    Copy-Item "$srcRapp\$stateFile" "$FreshBackup\$stateFile" -Force -ErrorAction SilentlyContinue
                }
            }
        }

        $SourceStage = "$BRAINSTEM_HOME\src-fresh-$PID"
        $OldSource = $null
        Remove-Item -Recurse -Force $SourceStage -ErrorAction SilentlyContinue
        Write-Host "  Downloading only the Brainstem runtime; solution ZIPs stay in the web library."
        $prevEAP = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        git clone --progress --filter=blob:none --sparse --depth 1 --single-branch --no-tags --branch $REPO_REF $REPO_URL $SourceStage 2>&1 |
            ForEach-Object { Write-Host "$_" }
        $cloneOk = ($LASTEXITCODE -eq 0)
        $ErrorActionPreference = $prevEAP
        if (-not $cloneOk) {
            Remove-Item -Recurse -Force $SourceStage -ErrorAction SilentlyContinue
            if ($FreshBackup) { Remove-Item -Recurse -Force $FreshBackup -ErrorAction SilentlyContinue }
            Write-Host "  [X] Failed to clone repository" -ForegroundColor Red
            Write-Host "  Existing files were left untouched." -ForegroundColor Yellow
            throw "Git 2.25+ is required for the lightweight Brainstem checkout"
        }
        if (-not (Enable-BrainstemSparseCheckout $SourceStage)) {
            Remove-Item -Recurse -Force $SourceStage -ErrorAction SilentlyContinue
            if ($FreshBackup) { Remove-Item -Recurse -Force $FreshBackup -ErrorAction SilentlyContinue }
            throw "failed to limit the checkout to rapp_brainstem/"
        }

        if ($PIN_VERSION) {
            # Pin/RC-test: check out the requested release tag after cloning
            # (accepts v0.6.14 / 0.6.14 / brainstem-v0.6.14 forms like install.sh).
            Push-Location $SourceStage
            $prevEAP = $ErrorActionPreference
            $ErrorActionPreference = 'Continue'
            git fetch --filter=blob:none --tags --quiet origin 2>&1 | Out-Null
            $TagRef = Resolve-PinnedTag $PIN_VERSION
            if ($TagRef) {
                git checkout --quiet $TagRef 2>&1 | Out-Null
            } else {
                Write-Host "  [X] Version $PIN_VERSION not found. Available versions:" -ForegroundColor Red
                git tag -l 'brainstem-v*' 'v*' 2>&1 | Sort-Object | ForEach-Object { Write-Host "    $_" }
            }
            $ErrorActionPreference = $prevEAP
            Pop-Location
            if (-not $TagRef) {
                Remove-Item -Recurse -Force $SourceStage -ErrorAction SilentlyContinue
                if ($FreshBackup) { Remove-Item -Recurse -Force $FreshBackup -ErrorAction SilentlyContinue }
                throw "pinned version $PIN_VERSION not found"
            }
            Write-Host "  [OK] Checked out $TagRef" -ForegroundColor Green
        }
        if (-not (Test-BrainstemSourceReady $SourceStage)) {
            Remove-Item -Recurse -Force $SourceStage -ErrorAction SilentlyContinue
            if ($FreshBackup) { Remove-Item -Recurse -Force $FreshBackup -ErrorAction SilentlyContinue }
            throw "downloaded Brainstem source is incomplete"
        }
        if (Test-Path "$BRAINSTEM_HOME\src") {
            $OldSource = "$BRAINSTEM_HOME\src-broken-$PID"
            Remove-Item -Recurse -Force $OldSource -ErrorAction SilentlyContinue
            Move-Item "$BRAINSTEM_HOME\src" $OldSource
        }
        try {
            Move-Item $SourceStage "$BRAINSTEM_HOME\src"
        } catch {
            if ($OldSource -and (Test-Path $OldSource)) {
                Move-Item $OldSource "$BRAINSTEM_HOME\src" -ErrorAction SilentlyContinue
            }
            Remove-Item -Recurse -Force $SourceStage -ErrorAction SilentlyContinue
            if ($FreshBackup) { Remove-Item -Recurse -Force $FreshBackup -ErrorAction SilentlyContinue }
            throw
        }

        # Restore any preserved user files over the fresh checkout.
        if ($FreshBackup) {
            $AgentsDir = "$BRAINSTEM_HOME\src\rapp_brainstem\agents"
            $FreshShipped = @()
            if (Test-Path $AgentsDir) {
                $FreshShipped = @(Get-ChildItem "$AgentsDir\*.py" -ErrorAction SilentlyContinue | ForEach-Object { $_.Name })
            }
            if (Test-Path "$FreshBackup\soul.md") { Copy-Item "$FreshBackup\soul.md" "$BRAINSTEM_HOME\src\rapp_brainstem\soul.md" -Force -ErrorAction SilentlyContinue }
            if (Test-Path "$FreshBackup\.env") { Copy-Item "$FreshBackup\.env" "$BRAINSTEM_HOME\src\rapp_brainstem\.env" -Force -ErrorAction SilentlyContinue }
            Get-ChildItem "$FreshBackup\agents\*.py" -ErrorAction SilentlyContinue | ForEach-Object {
                if ($_.Name -notin @("basic_agent.py", "__init__.py")) {
                    if ($_.Name -in $FreshShipped) {
                        $recovery = "$BRAINSTEM_HOME\recovery\agent-collisions-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
                        New-Item -ItemType Directory -Force -Path $recovery | Out-Null
                        Copy-Item $_.FullName "$recovery\$($_.Name)" -Force
                        Write-Host "  [!] Preserved custom-agent name collision at $recovery\$($_.Name)" -ForegroundColor Yellow
                    } else {
                        Copy-Item $_.FullName "$AgentsDir\$($_.Name)" -Force -ErrorAction SilentlyContinue
                    }
                }
            }
            if (Test-Path "$FreshBackup\.brainstem_data") { Copy-Item "$FreshBackup\.brainstem_data" "$BRAINSTEM_HOME\src\rapp_brainstem\.brainstem_data" -Recurse -Force -ErrorAction SilentlyContinue }
            foreach ($stateFile in @(
                ".copilot_token", ".copilot_session", ".copilot_pending",
                ".brainstem_model", ".brainstem_book.json", ".brainstem_secret",
                "voice.zip"
            )) {
                if (Test-Path "$FreshBackup\$stateFile") {
                    Copy-Item "$FreshBackup\$stateFile" "$BRAINSTEM_HOME\src\rapp_brainstem\$stateFile" -Force -ErrorAction SilentlyContinue
                }
            }
            Remove-Item -Recurse -Force $FreshBackup -ErrorAction SilentlyContinue
            Write-Host "  [OK] Preserved your soul, agents, memories, and config" -ForegroundColor Green
        }
        if ($OldSource) {
            Remove-Item -Recurse -Force $OldSource -ErrorAction SilentlyContinue
        }
    }
    if (-not (Test-BrainstemSourceReady "$BRAINSTEM_HOME\src")) {
        throw "Brainstem source is incomplete after install; rapp_brainstem\brainstem.py is missing"
    }
    Write-Host "  [OK] Source code ready" -ForegroundColor Green
}

function Run-PipInstall {
    $reqFile = "$BRAINSTEM_HOME\src\rapp_brainstem\requirements.txt"
    # Install into the venv (issue #29). The venv created by Setup-Venv already ships
    # pip; only the rare system-python fallback (no venv) needs pip bootstrapping.
    $py = Resolve-RunPython
    if (-not (Test-PipWorks $py)) {
        if (-not (Ensure-Pip)) { return }
        $py = Resolve-RunPython
    }
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
        Write-Host "  [..] Installing Python packages; pip progress will appear below." -ForegroundColor Yellow
        & $py -m pip install --progress-bar on --disable-pip-version-check -r $reqFile 2>&1 |
            ForEach-Object { Write-Host "$_" }
        # `--user` is only valid (and only needed) on the system-python fallback; it
        # errors inside a venv, so skip it when installing into the venv.
        if ($LASTEXITCODE -ne 0 -and $py -ne (Get-VenvPython)) {
            & $py -m pip install --progress-bar on --disable-pip-version-check -r $reqFile --user 2>&1 |
                ForEach-Object { Write-Host "$_" }
        }
    } finally {
        $ErrorActionPreference = $prev
    }
}

function Check-PythonDeps {
    $py = Resolve-RunPython
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
        Write-Host "  [..] Dependency check failed - retrying pip install once..." -ForegroundColor Yellow
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

function Ensure-Dependencies {
    # Quick import check — only run pip when something is actually missing (mirrors
    # install.sh's ensure_deps; keeps the fast path from hitting PyPI every launch).
    Push-Location "$BRAINSTEM_HOME\src\rapp_brainstem"
    if (Check-PythonDeps) {
        Pop-Location
        Write-Host "  [OK] Dependencies verified" -ForegroundColor Green
        return
    }
    Write-Host "  [..] Missing dependencies - installing..." -ForegroundColor Yellow
    Run-PipInstall
    $ok = Check-PythonDeps
    Pop-Location
    if (-not $ok) {
        throw "Python dependencies are missing and could not be installed (see messages above)"
    }
    Write-Host "  [OK] Dependencies installed" -ForegroundColor Green
}

function Install-CLI {
    Write-Host ""
    Write-Host "Installing CLI..."

    if (-not (Test-Path $BRAINSTEM_BIN)) {
        New-Item -ItemType Directory -Force -Path $BRAINSTEM_BIN | Out-Null
    }

    # Wrappers launch the venv interpreter (issue #29) so `brainstem` always runs the
    # same Python that install set up; if the venv is ever missing they fall back to
    # the system Python captured here. Quote every interpreter path — the direct-path
    # fallback (…\First Last\AppData\…\python.exe) contains spaces.
    $venvPy = Get-VenvPython
    $sysPy = Resolve-PythonExe
    # Batch wrapper (works in cmd.exe and PowerShell). A goto (not an if/else block)
    # avoids cmd.exe mis-parsing a path that happens to contain a parenthesis.
    $cmdContent = @"
@echo off
cd /d "$BRAINSTEM_HOME\src\rapp_brainstem"
if exist "$venvPy" goto RAPP_VENV
"$sysPy" brainstem.py %*
goto :eof
:RAPP_VENV
"$venvPy" brainstem.py %*
"@
    Set-Content -Path "$BRAINSTEM_BIN\brainstem.cmd" -Value $cmdContent

    # PowerShell wrapper
    $psContent = @"
Set-Location "$BRAINSTEM_HOME\src\rapp_brainstem"
if (Test-Path "$venvPy") { & "$venvPy" brainstem.py @args } else { & "$sysPy" brainstem.py @args }
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
    # Main/Install-Brainstem already handles source updates. Do not pull again here:
    # legacy full checkouts can download unrelated library changes indefinitely even
    # after the version check established that the Brainstem runtime is current.

    # Dependencies before launch: if they cannot be installed, fail now rather than
    # opening a browser against a server that never bound port 7071.
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

    # Authentication belongs to the running server and browser UI. Performing the
    # device-code flow here kept port 7071 unavailable for up to five silent minutes
    # when GitHub was blocked or the browser step was missed.
    Write-Host ""
    Write-Host "  Starting RAPP Brainstem..." -ForegroundColor Cyan
    Write-Host "  Setup is complete. Keep this terminal open while Brainstem is running." -ForegroundColor Green
    Write-Host "  The browser will handle GitHub sign-in if it is needed." -ForegroundColor Gray
    Write-Host "  Press Ctrl+C to stop the server." -ForegroundColor Gray
    Write-Host ""

    Push-Location "$BRAINSTEM_HOME\src\rapp_brainstem"

    # Free port 7071 before launching — an upgrade must not leave the OLD server
    # running, or the health poll below would pass against it and report a false
    # success while the new code never actually binds the port. Guarded for the
    # absence of Get-NetTCPConnection (older/Server SKUs).
    try {
        $listeners = Get-NetTCPConnection -LocalPort 7071 -State Listen -ErrorAction SilentlyContinue
        if ($listeners) {
            $ownerPids = @($listeners | ForEach-Object { $_.OwningProcess } | Sort-Object -Unique)
            foreach ($ownerPid in $ownerPids) {
                if ($ownerPid -and $ownerPid -ne 0) {
                    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $ownerPid" -ErrorAction SilentlyContinue
                    $commandLine = if ($process) { [string]$process.CommandLine } else { "" }
                    if ($commandLine -match 'brainstem\.py' -or $commandLine -like "*$BRAINSTEM_HOME*") {
                        Write-Host "  [!] Stopping existing Brainstem server (PID $ownerPid)..." -ForegroundColor Yellow
                        Stop-Process -Id $ownerPid -Force -ErrorAction SilentlyContinue
                    } else {
                        throw "Port 7071 is already used by another process (PID $ownerPid). Stop it or set PORT in $BRAINSTEM_HOME\src\rapp_brainstem\.env."
                    }
                }
            }
            Start-Sleep -Seconds 1
        }
    } catch {
        if ($_.Exception.Message -like 'Port 7071 is already used*') {
            Pop-Location
            throw
        }
    }

    # Open the browser once the server actually answers (#14) — a fixed delay
    # races cold startups and lands the user on a dead-port error page. Poll
    # /health, then open; after 60s open anyway so the user still gets the tab.
    Start-Job -ScriptBlock {
        for ($i = 0; $i -lt 60; $i++) {
            try {
                Invoke-WebRequest -Uri "http://localhost:7071/health" -UseBasicParsing -TimeoutSec 1 | Out-Null
                break
            } catch {
                Start-Sleep -Seconds 1
            }
        }
        Start-Process "http://localhost:7071"
    } | Out-Null

    $py = Resolve-RunPython
    & $py brainstem.py
}

function Main {
    Print-Banner

    if ($PIN_VERSION) {
        Write-Host "  Pinning to version: $PIN_VERSION" -ForegroundColor Cyan
        Write-Host ""
    }

    # Check if this is an upgrade of an existing install. Skip the fast path when a
    # version is pinned — Install-Brainstem must run to check out the requested tag.
    if ((-not $PIN_VERSION) -and (Test-Path "$BRAINSTEM_HOME\src\.git")) {
        Write-Host "Checking for updates..."
        if (-not (Check-ForUpgrade)) {
            # Already up to date — still re-heal the environment before launching,
            # exactly like install.sh's fast path: verify prerequisites, the venv and
            # deps, rewrite the CLI wrappers, and restore a missing .env (issues #9, #3).
            Check-Prerequisites
            Setup-Venv
            Ensure-Dependencies
            Install-CLI
            Create-Env
            if ($NO_LAUNCH) {
                Write-Host "  [OK] Brainstem runtime is ready (launch skipped)" -ForegroundColor Green
                return
            }
            Launch-Brainstem
            return
        }
    }

    Check-Prerequisites
    Install-Brainstem
    # Create the venv before the CLI wrappers (which point at it) and before deps
    # (which install into it) so install and launch share one interpreter (issue #29).
    Setup-Venv
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

    if ($NO_LAUNCH) {
        Write-Host "  [OK] Brainstem runtime is ready (launch skipped)" -ForegroundColor Green
        return
    }

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
