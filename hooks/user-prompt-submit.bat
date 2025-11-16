@echo off
REM Ultra Think Mode Hook - ENFORCED VERSION with Clarification Requirement
REM This hook enforces CLAUDE.md rules with blocking capability

echo.
echo ================================================================
echo   [ULTRA THINK MODE] - MANDATORY ENFORCEMENT
echo ================================================================
echo.

REM Check for violations FIRST
set "VIOLATION_TRACKER=%USERPROFILE%\.claude\scripts\violation_tracker.py"
if exist "%VIOLATION_TRACKER%" (
    py "%VIOLATION_TRACKER%" is_blocked 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ================================================================
        echo   [BLOCKED] PROMPT REJECTED
        echo ================================================================
        echo.
        echo   Your prompt has been BLOCKED due to accumulated violations
        echo   of CLAUDE.md rules.
        echo.
        py "%VIOLATION_TRACKER%" check 2>nul
        echo.
        echo   To reset violations and continue:
        echo   py %USERPROFILE%\.claude\scripts\violation_tracker.py reset
        echo.
        echo   Or run:
        echo   .claude\scripts\reset_violations.bat
        echo.
        echo ================================================================
        exit /b 1
    )
)

echo [SYSTEM INSTRUCTION] This request requires deep thinking:
echo.
echo   MANDATORY ACTIONS:
echo   1. Use ^<thinking^> blocks extensively
echo   2. Analyze from multiple angles
echo   3. Consider edge cases and risks
echo   4. Verify CLAUDE.md compliance
echo   5. Think step-by-step through solutions
echo.
echo ================================================================
echo.

REM Check CLAUDE.md rules reminder
echo [REMINDER] Key CLAUDE.md Rules:
echo   - Codex collaboration for LookML/multi-file tasks
echo   - TodoWrite 8-10 items for complex tasks
echo   - Byterover retrieve/store knowledge
echo   - Sample vs Real data distinction
echo   - No unauthorized requirement changes
echo.
echo ================================================================
echo.

REM MANDATORY CLARIFICATION PROTOCOL
echo [CRITICAL] CLARIFICATION REQUIREMENT - MUST ASK QUESTIONS:
echo.
echo   ⚠️  If user's prompt contains ANY ambiguity or unclear points:
echo.
echo   ✅ MUST ask clarifying questions BEFORE starting implementation
echo   ✅ MUST NOT guess or assume user's intent
echo   ✅ MUST NOT proceed with uncertain requirements
echo   ✅ MUST NOT use "おそらく" "たぶん" "推測" in responses
echo.
echo   Ambiguous patterns to ALWAYS question:
echo   - "適当に" "よしなに" "いい感じに" "お任せ" "推測して"
echo   - Table joins without specified keys
echo   - Filters without specific conditions
echo   - Field references without confirmation
echo   - Missing フィールド名, 結合キー, 条件式
echo   - Any vague or unclear instructions
echo.
echo   Required action when ambiguity detected:
echo   1. 🛑 STOP - Do NOT start implementation
echo   2. 📋 List ALL unclear points as questions
echo   3. ⏸️  WAIT for user's explicit answers
echo   4. ✅ ONLY THEN start implementation
echo.
echo   Example questions to ask:
echo   - "どのフィールドで結合しますか？"
echo   - "フィルター条件を具体的に教えてください"
echo   - "営業担当者フィールドはbqbusiness_discussions___sales_staff_namebqですか？"
echo   - "要件を確認させてください：〇〇という理解で合っていますか？"
echo.
echo ================================================================
echo.

REM Optional: Check if thinking_enforcer.py exists
if exist "%USERPROFILE%\.claude\scripts\thinking_enforcer.py" (
    echo [INFO] Thinking enforcer ready
    echo       Will verify thinking blocks after response
    echo.
)

REM Show current violation status
if exist "%VIOLATION_TRACKER%" (
    echo [COMPLIANCE STATUS]
    py "%VIOLATION_TRACKER%" check 2>nul
    echo.
)

exit /b 0
