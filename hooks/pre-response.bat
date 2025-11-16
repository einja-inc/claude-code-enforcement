@echo off
REM Pre-Response Hook - Codex Collaboration Enforcer
REM This hook ensures Codex collaboration for all required tasks

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   🔍 PRE-RESPONSE CHECK - CODEX COLLABORATION
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Run Python validation script
py .claude\scripts\codex-enforcer.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ PRE-RESPONSE CHECK FAILED
    echo.
    echo 📋 MANDATORY RULES:
    echo   1. LookML修正 → Codex協力必須
    echo   2. 複数ファイル修正 → Codex並列実行必須
    echo   3. データ分析 → Codex必須
    echo   4. 忖度修正禁止 - 指示された内容のみ実行
    echo.
    echo 💡 REMINDER: Read .claude/CLAUDE.md for full rules
    echo.
    exit /b 1
)

echo ✅ Pre-response check passed
echo.
exit /b 0
