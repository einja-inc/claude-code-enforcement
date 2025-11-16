#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parallel Execution Checker
並列実行（複数Task()を1メッセージで実行）のチェック

Usage:
    py parallel_execution_checker.py check <response_log>

Exit Codes:
    0: OK (parallel execution detected or not needed)
    1: VIOLATION (sequential execution when parallel is possible)
"""

import sys
import re
from pathlib import Path


class ParallelExecutionChecker:
    def __init__(self):
        # Task使用パターン
        self.task_patterns = [
            r'Task\s*\(',
            r'<invoke name="Task">',
        ]

        # 複数ファイルパターン（並列実行推奨）
        self.multifile_patterns = [
            r'2.*ファイル',
            r'複数.*ファイル',
            r'\.lkml.*\.lkml',
            r'\.py.*\.py',
        ]

    def count_task_calls(self, text: str) -> int:
        """Task呼び出し回数をカウント"""
        count = 0
        for pattern in self.task_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count

    def is_multifile_task(self, text: str) -> bool:
        """複数ファイルタスクか"""
        for pattern in self.multifile_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def has_parallel_execution(self, text: str) -> bool:
        """
        並列実行を検出（同一メッセージ内に複数Task）

        検出方法: 近接したTask呼び出しをチェック
        """
        # Task呼び出しの位置を取得
        task_positions = []
        for pattern in self.task_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                task_positions.append(match.start())

        if len(task_positions) < 2:
            return False

        # 位置をソート
        task_positions.sort()

        # 連続したTask呼び出しがあるか（500文字以内）
        for i in range(len(task_positions) - 1):
            distance = task_positions[i+1] - task_positions[i]
            if distance < 500:  # 近接していれば並列実行とみなす
                return True

        return False

    def check(self, text: str) -> dict:
        """
        並列実行のチェック

        Returns:
            {
                'task_count': int,
                'is_multifile': bool,
                'has_parallel': bool,
                'is_compliant': bool,
                'message': str
            }
        """
        task_count = self.count_task_calls(text)
        is_multifile = self.is_multifile_task(text)
        has_parallel = self.has_parallel_execution(text)

        # Task使用なしの場合はチェック不要
        if task_count == 0:
            return {
                'task_count': 0,
                'is_multifile': is_multifile,
                'has_parallel': False,
                'is_compliant': True,
                'message': 'No Task calls detected'
            }

        # 単一Taskの場合はOK
        if task_count == 1:
            return {
                'task_count': 1,
                'is_multifile': is_multifile,
                'has_parallel': False,
                'is_compliant': True,
                'message': 'Single Task call (parallel not needed)'
            }

        # 複数ファイル + 複数Task + 並列実行なし = 違反
        if is_multifile and task_count >= 2 and not has_parallel:
            return {
                'task_count': task_count,
                'is_multifile': True,
                'has_parallel': False,
                'is_compliant': False,
                'message': f'Multiple Tasks ({task_count}) should run in parallel'
            }

        # 並列実行検出
        if has_parallel:
            return {
                'task_count': task_count,
                'is_multifile': is_multifile,
                'has_parallel': True,
                'is_compliant': True,
                'message': f'Parallel execution detected ({task_count} Tasks)'
            }

        return {
            'task_count': task_count,
            'is_multifile': is_multifile,
            'has_parallel': has_parallel,
            'is_compliant': True,
            'message': f'{task_count} Task calls (compliant)'
        }


def main():
    if len(sys.argv) < 3:
        print("[ERROR] Usage: parallel_execution_checker.py check <response_log>")
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

    checker = ParallelExecutionChecker()
    result = checker.check(text)

    if result['is_compliant']:
        print(f"[OK] {result['message']}")
        sys.exit(0)
    else:
        print(f"[VIOLATION] {result['message']}")
        if result['is_multifile'] and not result['has_parallel']:
            print("           Multiple files require parallel Task execution")
            print("           Run all Tasks in single message:")
            print("           [Single Message]:")
            print("             Task('Agent1', 'task1', 'analyst')")
            print("             Task('Agent2', 'task2', 'analyst')")
        sys.exit(1)


if __name__ == '__main__':
    main()
