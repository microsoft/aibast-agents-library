# Rapid prototyping on the Brainstem the one-liner installed (Windows). Nothing else to install.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Home2 = if ($env:BRAINSTEM_HOME) { $env:BRAINSTEM_HOME } else { Join-Path $env:USERPROFILE ".brainstem" }
$Kernel = Join-Path $Home2 "src\rapp_brainstem\brainstem.py"
$Py = Join-Path $Home2 "venv\Scripts\python.exe"
$BsPort = if ($env:BS_PORT) { $env:BS_PORT } else { "7096" }; $AppPort = if ($env:APP_PORT) { $env:APP_PORT } else { "7097" }
if (-not (Test-Path $Kernel) -or -not (Test-Path $Py)) { Write-Host "No Brainstem found at $Home2. Run the Brainstem one-liner first."; exit 1 }
New-Item -ItemType Directory -Force -Path (Join-Path $Root "out") | Out-Null
function Up($url) { try { Invoke-RestMethod -TimeoutSec 2 $url | Out-Null; $true } catch { $false } }
if (-not (Up "http://localhost:$BsPort/health")) {
  $env:PORT = $BsPort; $env:AGENTS_PATH = Join-Path $Root "brainstem\agents"; $env:PM_BRAINSTEM_URL = "http://localhost:$BsPort"
  Start-Process -FilePath $Py -ArgumentList "`"$Kernel`"" -WindowStyle Hidden -RedirectStandardOutput (Join-Path $Root "out\brainstem.log") -RedirectStandardError (Join-Path $Root "out\brainstem.err")
  1..40 | ForEach-Object { if (Up "http://localhost:$BsPort/health") { return }; Start-Sleep 1 }
}
if (-not (Up "http://localhost:$AppPort/api/health")) {
  $env:PM_BRAINSTEM_URL = "http://localhost:$BsPort"
  Start-Process -FilePath $Py -ArgumentList "-m app.server --port $AppPort" -WorkingDirectory $Root -WindowStyle Hidden -RedirectStandardOutput (Join-Path $Root "out\app.log") -RedirectStandardError (Join-Path $Root "out\app.err")
  1..10 | ForEach-Object { if (Up "http://localhost:$AppPort/api/health") { return }; Start-Sleep 1 }
}
Write-Host "App: http://localhost:$AppPort"
Start-Process "http://localhost:$AppPort"
