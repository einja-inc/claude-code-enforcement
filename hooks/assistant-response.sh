#!/bin/bash
# Task Completion Notification Hook
# This hook sends a notification when Claude completes a response

# For Linux with notify-send
if command -v notify-send &> /dev/null; then
    notify-send "Claude Code" "タスクが完了しました！" -i dialog-information -t 5000
fi

# For macOS with osascript
if command -v osascript &> /dev/null; then
    osascript -e 'display notification "タスクが完了しました！" with title "Claude Code" sound name "Glass"'
fi

# Fallback: Console notification
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ タスク完了通知"
echo "  Claude Codeの作業が完了しました"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

exit 0
