@echo off
REM Pre-Task Check Hook - タスク開始前の自動チェック
REM このスクリプトはタスク開始前に自動実行される

echo.
echo ========================================
echo CLAUDE.md Rule Compliance Check
echo ========================================
echo.

REM Pre-Task Checklistを実行
py "%USERPROFILE%\.claude\pre_task_checklist.py"

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Pre-Task Check failed.
    echo Please review the violations and fix them before proceeding.
    echo.
    exit /b 1
)

echo.
echo [SUCCESS] Pre-Task Check passed.
echo You can proceed with the task.
echo.
exit /b 0
