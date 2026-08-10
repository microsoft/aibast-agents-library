@echo off
setlocal EnableExtensions EnableDelayedExpansion
title RAPP Brainstem Beta Installer

set "BRAINSTEM_HOME=%USERPROFILE%\.brainstem"
set "BETA_HOME=%BRAINSTEM_HOME%\beta-launcher"
set "BETA_SOURCE=%BETA_HOME%\src"
set "REPO_URL=https://github.com/microsoft/aibast-agents-library.git"
set "REPO_REF=main"
set "REPO_COMMIT="
set "NODE_VERSION=24.19.0"
set "BOOTSTRAP_URL=https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1"

if defined BRAINSTEM_BETA_HOME set "BETA_HOME=%BRAINSTEM_BETA_HOME%"
if defined BRAINSTEM_BETA_REPO_URL set "REPO_URL=%BRAINSTEM_BETA_REPO_URL%"
if defined BRAINSTEM_BETA_REF set "REPO_REF=%BRAINSTEM_BETA_REF%"
if defined BRAINSTEM_BETA_COMMIT set "REPO_COMMIT=%BRAINSTEM_BETA_COMMIT%"
if defined BRAINSTEM_BETA_NODE_VERSION set "NODE_VERSION=%BRAINSTEM_BETA_NODE_VERSION%"
if defined BRAINSTEM_BETA_BOOTSTRAP_URL set "BOOTSTRAP_URL=%BRAINSTEM_BETA_BOOTSTRAP_URL%"
set "BETA_SOURCE=%BETA_HOME%\src"

echo.
echo RAPP Brainstem Beta Launcher
echo Skill Recorder-style desktop launch over the shared global Brainstem
echo.

if defined REPO_COMMIT (
  powershell.exe -NoProfile -Command "if ($env:BRAINSTEM_BETA_COMMIT -notmatch '^[0-9a-fA-F]{40}$') { exit 1 }"
  if errorlevel 1 (
    echo [X] BRAINSTEM_BETA_COMMIT must be a full 40-character commit SHA.
    exit /b 1
  )
  set "REPO_REF=%REPO_COMMIT%"
)

where curl.exe >nul 2>&1 || (
  echo [X] Windows curl.exe is required.
  exit /b 1
)

if not exist "%BETA_HOME%" mkdir "%BETA_HOME%"
set "BOOTSTRAP=%TEMP%\rapp-brainstem-bootstrap-%RANDOM%.ps1"
echo [..] Preparing the shared global Brainstem...
curl.exe -fL --progress-bar "%BOOTSTRAP_URL%" -o "%BOOTSTRAP%"
if errorlevel 1 goto :fail
if /i not "%REPO_URL%"=="https://github.com/microsoft/aibast-agents-library.git" (
  set "GIT_CONFIG_COUNT=1"
  set "GIT_CONFIG_KEY_0=url.%REPO_URL%.insteadOf"
  set "GIT_CONFIG_VALUE_0=https://github.com/microsoft/aibast-agents-library.git"
)
if defined REPO_COMMIT (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%BOOTSTRAP%" --no-launch --version "%REPO_COMMIT%"
) else (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%BOOTSTRAP%" --no-launch
)
set "BOOTSTRAP_EXIT=%ERRORLEVEL%"
del /q "%BOOTSTRAP%" >nul 2>&1
if not "%BOOTSTRAP_EXIT%"=="0" goto :fail

set "GIT_EXE="
for /f "delims=" %%G in ('where git.exe 2^>nul') do if not defined GIT_EXE set "GIT_EXE=%%G"
if not defined GIT_EXE if exist "%ProgramFiles%\Git\cmd\git.exe" set "GIT_EXE=%ProgramFiles%\Git\cmd\git.exe"
if not defined GIT_EXE (
  echo [X] Git was not available after the Brainstem bootstrap.
  goto :fail
)

echo.
echo [..] Downloading only the beta launcher source...
if exist "%BETA_SOURCE%\.git" (
  "%GIT_EXE%" -C "%BETA_SOURCE%" remote set-url origin "%REPO_URL%"
  if errorlevel 1 goto :fail
  "%GIT_EXE%" -C "%BETA_SOURCE%" sparse-checkout init --cone
  if errorlevel 1 goto :fail
  "%GIT_EXE%" -C "%BETA_SOURCE%" sparse-checkout set beta
  if errorlevel 1 goto :fail
  "%GIT_EXE%" -C "%BETA_SOURCE%" config remote.origin.promisor true
  "%GIT_EXE%" -C "%BETA_SOURCE%" config remote.origin.partialclonefilter blob:none
  "%GIT_EXE%" -C "%BETA_SOURCE%" fetch --progress --filter=blob:none --depth 1 origin "%REPO_REF%"
  if errorlevel 1 goto :fail
  "%GIT_EXE%" -C "%BETA_SOURCE%" reset --hard FETCH_HEAD
  if errorlevel 1 goto :fail
) else (
  if exist "%BETA_SOURCE%" move "%BETA_SOURCE%" "%BETA_SOURCE%.incomplete.%RANDOM%" >nul
  "%GIT_EXE%" init "%BETA_SOURCE%"
  if errorlevel 1 goto :fail
  "%GIT_EXE%" -C "%BETA_SOURCE%" remote add origin "%REPO_URL%"
  if errorlevel 1 goto :fail
  "%GIT_EXE%" -C "%BETA_SOURCE%" sparse-checkout init --cone
  if errorlevel 1 goto :fail
  "%GIT_EXE%" -C "%BETA_SOURCE%" sparse-checkout set beta
  if errorlevel 1 goto :fail
  "%GIT_EXE%" -C "%BETA_SOURCE%" config remote.origin.promisor true
  "%GIT_EXE%" -C "%BETA_SOURCE%" config remote.origin.partialclonefilter blob:none
  "%GIT_EXE%" -C "%BETA_SOURCE%" fetch --progress --filter=blob:none --depth 1 origin "%REPO_REF%"
  if errorlevel 1 goto :fail
  "%GIT_EXE%" -C "%BETA_SOURCE%" reset --hard FETCH_HEAD
  if errorlevel 1 goto :fail
)
if defined REPO_COMMIT (
  set "ACTUAL_COMMIT="
  for /f "delims=" %%H in ('"%GIT_EXE%" -C "%BETA_SOURCE%" rev-parse HEAD') do set "ACTUAL_COMMIT=%%H"
  if /i not "!ACTUAL_COMMIT!"=="%REPO_COMMIT%" (
    echo [X] Beta checkout resolved to !ACTUAL_COMMIT! instead of %REPO_COMMIT%.
    goto :fail
  )
)
if not exist "%BETA_SOURCE%\beta\package.json" (
  echo [X] beta\package.json is missing from %REPO_REF%.
  goto :fail
)
if exist "%BETA_SOURCE%\solutions" (
  echo [X] Solution bundles leaked into the beta checkout.
  goto :fail
)
echo [OK] Beta checkout excludes the solution library.

