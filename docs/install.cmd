@echo off
REM RAPP Brainstem Installer for Windows CMD
REM Launches the PowerShell installer

echo.
echo   RAPP Brainstem Installer
echo   ========================
echo.
echo   Launching installer...
echo.

powershell -ExecutionPolicy Bypass -Command "& { irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1 | iex }"

if %ERRORLEVEL% neq 0 (
    echo.
    echo   Installation failed. Try running install.ps1 directly in PowerShell.
    echo.
    pause
    exit /b 1
)

echo.
echo   Installation complete!
echo   Open a new terminal and run: brainstem
echo.
pause
