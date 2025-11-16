@echo off
REM Assistant Response Hook - Enhanced with Thinking Verification
REM This hook runs after Claude completes a response

echo.
echo ================================================================
echo   [TASK COMPLETED] Claude Code Response Finished
echo ================================================================
echo.

REM Check if thinking enforcer exists and run it
set "THINKING_ENFORCER=%USERPROFILE%\.claude\scripts\thinking_enforcer.py"
set "RESPONSE_LOG=%USERPROFILE%\.claude\logs\last_response.txt"

if exist "%THINKING_ENFORCER%" (
    if exist "%RESPONSE_LOG%" (
        echo [VERIFICATION] Checking ULTRA THINK MODE compliance...
        echo.
        py "%THINKING_ENFORCER%" "%RESPONSE_LOG%" 2>nul

        if %ERRORLEVEL% EQU 0 (
            echo.
            echo [OK] Response includes proper thinking blocks
        ) else (
            echo.
            echo [VIOLATION] No thinking blocks detected!
            echo            Recording violation...
            py "%USERPROFILE%\.claude\scripts\violation_tracker.py" add no_thinking "Response without thinking blocks" 2>nul
            echo.
            echo [WARNING] This violation has been recorded
            echo           Future prompts may be blocked if violations accumulate
        )
        echo.
    )
)

REM Check Codex collaboration (if multiple files modified)
set "CODEX_ENFORCER=%USERPROFILE%\.claude\scripts\codex_enforcer.py"
set "SESSION_LOG=%USERPROFILE%\.claude\logs\last_session.txt"
if exist "%CODEX_ENFORCER%" (
    if exist "%SESSION_LOG%" (
        echo [VERIFICATION] Checking Codex collaboration...
        echo.
        py "%CODEX_ENFORCER%" check "%SESSION_LOG%" 2>nul
        if %ERRORLEVEL% NEQ 0 (
            echo.
            echo [VIOLATION] Codex collaboration missing!
            echo            Recording violation...
            py "%USERPROFILE%\.claude\scripts\violation_tracker.py" add no_codex "Multi-file task without Codex" 2>nul
            echo.
            echo [WARNING] This violation has been recorded
        )
        echo.
    )
)

REM Task completion summary
echo ================================================================
echo   [SUMMARY] Response Statistics
echo ================================================================
echo.
echo   Status: COMPLETED
echo   Timestamp: %date% %time%
echo.

REM Optional: Check TodoWrite status
if exist "%USERPROFILE%\.claude\todos.json" (
    echo [INFO] Todo list may have been updated
    echo       Check your current task status
    echo.
)

echo ================================================================
echo   Ready for next task
echo ================================================================
echo.

REM Windows Multi-Method Notification (More Reliable)
set "NOTIFY_SCRIPT=%USERPROFILE%\.claude\hooks\notify-multi.ps1"
if exist "%NOTIFY_SCRIPT%" (
    powershell -ExecutionPolicy Bypass -File "%NOTIFY_SCRIPT%" -Title "Claude Code" -Message "Task completed successfully" 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Desktop notification sent (multi-method)
        echo.
    )
)

exit /b 0
