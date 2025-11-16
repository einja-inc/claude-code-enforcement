@echo off
REM Pre-Response Check Hook - Claude応答前の自動チェック
REM Claude Codeの応答生成前に自動実行される

echo.
echo ========================================
echo Auto Compliance Check
echo ========================================
echo.

REM 自動コンプライアンスチェッカーを実行
py "%USERPROFILE%\.claude\auto_compliance_checker.py" %*

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Compliance issues detected.
    echo Please review and confirm with user before proceeding.
    echo.
    REM 警告のみで処理は続行（完全ブロックはしない）
    exit /b 0
)

echo.
echo [OK] Compliance check passed.
echo.
exit /b 0
