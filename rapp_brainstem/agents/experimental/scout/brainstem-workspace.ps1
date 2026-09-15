param(
    [ValidateSet(
        "start",
        "stop",
        "status",
        "open",
        "install-startup",
        "uninstall-startup"
    )]
    [string]$Action = "start"
)

$ErrorActionPreference = "Stop"
$Workspace = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$StateDir = Join-Path $Workspace ".brainstem_data\scout"
$StateFile = Join-Path $StateDir "server.json"
$StdoutLog = Join-Path $StateDir "server.out.log"
$StderrLog = Join-Path $StateDir "server.err.log"
$SecretFile = Join-Path $Workspace ".brainstem_secret"
$PreviewConfig = Join-Path $PSScriptRoot "preview-config.js"

function Get-StartupFile {
    $startupDir = [Environment]::GetFolderPath("Startup")
    if (-not $startupDir) {
        throw "The current user Startup folder is unavailable."
    }
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.Encoding]::UTF8.GetBytes($Workspace.ToLowerInvariant())
        $suffix = ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").Substring(0, 12)
    } finally {
        $sha.Dispose()
    }
    return Join-Path $startupDir "RAPP-Brainstem-$suffix.cmd"
}

function Install-Startup {
    $startupFile = Get-StartupFile
    $controller = $PSCommandPath.Replace("%", "%%")
    $content = @(
        "@echo off",
        "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$controller`" start"
    ) -join "`r`n"
    Set-Content -LiteralPath $startupFile -Value $content -Encoding ASCII
    Write-Output "Brainstem startup installed at $startupFile"
}

function Uninstall-Startup {
    $startupFile = Get-StartupFile
    if (Test-Path $startupFile) {
        Remove-Item -LiteralPath $startupFile -Force
    }
    Write-Output "Brainstem startup removed from $startupFile"
}

function Get-OrCreateSecret {
    if (Test-Path $SecretFile) {
        $secret = (Get-Content $SecretFile -Raw).Trim()
        if ($secret) {
            return $secret
        }
    }
    $bytes = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $rng.GetBytes($bytes)
    } finally {
        $rng.Dispose()
    }
    $secret = [Convert]::ToBase64String($bytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
    Set-Content -LiteralPath $SecretFile -Value $secret -NoNewline -Encoding ASCII
    return $secret
}