set "NODE_PLATFORM=win-x64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "NODE_PLATFORM=win-arm64"
set "NODE_ARCHIVE=node-v%NODE_VERSION%-%NODE_PLATFORM%.zip"
set "NODE_DIR=%BETA_HOME%\node-v%NODE_VERSION%-%NODE_PLATFORM%"
set "CACHE=%BETA_HOME%\cache"
if not exist "%CACHE%" mkdir "%CACHE%"

if not exist "%NODE_DIR%\node.exe" (
  echo.
  echo [..] Downloading portable Node.js v%NODE_VERSION%...
  curl.exe -fL --progress-bar "https://nodejs.org/dist/v%NODE_VERSION%/SHASUMS256.txt" -o "%CACHE%\SHASUMS256.txt"
  if errorlevel 1 goto :fail
  curl.exe -fL --progress-bar "https://nodejs.org/dist/v%NODE_VERSION%/%NODE_ARCHIVE%" -o "%CACHE%\%NODE_ARCHIVE%"
  if errorlevel 1 goto :fail

  set "EXPECTED_HASH="
  for /f "tokens=1" %%H in ('findstr /i /c:" %NODE_ARCHIVE%" "%CACHE%\SHASUMS256.txt"') do set "EXPECTED_HASH=%%H"
  set "ACTUAL_HASH="
  for /f "skip=1 tokens=* delims=" %%H in ('certutil -hashfile "%CACHE%\%NODE_ARCHIVE%" SHA256') do if not defined ACTUAL_HASH set "ACTUAL_HASH=%%H"
  set "ACTUAL_HASH=!ACTUAL_HASH: =!"
  if not defined EXPECTED_HASH (
    echo [X] Node.js checksum entry was not found.
    goto :fail
  )
  if /i not "!ACTUAL_HASH!"=="!EXPECTED_HASH!" (
    echo [X] Node.js archive checksum mismatch.
    goto :fail
  )
  tar.exe -xf "%CACHE%\%NODE_ARCHIVE%" -C "%BETA_HOME%"
  if errorlevel 1 goto :fail
)
if not exist "%NODE_DIR%\node.exe" (
  echo [X] Portable Node.js extraction failed.
  goto :fail
)
echo [OK] Portable Node.js verified.

echo.
echo [..] Installing Electron and the bundled GitHub Copilot CLI...
set "npm_config_cache=%BETA_HOME%\npm-cache"
call "%NODE_DIR%\npm.cmd" ci --prefix "%BETA_SOURCE%\beta" --no-audit --no-fund
if errorlevel 1 goto :fail
call "%NODE_DIR%\npm.cmd" --prefix "%BETA_SOURCE%\beta" run check
if errorlevel 1 goto :fail
call "%NODE_DIR%\npm.cmd" --prefix "%BETA_SOURCE%\beta" test
if errorlevel 1 goto :fail

set "ELECTRON_EXE=%BETA_SOURCE%\beta\node_modules\electron\dist\electron.exe"
if not exist "%ELECTRON_EXE%" (
  echo [X] Electron runtime is missing.
  goto :fail
)

set "LAUNCHER=%BETA_HOME%\launch.cmd"
> "%LAUNCHER%" echo @echo off
>>"%LAUNCHER%" echo start "" "%ELECTRON_EXE%" "%BETA_SOURCE%\beta"

cscript.exe //nologo "%BETA_SOURCE%\beta\scripts\create-windows-shortcuts.js" "%ELECTRON_EXE%" "%BETA_SOURCE%\beta"
if errorlevel 1 goto :fail

echo.
echo [OK] RAPP Brainstem Beta is installed.
echo      Mainline and beta share: %BRAINSTEM_HOME%
echo      Use the RAPP Brainstem Beta desktop or Start Menu shortcut.
echo.
if not "%BRAINSTEM_BETA_NO_LAUNCH%"=="1" start "" "%ELECTRON_EXE%" "%BETA_SOURCE%\beta"
exit /b 0

:fail
echo.
echo [X] RAPP Brainstem Beta installation failed.
echo     Review the error above and re-run this installer.
exit /b 1
