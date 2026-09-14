---
name: aibast-staging-ring-test
version: 1.0.0
description: Test the AIBAST staging one-liner on this Windows device exactly as a user would, then report evidence. For GitHub Copilot on Windows.
homepage: https://kody-w.github.io/aibast-agents-library/
metadata: {"category":"release-engineering","repo":"https://github.com/kody-w/aibast-agents-library","ring":"staging"}
---

# AIBAST staging ring test (Windows)

You are testing the **staging** build of the AIBAST Agents Library Brainstem
before it is promoted to production. The staging one-liner is served from
https://kody-w.github.io/aibast-agents-library and installs the staging
branch of `kody-w/aibast-agents-library`. Nothing you do here touches the
production one-liner at microsoft.github.io.

The deliverable is an **evidence report**, not an opinion. Every step below
produces something to paste into the report. If a step fails, capture the
exact error text and continue with the steps that do not depend on it.

## Instructions for Copilot

Execute these steps autonomously in PowerShell. Pause only where marked ⏸.

### 1. Prerequisites

```powershell
$PSVersionTable.PSVersion
git --version
python --version
```

Python 3.11 or newer and Git must be present. If Python is missing, the
installer will try to help; note whatever it prints.

### 2. Choose the profile (⏸ ask the user)

Default to an **isolated profile** so the user's existing Brainstem, if any, is untouched:

```powershell
$env:USERPROFILE = Join-Path $env:TEMP 'aibast-ring-test'
New-Item -ItemType Directory -Force -Path $env:USERPROFILE | Out-Null
```

Ask the user only if they want the real install over their current profile
instead. The real install repoints `%USERPROFILE%\.brainstem\src` to the
staging branch and keeps their soul, agents, and token.

### 3. Fetch the staging installer and confirm its identity

```powershell
$installer = Invoke-WebRequest -Uri 'https://kody-w.github.io/aibast-agents-library/install.ps1' -UseBasicParsing
$content = $installer.Content
$content | Select-String -Pattern '^\$REPO_URL|^\$REPO_REF|^\$REMOTE_VERSION_URL'
```

Expected: the defaults name `https://github.com/kody-w/aibast-agents-library.git`
and `staging`. If they name `microsoft` or `main`, stop and report: the staging
Pages are serving the wrong identity.

### 4. Install without launching

```powershell
& ([scriptblock]::Create($content)) --no-launch *>&1 | Tee-Object -FilePath (Join-Path $env:USERPROFILE 'install.log')
```

Record the total time and the final lines of `install.log`.

### 5. Verify what was installed

```powershell
$src = Join-Path $env:USERPROFILE '.brainstem\src'
git -C $src remote get-url origin
git -C $src rev-parse --abbrev-ref HEAD
git -C $src rev-parse HEAD
Get-Content (Join-Path $src 'rapp_brainstem\VERSION')
Test-Path (Join-Path $env:USERPROFILE '.brainstem\venv\Scripts\python.exe')
Test-Path (Join-Path $env:USERPROFILE '.local\bin\brainstem.cmd')
```

Expected: origin is the `kody-w` fork, branch `staging`, all `Test-Path` lines `True`.
Compare the commit to the current staging head:

```powershell
(Invoke-RestMethod 'https://api.github.com/repos/kody-w/aibast-agents-library/commits/staging').sha
```

### 6. Start the server on a spare port

```powershell
$runtime = Join-Path $src 'rapp_brainstem'
$env:PORT = '7091'
$server = Start-Process -FilePath (Join-Path $env:USERPROFILE '.brainstem\venv\Scripts\python.exe') -ArgumentList 'brainstem.py' -WorkingDirectory $runtime -PassThru -RedirectStandardOutput (Join-Path $env:USERPROFILE 'server.log') -RedirectStandardError (Join-Path $env:USERPROFILE 'server.err')
Start-Sleep -Seconds 8
Invoke-RestMethod 'http://127.0.0.1:7091/health/public'
Invoke-RestMethod 'http://127.0.0.1:7091/health' | ConvertTo-Json -Depth 3
```

Expected: `/health/public` returns `status: ok` and `version: 0.6.16`;
`/health` lists loaded agents.

### 7. Sign in if needed, then chat

If `/health` shows no auth, open http://localhost:7091/login in a browser and
complete the GitHub device-code sign-in (⏸ the user must do this), or set
`$env:GITHUB_TOKEN` from `gh auth token` before starting the server.

```powershell
$body = @{ user_input = 'In one sentence, confirm you are running and name one tool you have available. Answer in under 40 words.'; conversation_history = @() } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:7091/chat' -ContentType 'application/json' -Body $body | Select-Object response, model
```

Expected: a one-sentence answer in the `response` field.

### 8. Stop the server and clean up

```powershell
Stop-Process -Id $server.Id -Force
```

Leave the isolated profile in place if the user may want to inspect it;
otherwise `Remove-Item -Recurse -Force $env:USERPROFILE`.

### 9. Report

Produce this table, then the raw error text for anything that failed:

| Check | Result |
|---|---|
| Device | Windows version, PowerShell version, Python version |
| Installer identity | repo / branch from step 3 |
| Install | exit status, seconds, last lines of `install.log` |
| Installed | origin, branch, commit, VERSION, staging head sha |
| `/health/public` | JSON |
| `/health` | status, model, agent count |
| `/chat` | the response text |
| Server log | first 10 lines of `server.log` and `server.err` |

⏸ Ask the user before filing. If anything failed, file it at
https://github.com/kody-w/aibast-agents-library/issues/new with the label
`post-release`, milestone **M2 Vendored one-liner on staging**, and the table
above. Do not file on the Microsoft repository; staging issues stay on the fork.