function Write-PreviewConfig([int]$Port) {
    $secret = Get-OrCreateSecret
    $config = [ordered]@{
        url = "http://127.0.0.1:$Port/"
        secret = $secret
    } | ConvertTo-Json -Compress
    Set-Content -LiteralPath $PreviewConfig `
        -Value "window.__SCOUT_BRAINSTEM_PREVIEW__ = $config;" `
        -NoNewline `
        -Encoding UTF8
}

function Get-ConfiguredPort {
    $envFile = Join-Path $Workspace ".env"
    if (Test-Path $envFile) {
        $line = Get-Content $envFile | Where-Object { $_ -match "^\s*PORT\s*=\s*(\d+)\s*$" } |
            Select-Object -Last 1
        if ($line -and $line -match "(\d+)") {
            return [int]$Matches[1]
        }
    }
    return 7071
}

function Get-State {
    if (-not (Test-Path $StateFile)) {
        return $null
    }
    try {
        return Get-Content $StateFile -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-Health([int]$Port) {
    try {
        return Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2
    } catch {
        return $null
    }
}

function Get-ListenerPid([int]$Port) {
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($connection) {
        return [int]$connection.OwningProcess
    }
    return $null
}

function Save-State([int]$Port, $ProcessId, $LauncherPid) {
    $record = [ordered]@{
        schema = "scout-brainstem-workspace/1"
        pid = $ProcessId
        launcher_pid = $LauncherPid
        port = $Port
        url = "http://127.0.0.1:$Port"
        workspace = $Workspace
        started_at = [DateTime]::UtcNow.ToString("o")
    }
    $record | ConvertTo-Json | Set-Content -LiteralPath $StateFile -Encoding UTF8
}

function Test-WorkspaceHealth($Health) {
    if (-not $Health -or $Health.status -notin @("ok", "unauthenticated")) {
        return $false
    }
    try {
        return ([IO.Path]::GetFullPath([string]$Health.brainstem_dir).TrimEnd("\") -eq
            [IO.Path]::GetFullPath($Workspace).TrimEnd("\"))
    } catch {
        return $false
    }
}

function Test-PortFree([int]$Port) {
    $listener = $null
    try {
        $listener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        return $true
    } catch {
        return $false
    } finally {
        if ($listener) {
            $listener.Stop()
        }
    }
}

function Find-Port([int]$Preferred) {
    for ($port = $Preferred; $port -le ($Preferred + 100); $port++) {
        $health = Get-Health $port
        if (Test-WorkspaceHealth $health) {
            return $port
        }
        if (Test-PortFree $port) {
            return $port
        }
    }
    throw "No free localhost port found from $Preferred through $($Preferred + 100)."
}

function Resolve-Python {
    $managed = Join-Path $HOME ".brainstem\venv\Scripts\python.exe"
    if (Test-Path $managed) {
        return $managed
    }
    foreach ($candidate in @("python", "python3")) {
        try {
            & $candidate -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        } catch {}
    }
    throw "Python 3.11+ is unavailable. Run the official Brainstem installer first."
}

function Start-Brainstem {
    New-Item -ItemType Directory -Path $StateDir -Force | Out-Null

    $state = Get-State
    if ($state -and $state.port) {
        $health = Get-Health ([int]$state.port)
        if (Test-WorkspaceHealth $health) {
            Write-PreviewConfig ([int]$state.port)
            return [pscustomobject]@{
                port = [int]$state.port
                pid = Get-ListenerPid ([int]$state.port)
                health = $health
            }
        }
    }

    $preferredPort = Get-ConfiguredPort
    $port = Find-Port $preferredPort
    $health = Get-Health $port
    if (Test-WorkspaceHealth $health) {
        $listenerPid = Get-ListenerPid $port
        Save-State $port $listenerPid $null
        Write-PreviewConfig $port
        return [pscustomobject]@{
            port = $port
            pid = $listenerPid
            health = $health
        }
    }

    $python = Resolve-Python
    Remove-Item $StdoutLog, $StderrLog -Force -ErrorAction SilentlyContinue

    $globalState = Join-Path $HOME ".brainstem\src\rapp_brainstem"
    foreach ($name in @(".copilot_token", ".copilot_session")) {
        $source = Join-Path $globalState $name
        $target = Join-Path $Workspace $name
        if ((Test-Path $source) -and (-not (Test-Path $target))) {
            Copy-Item -LiteralPath $source -Destination $target
        }
    }

    $oldPort = $env:PORT
    $oldUtf8 = $env:PYTHONUTF8
    $oldUnbuffered = $env:PYTHONUNBUFFERED
    try {
        $env:PORT = [string]$port
        $env:PYTHONUTF8 = "1"
        $env:PYTHONUNBUFFERED = "1"
        $process = Start-Process -FilePath $python `
            -ArgumentList "brainstem.py" `
            -WorkingDirectory $Workspace `
            -RedirectStandardOutput $StdoutLog `
            -RedirectStandardError $StderrLog `
            -WindowStyle Hidden `
            -PassThru
    } finally {
        $env:PORT = $oldPort
        $env:PYTHONUTF8 = $oldUtf8
        $env:PYTHONUNBUFFERED = $oldUnbuffered
    }

    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        Start-Sleep -Milliseconds 500
        $health = Get-Health $port
        if (Test-WorkspaceHealth $health) {
            $listenerPid = Get-ListenerPid $port
            Save-State $port $listenerPid $process.Id
            Write-PreviewConfig $port
            return [pscustomobject]@{
                port = $port
                pid = $listenerPid
                health = $health
            }
        }
        if ($process.HasExited) {
            break
        }
    }

    $details = @()
    if (Test-Path $StdoutLog) {
        $details += Get-Content $StdoutLog
    }
    if (Test-Path $StderrLog) {
        $details += Get-Content $StderrLog
    }
    throw "Brainstem failed to become healthy.`n$($details -join [Environment]::NewLine)"
}

function Stop-Brainstem {
    $state = Get-State
    if (-not $state -or -not $state.pid) {
        Write-Output "Brainstem workspace process is not recorded."
        return
    }
    $processIds = @([int]$state.pid)
    if ($state.launcher_pid) {
        $processIds += [int]$state.launcher_pid
    }
    foreach ($processId in ($processIds | Select-Object -Unique)) {
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process) {
            try {
                Stop-Process -Id $process.Id -ErrorAction Stop
            } catch [Microsoft.PowerShell.Commands.ProcessCommandException] {
                if (Get-Process -Id $process.Id -ErrorAction SilentlyContinue) {
                    throw
                }
            }
        }
    }
    Remove-Item $StateFile -Force -ErrorAction SilentlyContinue
    Write-Output "Brainstem workspace process stopped."
}

switch ($Action) {
    "start" {
        $result = Start-Brainstem
        Write-Output "Brainstem healthy at http://127.0.0.1:$($result.port)"
    }
    "open" {
        $result = Start-Brainstem
        Write-Output "Brainstem ready at http://127.0.0.1:$($result.port)"
        Start-Sleep -Seconds 5
    }
    "status" {
        $result = Start-Brainstem
        [ordered]@{
            status = $result.health.status
            version = $result.health.version
            model = $result.health.model
            agents = $result.health.agents
            pid = $result.pid
            port = $result.port
            url = "http://127.0.0.1:$($result.port)"
            brainstem_dir = $result.health.brainstem_dir
        } | ConvertTo-Json -Depth 5
    }
    "stop" {
        Stop-Brainstem
    }
    "install-startup" {
        Install-Startup
    }
    "uninstall-startup" {
        Uninstall-Startup
    }
}
