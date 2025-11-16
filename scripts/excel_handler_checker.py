#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel File Handling Checker
Excelファイル処理方法の検証（Python必須、Read tool禁止）

Usage:
    py excel_handler_checker.py check <response_log>

Exit Codes:
    0: OK (proper Excel handling)
    1: VIOLATION (incorrect Excel handling)
"""

import sys
import re
from pathlib import Path


class ExcelHandlerChecker:
    def __init__(self):
        # Excelファイル参照パターン
        self.excel_patterns = [
            r'\.xlsx?\b',
            r'Excel.*ファイル',
            r'Excelを.*読',
        ]

        # Read tool使用パターン（違反）
        self.read_tool_patterns = [
            r'Read.*\.xlsx?',
            r'Read tool.*Excel',
            r'<invoke name="Read">.*\.xlsx?',
        ]

        # Python使用パターン（正しい）
        self.python_patterns = [
            r'import pandas',
            r'pd\.read_excel',
            r'openpyxl',
            r'sys\.stdout\.reconfigure',
        ]

        # 禁止パターン
        self.forbidden_patterns = [
            r'CSV.*変換.*してください',
            r'CSV.*変換.*依頼',
            r'CSVに.*変換.*して',
            r'binary file.*cannot read',
        ]

    def has_excel_reference(self, text: str) -> bool:
        """Excelファイルへの言及があるか"""
        for pattern in self.excel_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def used_read_tool(self, text: str) -> bool:
        """Read toolをExcelに使用しているか（違反）"""
        for pattern in self.read_tool_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def used_python(self, text: str) -> bool:
        """Pythonスクリプトを使用しているか（正しい）"""
        for pattern in self.python_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def has_forbidden_phrases(self, text: str) -> bool:
        """禁止表現があるか"""
        for pattern in self.forbidden_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def check(self, text: str) -> dict:
        """
        Excel処理方法のチェック

        Returns:
            {
                'has_excel': bool,
                'used_read_tool': bool,
                'used_python': bool,
                'has_forbidden': bool,
                'is_compliant': bool,
                'message': str
            }
        """
        has_excel = self.has_excel_reference(text)

        # Excel言及がない場合はチェック不要
        if not has_excel:
            return {
                'has_excel': False,
                'used_read_tool': False,
                'used_python': False,
                'has_forbidden': False,
                'is_compliant': True,
                'message': 'No Excel file reference detected'
            }

        used_read = self.used_read_tool(text)
        used_python = self.used_python(text)
        has_forbidden = self.has_forbidden_phrases(text)

        # Read tool使用は違反
        if used_read:
            return {
                'has_excel': True,
                'used_read_tool': True,
                'used_python': used_python,
                'has_forbidden': has_forbidden,
                'is_compliant': False,
                'message': 'Read tool used for Excel file (forbidden)'
            }

        # 禁止表現（CSV変換依頼）は違反
        if has_forbidden:
            return {
                'has_excel': True,
                'used_read_tool': False,
                'used_python': used_python,
                'has_forbidden': True,
                'is_compliant': False,
                'message': 'Asked user to convert to CSV (forbidden)'
            }

        # Excelがあるのにpython未使用の場合は警告
        if has_excel and not used_python:
            return {
                'has_excel': True,
                'used_read_tool': False,
                'used_python': False,
                'has_forbidden': False,
                'is_compliant': False,
                'message': 'Excel file mentioned but Python not used'
            }

        return {
            'has_excel': True,
            'used_read_tool': False,
            'used_python': True,
            'has_forbidden': False,
            'is_compliant': True,
            'message': 'Excel handled correctly with Python'
        }


def main():
    if len(sys.argv) < 3:
        print("[ERROR] Usage: excel_handler_checker.py check <response_log>")
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

    checker = ExcelHandlerChecker()
    result = checker.check(text)

    if result['is_compliant']:
        print(f"[OK] {result['message']}")
        sys.exit(0)
    else:
        print(f"[VIOLATION] {result['message']}")
        if result['used_read_tool']:
            print("           NEVER use Read tool for Excel files")
            print("           ALWAYS use Python: import pandas; pd.read_excel()")
        if result['has_forbidden']:
            print("           NEVER ask user to convert to CSV")
            print("           Handle Excel directly with Python")
        if result['has_excel'] and not result['used_python']:
            print("           Must use Python for Excel processing")
            print("           Example: py -c \"import pandas as pd; df = pd.read_excel('file.xlsx')\"")
        sys.exit(1)


if __name__ == '__main__':
    main()
