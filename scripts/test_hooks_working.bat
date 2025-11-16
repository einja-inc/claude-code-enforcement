@echo off
REM Test if Hooks are Working
REM This script verifies that all enforcement hooks are functioning

echo.
echo ================================================================
echo   Testing Claude Code Hooks System
echo ================================================================
echo.

set "PASS_COUNT=0"
set "FAIL_COUNT=0"

REM Test 1: Check if user-prompt-submit.bat exists
echo [TEST 1] Checking user-prompt-submit.bat...
if exist "%USERPROFILE%\.claude\hooks\user-prompt-submit.bat" (
    echo [PASS] user-prompt-submit.bat exists
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] user-prompt-submit.bat NOT FOUND
    set /a FAIL_COUNT+=1
)
echo.

REM Test 2: Check if assistant-response.bat exists
echo [TEST 2] Checking assistant-response.bat...
if exist "%USERPROFILE%\.claude\hooks\assistant-response.bat" (
    echo [PASS] assistant-response.bat exists
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] assistant-response.bat NOT FOUND
    set /a FAIL_COUNT+=1
)
echo.

REM Test 3: Check if notify-multi.ps1 exists
echo [TEST 3] Checking notify-multi.ps1...
if exist "%USERPROFILE%\.claude\hooks\notify-multi.ps1" (
    echo [PASS] notify-multi.ps1 exists
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] notify-multi.ps1 NOT FOUND
    set /a FAIL_COUNT+=1
)
echo.

REM Test 4: Check if thinking_enforcer.py exists
echo [TEST 4] Checking thinking_enforcer.py...
if exist "%USERPROFILE%\.claude\scripts\thinking_enforcer.py" (
    echo [PASS] thinking_enforcer.py exists
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] thinking_enforcer.py NOT FOUND
    set /a FAIL_COUNT+=1
)
echo.

REM Test 5: Check if violation_tracker.py exists
echo [TEST 5] Checking violation_tracker.py...
if exist "%USERPROFILE%\.claude\scripts\violation_tracker.py" (
    echo [PASS] violation_tracker.py exists
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] violation_tracker.py NOT FOUND
    set /a FAIL_COUNT+=1
)
echo.

REM Test 6: Check if codex_enforcer.py exists
echo [TEST 6] Checking codex_enforcer.py...
if exist "%USERPROFILE%\.claude\scripts\codex_enforcer.py" (
    echo [PASS] codex_enforcer.py exists
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] codex_enforcer.py NOT FOUND
    set /a FAIL_COUNT+=1
)
echo.

REM Test 7: Test violation_tracker functionality
echo [TEST 7] Testing violation_tracker.py functionality...
py "%USERPROFILE%\.claude\scripts\violation_tracker.py" check >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] violation_tracker.py works
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] violation_tracker.py error
    set /a FAIL_COUNT+=1
)
echo.

REM Test 8: Test notification (dry run)
echo [TEST 8] Testing notification system...
powershell -ExecutionPolicy Bypass -Command "Test-Path '%USERPROFILE%\.claude\hooks\notify-multi.ps1'" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] PowerShell can access notify-multi.ps1
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] PowerShell cannot access notify-multi.ps1
    set /a FAIL_COUNT+=1
)
echo.

REM Test 9: Check CLAUDE.md exists
echo [TEST 9] Checking CLAUDE.md...
if exist "%USERPROFILE%\.claude\CLAUDE.md" (
    echo [PASS] CLAUDE.md exists
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] CLAUDE.md NOT FOUND
    set /a FAIL_COUNT+=1
)
echo.

REM Test 10: Check clarification protocol in CLAUDE.md
echo [TEST 10] Checking clarification protocol in CLAUDE.md...
findstr /C:"MANDATORY CLARIFICATION PROTOCOL" "%USERPROFILE%\.claude\CLAUDE.md" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Clarification protocol found in CLAUDE.md
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Clarification protocol NOT FOUND
    set /a FAIL_COUNT+=1
)
echo.

REM Summary
echo ================================================================
echo   Test Summary
echo ================================================================
echo.
echo   Total Tests: 10
echo   Passed:      %PASS_COUNT%
echo   Failed:      %FAIL_COUNT%
echo.

if %FAIL_COUNT% EQU 0 (
    echo [SUCCESS] All hooks are properly configured!
    echo.
    echo Next steps to verify they're actually running:
    echo   1. Submit a prompt and check for ULTRA THINK MODE reminder
    echo   2. After response, check for desktop notification
    echo   3. Check violation status: py scripts\violation_tracker.py check
    echo.
    exit /b 0
) else (
    echo [WARNING] Some components are missing
    echo           Please review the failures above
    echo.
    exit /b 1
)
