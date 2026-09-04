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
$StateFile = Join-Path $StateDir "state.json"
$SecretFile = Join-Path $StateDir "gateway.secret"
$RuntimeConfig = Join-Path $StateDir "runtime-config.js"
$KernelOut = Join-Path $StateDir "kernel.out.log"
$KernelErr = Join-Path $StateDir "kernel.err.log"
$GatewayOut = Join-Path $StateDir "gateway.out.log"
$GatewayErr = Join-Path $StateDir "gateway.err.log"
$GatewayScript = Join-Path $PSScriptRoot "scout_gateway_agent.py"
$WorkspacePage = Join-Path $PSScriptRoot "workspace.html"

function Get-StartupFile {
    $startupDir = [Environment]::GetFolderPath("Startup")
    if (-not $startupDir) {
        throw "The current user Startup folder is unavailable."
    }
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.Encoding]::UTF8.GetBytes($Workspace.ToLowerInvariant())
        $suffix = ([BitConverter]::ToString($sha.ComputeHash($bytes))).
            Replace("-", "").
            Substring(0, 12)
    } finally {
        $sha.Dispose()
    }
    return Join-Path $startupDir "RAPP-Scout-Brainstem-$suffix.cmd"
}

function Install-Startup {
    $startupFile = Get-StartupFile
    $escapedController = $PSCommandPath.Replace("'", "''")
    $command = "& '$escapedController' start"
    $encodedCommand = [Convert]::ToBase64String(
        [Text.Encoding]::Unicode.GetBytes($command)
    )
    $content = @(
        "@echo off",
        "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -EncodedCommand $encodedCommand"
    ) -join "`r`n"
    Set-Content -LiteralPath $startupFile -Value $content -Encoding ASCII
    Write-Output "Scout Brainstem startup installed at $startupFile"
}

function Uninstall-Startup {
    $startupFile = Get-StartupFile
    Remove-Item -LiteralPath $startupFile -Force -ErrorAction SilentlyContinue
    Write-Output "Scout Brainstem startup removed from $startupFile"
}

function Get-State {
    if (-not (Test-Path -LiteralPath $StateFile)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json
    } catch {
        throw "Scout state file is invalid: $($_.Exception.Message)"
    }
}

function Get-WorkspaceVersion {
    $versionFile = Join-Path $Workspace "VERSION"
    if (-not (Test-Path -LiteralPath $versionFile)) {
        return "0.0.0"
    }
    return (Get-Content -LiteralPath $versionFile -Raw).Trim()
}

function Get-GatewayHash {
    if (-not (Test-Path -LiteralPath $GatewayScript)) {
        return ""
    }
    return (Get-FileHash -LiteralPath $GatewayScript -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-OrCreateGatewaySecret {
    if (Test-Path -LiteralPath $SecretFile) {
        $existing = (Get-Content -LiteralPath $SecretFile -Raw).Trim()
        if ($existing.Length -ge 32) {
            return $existing
        }
    }

    New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
    $bytes = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $rng.GetBytes($bytes)
    } finally {
        $rng.Dispose()
    }
    $secret = [Convert]::ToBase64String($bytes).
        TrimEnd("=").
        Replace("+", "-").
        Replace("/", "_")
    Set-Content -LiteralPath $SecretFile -Value $secret -NoNewline -Encoding ASCII
    return $secret
}

function Write-RuntimeConfig([int]$GatewayPort, [string]$Secret) {
    $config = [ordered]@{
        url = "http://127.0.0.1:$GatewayPort"
        secret = $Secret
    } | ConvertTo-Json -Compress
    Set-Content -LiteralPath $RuntimeConfig `
        -Value "window.__SCOUT_BRAINSTEM__ = $config;" `
        -NoNewline `
        -Encoding UTF8
}

function Resolve-Python {
    $candidates = @()
    $managed = Join-Path $HOME ".brainstem\venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $managed) {
        $candidates += $managed
    }
    try {
        $launcher = & py -3 -c "import sys; print(sys.executable)" 2>$null |
            Select-Object -First 1
        if ($launcher) {
            $candidates += $launcher
        }
    } catch {}
    $candidates += @("python", "python3")

    foreach ($candidate in $candidates) {
        try {
            & $candidate -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return [string]$candidate
            }
        } catch {}
    }
    throw "Python 3.11+ is unavailable. Run the official Brainstem installer first."
}

function Test-PortFree([int]$Port) {
    $listener = $null
    try {
        $listener = [Net.Sockets.TcpListener]::new(
            [Net.IPAddress]::Loopback,
            $Port
        )
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

function Find-FreePort([int]$Preferred, [int[]]$Excluded = @()) {
    for ($port = $Preferred; $port -le ($Preferred + 100); $port++) {
        if (($Excluded -contains $port) -or (-not (Test-PortFree $port))) {
            continue
        }
        return $port
    }
    throw "No free loopback port found from $Preferred through $($Preferred + 100)."
}

function Get-ConfiguredKernelPort {
    $envFile = Join-Path $Workspace ".env"
    if (Test-Path -LiteralPath $envFile) {
        $line = Get-Content -LiteralPath $envFile |
            Where-Object { $_ -match "^\s*PORT\s*=\s*(\d+)\s*$" } |
            Select-Object -Last 1
        if ($line -and $line -match "(\d+)") {
            return [Math]::Max(7072, [int]$Matches[1])
        }
    }
    return 7072
}

function Get-KernelHealth([int]$Port) {
    try {
        return Invoke-RestMethod `
            -Uri "http://127.0.0.1:$Port/health" `
            -TimeoutSec 2
    } catch {
        return $null
    }
}

function Get-GatewayHealth([int]$Port, [string]$Secret) {
    try {
        return Invoke-RestMethod `
            -Uri "http://127.0.0.1:$Port/_scout/health" `
            -Headers @{ "X-Scout-Gateway-Secret" = $Secret } `
            -TimeoutSec 2
    } catch {
        return $null
    }
}

