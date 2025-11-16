#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TodoWrite Enforcer
TodoWriteの使用と8-10項目要件をチェック

Usage:
    py todowrite_enforcer.py check <response_log>

Exit Codes:
    0: OK (TodoWrite used with 8-10 items)
    1: VIOLATION (TodoWrite missing or insufficient items)
"""

import sys
import re
import json
from pathlib import Path


class TodoWriteEnforcer:
    def __init__(self):
        # TodoWrite使用パターン
        self.todowrite_patterns = [
            r'TodoWrite',
            r'<invoke name="TodoWrite">',
            r'"todos":\s*\[',
        ]

        # 複雑タスクパターン（TodoWrite必須）
        self.complex_task_patterns = [
            r'修正.*ファイル',
            r'実装.*機能',
            r'追加.*ディメンション',
            r'作成.*ビュー',
            r'分析.*データ',
            r'LookML.*修正',
            r'複数.*ファイル',
            r'Task\(.*Codex',
        ]

    def has_todowrite(self, text: str) -> bool:
        """TodoWriteが使用されているか"""
        for pattern in self.todowrite_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def is_complex_task(self, text: str) -> bool:
        """複雑タスクか（TodoWrite必須）"""
        for pattern in self.complex_task_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def count_todo_items(self, text: str) -> int:
        """TodoWriteの項目数をカウント"""
        # TodoWriteのJSONパラメータを抽出
        match = re.search(r'"todos":\s*\[(.*?)\]', text, re.DOTALL)
        if not match:
            return 0

        todos_json = match.group(1)

        # 簡易的にオブジェクト数をカウント（{...}の数）
        count = len(re.findall(r'\{[^}]*"content"', todos_json))

        return count

    def check(self, text: str) -> dict:
        """
        TodoWrite使用のチェック

        Returns:
            {
                'has_todowrite': bool,
                'is_complex': bool,
                'todo_count': int,
                'is_compliant': bool,
                'message': str
            }
        """
        has_todowrite = self.has_todowrite(text)
        is_complex = self.is_complex_task(text)
        todo_count = self.count_todo_items(text) if has_todowrite else 0

        # 簡単なタスクの場合はチェック不要
        if not is_complex:
            return {
                'has_todowrite': has_todowrite,
                'is_complex': False,
                'todo_count': todo_count,
                'is_compliant': True,
                'message': 'Simple task, TodoWrite optional'
            }

        # 複雑タスクでTodoWrite未使用は違反
        if is_complex and not has_todowrite:
            return {
                'has_todowrite': False,
                'is_complex': True,
                'todo_count': 0,
                'is_compliant': False,
                'message': 'Complex task requires TodoWrite'
            }

        # TodoWrite使用だが項目数不足は違反
        if has_todowrite and todo_count < 8:
            return {
                'has_todowrite': True,
                'is_complex': is_complex,
                'todo_count': todo_count,
                'is_compliant': False,
                'message': f'TodoWrite has only {todo_count} items (minimum 8 required)'
            }

        return {
            'has_todowrite': True,
            'is_complex': is_complex,
            'todo_count': todo_count,
            'is_compliant': True,
            'message': f'TodoWrite compliant ({todo_count} items)'
        }


def main():
    if len(sys.argv) < 3:
        print("[ERROR] Usage: todowrite_enforcer.py check <response_log>")
        sys.exit(1)

    command = sys.argv[1]
    if command != "check":
        print(f"[ERROR] Unknown command: {command}")
        sys.exit(1)

    response_log = Path(sys.argv[2])
    if not response_log.exists():
        print("[WARNING] Response log not found")
        sys.exit(0)

    try:
        text = response_log.read_text(encoding='utf-8')
    except Exception as e:
        print(f"[WARNING] Could not read response log: {e}")
        sys.exit(0)

    enforcer = TodoWriteEnforcer()
    result = enforcer.check(text)

    if result['is_compliant']:
        print(f"[OK] {result['message']}")
        sys.exit(0)
    else:
        print(f"[VIOLATION] {result['message']}")
        if not result['has_todowrite']:
            print("           Complex tasks require TodoWrite with 8-10 items")
            print("           Use: TodoWrite { todos: [...8-10 items...] }")
        elif result['todo_count'] < 8:
            print(f"           Current: {result['todo_count']} items")
            print("           Required: 8-10 items")
            print("           Break down task into smaller, actionable steps")
        sys.exit(1)


if __name__ == '__main__':
    main()
