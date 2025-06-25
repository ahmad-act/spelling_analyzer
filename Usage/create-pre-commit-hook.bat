@echo off
REM Create .git\hooks\pre-commit file with spelling-analyzer script

setlocal

REM Get current directory
set "CUR_DIR=%cd%"
set "HOOK_PATH=%CUR_DIR%\.git\hooks\pre-commit"

REM Create hooks folder if it doesn't exist
if not exist ".git\hooks" (
    echo Git not initialized in this folder. Run 'git init' first.
    exit /b 1
)

REM Write the shell script into pre-commit
(
    echo #!/bin/sh
    echo.
    echo echo "Running spelling-analyzer on current project..."
    echo.
    echo spelling-analyzer "." --output "./spelling_report.json" --fail-on code,comment
    echo RESULT=$?
    echo.
    echo if [ $RESULT -ne 0 ]; then
    echo ^  echo "spelling-analyzer detected issues in codes or comments."
    echo ^  echo "Commit aborted. Please fix the spelling issues."
    echo ^  exit 1
    echo fi
    echo.
    echo exit 0
) > "%HOOK_PATH%"

REM Confirm creation
if exist "%HOOK_PATH%" (
    echo.
    echo ✅ pre-commit hook successfully created at:
    echo    "%HOOK_PATH%"
    echo.
    echo You can close this window now. It will close automatically in 9 seconds...
    
    REM Countdown
    for /l %%i in (15,-1,1) do (
        echo Closing in %%i...
        timeout /t 1 > nul
    )
) else (
    echo ❌ Failed to create the hook file.
)

endlocal
exit