function Test-ProcessRunning($ProcessId) {
    if (-not $ProcessId) {
        return $false
    }
    return [bool](Get-Process -Id ([int]$ProcessId) -ErrorAction SilentlyContinue)
}

function Get-ListenerPid([int]$Port) {
    $listener = Get-NetTCPConnection `
        -LocalAddress "127.0.0.1" `
        -LocalPort $Port `
        -State Listen `
        -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if (-not $listener) {
        throw "No loopback listener owns port $Port."
    }
    return [int]$listener.OwningProcess
}

function Test-RecordedProcess(
    $State,
    [string]$Role,
    [bool]$RequireListener = $true
) {
    $pidProperty = "${Role}_pid"
    $startProperty = "${Role}_started_at"
    $executableProperty = "${Role}_executable"
    $portProperty = "${Role}_port"
    $signatureProperty = "${Role}_signature"
    $processId = $State.$pidProperty
    if (-not $processId) {
        return $null
    }
    $process = Get-Process -Id ([int]$processId) -ErrorAction SilentlyContinue
    if (-not $process) {
        return $null
    }

    try {
        $recordedStart = [DateTime]::Parse([string]$State.$startProperty).
            ToUniversalTime()
        $actualStart = $process.StartTime.ToUniversalTime()
        if ([Math]::Abs(($actualStart - $recordedStart).TotalSeconds) -gt 2) {
            Write-Warning "Refusing to stop recycled $Role PID $processId."
            return $null
        }
        $recordedExecutable = [IO.Path]::GetFullPath(
            [string]$State.$executableProperty
        )
        $actualExecutable = [IO.Path]::GetFullPath($process.Path)
        if ($recordedExecutable -ne $actualExecutable) {
            Write-Warning "Refusing to stop $Role PID $processId with a different executable."
            return $null
        }
        $command = Get-CimInstance Win32_Process `
            -Filter "ProcessId = $processId" `
            -ErrorAction Stop
        if (
            -not $command -or
            -not ([string]$command.CommandLine).Contains(
                [string]$State.$signatureProperty
            )
        ) {
            Write-Warning "Refusing to stop $Role PID $processId with a different command."
            return $null
        }
        if ($RequireListener) {
            $listener = Get-NetTCPConnection `
                -LocalAddress "127.0.0.1" `
                -LocalPort ([int]$State.$portProperty) `
                -State Listen `
                -ErrorAction SilentlyContinue |
                Where-Object { $_.OwningProcess -eq [int]$processId } |
                Select-Object -First 1
            if (-not $listener) {
                Write-Warning "Refusing to stop $Role PID $processId without its recorded listener."
                return $null
            }
        }
        return $process
    } catch {
        Write-Warning "Could not verify recorded $Role PID ${processId}: $($_.Exception.Message)"
        return $null
    }
}

