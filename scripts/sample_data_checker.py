#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sample Data vs Real Data Distinction Checker
サンプルデータと実データの明確な区別をチェック

Usage:
    py sample_data_checker.py check <response_log>

Exit Codes:
    0: OK (proper data distinction)
    1: VIOLATION (data presented without clear distinction)
"""

import sys
import re
from pathlib import Path


class SampleDataChecker:
    def __init__(self):
        # データ出力パターン
        self.data_output_patterns = [
            r'\{[\s\S]*?"[^"]+"\s*:\s*[^}]+\}',  # JSON形式
            r'\[\s*\{[\s\S]*?\}\s*\]',  # JSON配列
            r'DynamoDB|S3|MySQL|PostgreSQL|MongoDB',  # データソース名
            r'\.json|\.csv|\.xlsx',  # データファイル
            r'SELECT .* FROM',  # SQL
            r'API.*endpoint',  # API
        ]

        # サンプルデータ明示パターン
        self.sample_indicators = [
            r'⚠️.*サンプルデータ',
            r'これは.*サンプル',
            r'sample.*data',
            r'テスト用.*データ',
            r'動作確認用',
            r'架空のデータ',
            r'data_type.*SAMPLE',
        ]

        # 実データ明示パターン
        self.real_data_indicators = [
            r'✅.*実データ',
            r'データソース:',
            r'取得日時:',
            r'data_type.*REAL',
            r'DynamoDB.*テーブル',
            r'S3.*バケット',
            r'API.*エンドポイント',
        ]

        # 禁止パターン（推測を示す表現）
        self.forbidden_phrases = [
            r'おそらく.*データ',
            r'たぶん.*データ',
            r'推測すると',
            r'だと思います.*データ',
        ]

    def has_data_output(self, text: str) -> bool:
        """データ出力が含まれているか検出"""
        for pattern in self.data_output_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                return True
        return False

    def has_sample_indicator(self, text: str) -> bool:
        """サンプルデータの明示があるか"""
        for pattern in self.sample_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def has_real_data_indicator(self, text: str) -> bool:
        """実データの明示があるか"""
        for pattern in self.real_data_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def has_forbidden_phrases(self, text: str) -> bool:
        """推測を示す禁止表現があるか"""
        for pattern in self.forbidden_phrases:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def check(self, text: str) -> dict:
        """
        データ区別のチェック

        Returns:
            {
                'has_data': bool,
                'has_distinction': bool,
                'has_forbidden': bool,
                'is_compliant': bool,
                'message': str
            }
        """
        has_data = self.has_data_output(text)
        has_sample = self.has_sample_indicator(text)
        has_real = self.has_real_data_indicator(text)
        has_forbidden = self.has_forbidden_phrases(text)

        # データ出力がない場合はチェック不要
        if not has_data:
            return {
                'has_data': False,
                'has_distinction': True,
                'has_forbidden': False,
                'is_compliant': True,
                'message': 'No data output detected'
            }

        # データ出力があるのに区別がない場合は違反
        has_distinction = has_sample or has_real

        if not has_distinction:
            return {
                'has_data': True,
                'has_distinction': False,
                'has_forbidden': has_forbidden,
                'is_compliant': False,
                'message': 'Data output without clear distinction (sample vs real)'
            }

        # 禁止表現がある場合は違反
        if has_forbidden:
            return {
                'has_data': True,
                'has_distinction': has_distinction,
                'has_forbidden': True,
                'is_compliant': False,
                'message': 'Forbidden speculative phrases detected'
            }

        return {
            'has_data': True,
            'has_distinction': True,
            'has_forbidden': False,
            'is_compliant': True,
            'message': 'Data properly distinguished'
        }


def main():
    if len(sys.argv) < 3:
        print("[ERROR] Usage: sample_data_checker.py check <response_log>")
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

    checker = SampleDataChecker()
    result = checker.check(text)

    if result['is_compliant']:
        print(f"[OK] {result['message']}")
        sys.exit(0)
    else:
        print(f"[VIOLATION] {result['message']}")
        if result['has_data'] and not result['has_distinction']:
            print("           Data output must clearly indicate:")
            print("           - Sample data: use warning mark (⚠️) + 'サンプルデータ'")
            print("           - Real data: specify 'データソース:' + source name")
        if result['has_forbidden']:
            print("           Remove speculative phrases like 'おそらく', 'たぶん', '推測'")
        sys.exit(1)


if __name__ == '__main__':
    main()
