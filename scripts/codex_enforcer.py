#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Collaboration Enforcer
複数ファイル修正時にCodex協力を強制

Usage:
    py codex_enforcer.py check <session_log>
    py codex_enforcer.py detect_multifile <message>

Exit Codes:
    0: OK (Codex協力あり or 単一ファイル)
    1: VIOLATION (複数ファイルでCodex未使用)
"""

import sys
import re
from pathlib import Path


def detect_multifile_task(message: str) -> tuple[bool, list]:
    """
    メッセージから複数ファイル修正タスクを検出

    Returns:
        (is_multifile, file_list)
    """
    # ファイルパスパターン
    file_patterns = [
        r'\.lkml',
        r'\.py',
        r'\.js',
        r'\.ts',
        r'\.bat',
        r'\.md'
    ]

    detected_files = []

    for pattern in file_patterns:
        matches = re.findall(r'\S+' + pattern, message, re.IGNORECASE)
        detected_files.extend(matches)

    # 重複を削除
    detected_files = list(set(detected_files))

    is_multifile = len(detected_files) >= 2

    return is_multifile, detected_files


def check_codex_usage(session_log: Path) -> bool:
    """
    セッションログからCodex（Task tool）使用を検出

    Returns:
        True if Codex was used
    """
    if not session_log.exists():
        return False

    try:
        content = session_log.read_text(encoding='utf-8')

        # Task tool呼び出しパターン
        codex_patterns = [
            r'Task\(',
            r'<invoke name="Task">',
            r'subagent_type.*codex',
            r'subagent_type.*analyst'
        ]

        for pattern in codex_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False
    except Exception as e:
        print(f"[WARNING] Could not check session log: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: codex_enforcer.py <command>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "detect_multifile":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: codex_enforcer.py detect_multifile <message>")
            sys.exit(1)

        message = " ".join(sys.argv[2:])
        is_multifile, files = detect_multifile_task(message)

        if is_multifile:
            print(f"[MULTIFILE DETECTED]")
            print(f"  Files: {len(files)}")
            for f in files:
                print(f"    - {f}")
            print()
            print("[WARNING] Codex collaboration is REQUIRED")
            print("          Use Task(codex) for analysis")
            sys.exit(1)
        else:
            print("[OK] Single file or no file modification detected")
            sys.exit(0)

    elif command == "check":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: codex_enforcer.py check <session_log>")
            sys.exit(1)

        session_log = Path(sys.argv[2])

        if check_codex_usage(session_log):
            print("[OK] Codex collaboration detected")
            sys.exit(0)
        else:
            print("[VIOLATION] No Codex collaboration found")
            print("            Recording violation...")
            sys.exit(1)

    else:
        print(f"[ERROR] Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