function Stop-RecordedProcesses($State) {
    if (-not $State) {
        return
    }
    foreach ($role in @("gateway", "kernel")) {
        $process = Test-RecordedProcess $State $role
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
}

function Save-State(
    [int]$GatewayPort,
    [int]$KernelPort
) {
    $gatewayProcess = Get-Process -Id (Get-ListenerPid $GatewayPort) -ErrorAction Stop
    $kernelProcess = Get-Process -Id (Get-ListenerPid $KernelPort) -ErrorAction Stop
    [ordered]@{
        schema = "rapp-scout-overlay/1"
        workspace = $Workspace
        gateway_pid = $GatewayProcess.Id
        gateway_port = $GatewayPort
        gateway_url = "http://127.0.0.1:$GatewayPort"
        gateway_started_at = $GatewayProcess.StartTime.ToUniversalTime().ToString("o")
        gateway_executable = $GatewayProcess.Path
        gateway_signature = $GatewayScript
        gateway_sha256 = (Get-GatewayHash)
        kernel_pid = $KernelProcess.Id
        kernel_port = $KernelPort
        kernel_url = "http://127.0.0.1:$KernelPort"
        kernel_started_at = $KernelProcess.StartTime.ToUniversalTime().ToString("o")
        kernel_executable = $KernelProcess.Path
        kernel_signature = "brainstem.py"
        version = (Get-WorkspaceVersion)
        started_at = [DateTime]::UtcNow.ToString("o")
    } | ConvertTo-Json | Set-Content -LiteralPath $StateFile -Encoding UTF8
}

function Get-ExistingOverlay {
    $state = Get-State
    if (
        -not $state -or
        [string]$state.version -ne (Get-WorkspaceVersion) -or
        [string]$state.gateway_sha256 -ne (Get-GatewayHash) -or
        -not (Test-ProcessRunning $state.gateway_pid) -or
        -not (Test-ProcessRunning $state.kernel_pid)
    ) {
        return $null
    }
    $secret = Get-OrCreateGatewaySecret
    $gateway = Get-GatewayHealth ([int]$state.gateway_port) $secret
    $kernel = Get-KernelHealth ([int]$state.kernel_port)
    if (
        -not $gateway -or
        $gateway.status -ne "ok" -or
        [string]$gateway.workspace -ne $Workspace -or
        -not $kernel -or
        $kernel.status -notin @("ok", "unauthenticated")
    ) {
        return $null
    }
    Write-RuntimeConfig ([int]$state.gateway_port) $secret
    return [pscustomobject]@{
        state = $state
        gateway = $gateway
        kernel = $kernel
    }
}

function Wait-Kernel(
    [int]$Port,
    [Diagnostics.Process]$Process,
    [int]$Attempts = 120
) {
    for ($attempt = 0; $attempt -lt $Attempts; $attempt++) {
        Start-Sleep -Milliseconds 500
        $health = Get-KernelHealth $Port
        if ($health -and $health.status -in @("ok", "unauthenticated")) {
            return $health
        }
        if ($Process.HasExited) {
            break
        }
    }
    $details = @()
    if (Test-Path -LiteralPath $KernelOut) {
        $details += Get-Content -LiteralPath $KernelOut -Tail 80
    }
    if (Test-Path -LiteralPath $KernelErr) {
        $details += Get-Content -LiteralPath $KernelErr -Tail 80
    }
    throw "Brainstem kernel failed to become healthy.`n$($details -join [Environment]::NewLine)"
}

function Wait-Gateway(
    [int]$Port,
    [string]$Secret,
    [Diagnostics.Process]$Process,
    [int]$Attempts = 60
) {
    for ($attempt = 0; $attempt -lt $Attempts; $attempt++) {
        Start-Sleep -Milliseconds 250
        $health = Get-GatewayHealth $Port $Secret
        if ($health -and $health.status -eq "ok") {
            return $health
        }
        if ($Process.HasExited) {
            break
        }
    }
    $details = @()
    if (Test-Path -LiteralPath $GatewayOut) {
        $details += Get-Content -LiteralPath $GatewayOut -Tail 80
    }
    if (Test-Path -LiteralPath $GatewayErr) {
        $details += Get-Content -LiteralPath $GatewayErr -Tail 80
    }
    throw "Scout gateway failed to become healthy.`n$($details -join [Environment]::NewLine)"
}

function Start-Overlay {
    if (-not (Test-Path -LiteralPath $GatewayScript)) {
        throw "Scout gateway component is missing at $GatewayScript"
    }
    if (-not (Test-Path -LiteralPath $WorkspacePage)) {
        throw "Scout workspace page is missing at $WorkspacePage"
    }

    New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
    $existing = Get-ExistingOverlay
    if ($existing) {
        return $existing
    }

    $stale = Get-State
    Stop-RecordedProcesses $stale
    Remove-Item -LiteralPath $StateFile -Force -ErrorAction SilentlyContinue
    Remove-Item $KernelOut, $KernelErr, $GatewayOut, $GatewayErr `
        -Force `
        -ErrorAction SilentlyContinue

    $gatewayPreferred = if ($env:SCOUT_BRAINSTEM_GATEWAY_PORT) {
        [int]$env:SCOUT_BRAINSTEM_GATEWAY_PORT
    } else {
        7071
    }
    $gatewayPort = Find-FreePort $gatewayPreferred
    $kernelPort = Find-FreePort (Get-ConfiguredKernelPort) @($gatewayPort)
    $secret = Get-OrCreateGatewaySecret
    $python = Resolve-Python

    $globalState = Join-Path $HOME ".brainstem\src\rapp_brainstem"
    foreach ($name in @(".copilot_token", ".copilot_session")) {
        $source = Join-Path $globalState $name
        $target = Join-Path $Workspace $name
        if ((Test-Path -LiteralPath $source) -and (-not (Test-Path -LiteralPath $target))) {
            Copy-Item -LiteralPath $source -Destination $target
        }
    }

    $kernelProcess = $null
    $gatewayProcess = $null
    $oldPort = $env:PORT
    $oldUtf8 = $env:PYTHONUTF8
    $oldUnbuffered = $env:PYTHONUNBUFFERED
    try {
        $env:PORT = [string]$kernelPort
        $env:PYTHONUTF8 = "1"
        $env:PYTHONUNBUFFERED = "1"
        $kernelProcess = Start-Process `
            -FilePath $python `
            -ArgumentList "brainstem.py" `
            -WorkingDirectory $Workspace `
            -RedirectStandardOutput $KernelOut `
            -RedirectStandardError $KernelErr `
            -WindowStyle Hidden `
            -PassThru
    } finally {
        $env:PORT = $oldPort
        $env:PYTHONUTF8 = $oldUtf8
        $env:PYTHONUNBUFFERED = $oldUnbuffered
    }

    try {
        $kernelHealth = Wait-Kernel $kernelPort $kernelProcess
        $gatewayArguments = @(
            "`"$GatewayScript`"",
            "--port", [string]$gatewayPort,
            "--upstream-port", [string]$kernelPort,
            "--secret-file", "`"$SecretFile`"",
            "--workspace", "`"$Workspace`""
        ) -join " "
        $gatewayProcess = Start-Process `
            -FilePath $python `
            -ArgumentList $gatewayArguments `
            -WorkingDirectory $Workspace `
            -RedirectStandardOutput $GatewayOut `
            -RedirectStandardError $GatewayErr `
            -WindowStyle Hidden `
            -PassThru
        $gatewayHealth = Wait-Gateway $gatewayPort $secret $gatewayProcess

        Save-State `
            $gatewayPort `
            $kernelPort
        Write-RuntimeConfig $gatewayPort $secret
        return [pscustomobject]@{
            state = Get-State
            gateway = $gatewayHealth
            kernel = $kernelHealth
        }
    } catch {
        foreach ($process in @($gatewayProcess, $kernelProcess)) {
            if ($process -and -not $process.HasExited) {
                Stop-Process -Id $process.Id -ErrorAction SilentlyContinue
            }
        }
        throw
    }
}

function Stop-Overlay {
    $state = Get-State
    Stop-RecordedProcesses $state
    Remove-Item -LiteralPath $StateFile -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $RuntimeConfig -Force -ErrorAction SilentlyContinue
    Write-Output "Scout Brainstem overlay stopped."
}

function Get-OverlayStatus {
    $overlay = Get-ExistingOverlay
    if (-not $overlay) {
        return [ordered]@{
            status = "stopped"
            schema = "rapp-scout-overlay/1"
            workspace = $Workspace
        }
    }
    return [ordered]@{
        status = "running"
        schema = $overlay.state.schema
        version = $overlay.kernel.version
        auth = $overlay.kernel.status
        model = $overlay.kernel.model
        agents = $overlay.kernel.agents
        gateway_pid = $overlay.state.gateway_pid
        gateway_port = $overlay.state.gateway_port
        gateway_url = $overlay.state.gateway_url
        kernel_pid = $overlay.state.kernel_pid
        kernel_port = $overlay.state.kernel_port
        kernel_url = $overlay.state.kernel_url
        workspace = $Workspace
        workspace_page = $WorkspacePage
    }
}

switch ($Action) {
    "start" {
        $overlay = Start-Overlay
        Write-Output "Scout Brainstem ready at $($overlay.state.gateway_url)"
        Write-Output "Workspace page: $WorkspacePage"
    }
    "open" {
        $overlay = Start-Overlay
        Start-Process $overlay.state.gateway_url
        Write-Output "Opened $($overlay.state.gateway_url)"
    }
    "status" {
        Get-OverlayStatus | ConvertTo-Json -Depth 5
    }
    "stop" {
        Stop-Overlay
    }
    "install-startup" {
        Install-Startup
    }
    "uninstall-startup" {
        Uninstall-Startup
    }
}
