#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA THINK MODE Enforcer
Claude Codeの応答に<thinking>ブロックが含まれているかチェック

Usage:
    python thinking_enforcer.py <response_file>

Exit Codes:
    0: Thinking blocks found (OK)
    1: No thinking blocks (WARNING)
"""

import sys
import re
from pathlib import Path


def check_thinking_blocks(text: str) -> tuple[bool, dict]:
    """
    テキスト内の<thinking>ブロックをチェック

    Returns:
        (has_thinking, stats)
    """
    # <thinking>...</thinking> パターンを検出
    thinking_pattern = r'<thinking>.*?</thinking>'
    matches = re.findall(thinking_pattern, text, re.DOTALL)

    stats = {
        'count': len(matches),
        'total_chars': sum(len(m) for m in matches),
        'has_thinking': len(matches) > 0
    }

    return stats['has_thinking'], stats


def main():
    if len(sys.argv) < 2:
        print("[INFO] Usage: thinking_enforcer.py <response_file>")
        sys.exit(0)

    response_file = Path(sys.argv[1])

    if not response_file.exists():
        print(f"[INFO] Response file not found: {response_file}")
        sys.exit(0)

    try:
        content = response_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"[INFO] Could not read file: {e}")
        sys.exit(0)

    has_thinking, stats = check_thinking_blocks(content)

    print("=" * 60)
    print("  ULTRA THINK MODE - Verification")
    print("=" * 60)

    if has_thinking:
        print(f"[OK] Thinking blocks found: {stats['count']}")
        print(f"     Total thinking content: {stats['total_chars']} characters")
        print()
        print("[SUCCESS] ULTRA THINK MODE is active")
        sys.exit(0)
    else:
        print("[WARNING] No thinking blocks detected!")
        print()
        print("REMINDER: You should use <thinking> blocks for:")
        print("  1. Complex problem analysis")
        print("  2. Multi-step reasoning")
        print("  3. Edge case consideration")
        print("  4. CLAUDE.md compliance check")
        print()
        print("This is just a reminder - not blocking execution")
        sys.exit(1)


if __name__ == '__main__':
    main()
