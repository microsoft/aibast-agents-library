# start.ps1 — Windows launcher for RAPP Brainstem
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# TLS 1.2 for the get-pip.py fallback below — stock PS 5.1 on older builds
# negotiates TLS 1.0, which bootstrap.pypa.io refuses. Harmless elsewhere.
try {
    [Net.ServicePointManager]::SecurityProtocol = `
        [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
} catch {}

# Refresh PATH so newly-installed tools (gh, python) are found
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")

# Ensure UTF-8 output from Python
$env:PYTHONUTF8 = "1"

# Resolve a REAL Python 3 (not the Windows Store execution-alias stub, which is a
# valid "command" but only prints "Python was not found" and opens the Store).
$py = $null
foreach ($cmd in @("python", "python3")) {
    try {
        $out = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $out -match "Python 3\.") { $py = $cmd; break }
    } catch {}
}
if (-not $py) {
    Write-Host "ERROR: Python 3 not found on PATH. Install Python 3.11+ from https://python.org" -ForegroundColor Red
    Write-Host "       (Check 'Add Python to PATH' during install.)" -ForegroundColor Yellow
    exit 1
}

# Create .env from the example on first run (parity with start.sh).
if ((-not (Test-Path ".env")) -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
}

# Dependency check. Run under EAP=Continue: at the script's global EAP=Stop, a native
# command writing to stderr (which a missing import does) is promoted to a TERMINATING
# error on Windows PowerShell 5.1 and would abort the launcher before it could install.
function Test-Deps {
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $py -c "import flask, flask_cors, requests, dotenv" 2>$null
        return ($LASTEXITCODE -eq 0)
    } finally {
        $ErrorActionPreference = $prev
    }
}

if (-not (Test-Deps)) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    # The base Python may lack pip entirely (corp images, stripped installs) —
    # restore it before the first pip call, or every install below is guaranteed
    # "No module named pip" noise. Same chain as install.ps1's Ensure-Pip:
    # ensurepip (stdlib, offline) -> get-pip.py (network). The pip installs stay
    # inside this EAP=Continue scope too: on PS 5.1 with a redirected stderr,
    # pip's warnings would otherwise be promoted to a terminating error.
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $py -m pip --version 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Python has no pip — bootstrapping via ensurepip..." -ForegroundColor Yellow
            & $py -m ensurepip --upgrade --default-pip 2>&1 | ForEach-Object { Write-Host "$_" }
            & $py -m pip --version 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "ensurepip unavailable — fetching get-pip.py..." -ForegroundColor Yellow
                $getPip = Join-Path $env:TEMP "rapp-get-pip.py"
                try {
                    Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip -UseBasicParsing -TimeoutSec 120
                    & $py $getPip 2>&1 | ForEach-Object { Write-Host "$_" }
                } catch {}
                Remove-Item $getPip -Force -ErrorAction SilentlyContinue
            }
        }
        & $py -m pip install -r requirements.txt -q
        if (-not (Test-Deps)) {
            & $py -m pip install -r requirements.txt
        }
    } finally { $ErrorActionPreference = $prev }
}

if (-not (Test-Deps)) {
    Write-Host "ERROR: Python dependencies are missing and could not be installed." -ForegroundColor Red
    Write-Host "       Python at '$py' has no working pip (ensurepip and get-pip.py both failed)." -ForegroundColor Yellow
    Write-Host "       Reinstall Python from https://python.org with 'pip' checked, or run the" -ForegroundColor Yellow
    Write-Host "       installer one-liner, then try .\start.ps1 again." -ForegroundColor Yellow
    exit 1
}

# Check gh CLI (optional — the web login flow works without it)
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    Write-Host "gh CLI found — token will be auto-detected if you're logged in." -ForegroundColor Green
} else {
    Write-Host "gh CLI not found — you can authenticate via the web UI at http://localhost:7071" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting RAPP Brainstem..." -ForegroundColor Cyan
& $py brainstem.py
