#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Requirement Change Detector
要件の勝手な変更・判断を検出

Usage:
    py requirement_change_detector.py check <response_log>

Exit Codes:
    0: OK (no unauthorized requirement changes)
    1: VIOLATION (unauthorized requirement change detected)
"""

import sys
import re
from pathlib import Path


class RequirementChangeDetector:
    def __init__(self):
        # 要件変更を示す禁止パターン
        self.unauthorized_patterns = [
            r'代わりに.*を使用',
            r'別の.*に変更',
            r'こっちの方が.*いい',
            r'簡略化.*しました',
            r'最適化.*しました',
            r'〜の代替として',
            r'勝手に.*変更',
            r'自動的に.*変更',
        ]

        # 推測を示す禁止パターン
        self.speculation_patterns = [
            r'おそらく.*でしょう',
            r'たぶん.*だと思',
            r'推測すると',
            r'〜だろうと判断',
            r'〜のはずです',
            r'〜と仮定して',
        ]

        # 結合キー推測パターン（特に危険）
        self.join_speculation = [
            r'結合キーは.*だろう',
            r'おそらく.*で結合',
            r'他のビュー.*参考.*結合',
            r'同じキー.*使用',
        ]

        # 正しい確認パターン
        self.confirmation_patterns = [
            r'どのフィールドで結合',
            r'結合キーを教えて',
            r'どちらにしますか',
            r'確認.*ください',
            r'選択肢.*提示',
        ]

    def has_unauthorized_change(self, text: str) -> bool:
        """要件の勝手な変更があるか"""
        for pattern in self.unauthorized_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def has_speculation(self, text: str) -> bool:
        """推測による実装があるか"""
        for pattern in self.speculation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def has_join_speculation(self, text: str) -> bool:
        """結合キーの推測があるか"""
        for pattern in self.join_speculation:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def has_confirmation(self, text: str) -> bool:
        """ユーザーへの確認があるか"""
        for pattern in self.confirmation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def check(self, text: str) -> dict:
        """
        要件変更のチェック

        Returns:
            {
                'has_unauthorized': bool,
                'has_speculation': bool,
                'has_join_speculation': bool,
                'has_confirmation': bool,
                'is_compliant': bool,
                'message': str
            }
        """
        has_unauthorized = self.has_unauthorized_change(text)
        has_speculation = self.has_speculation(text)
        has_join_speculation = self.has_join_speculation(text)
        has_confirmation = self.has_confirmation(text)

        # 勝手な要件変更は重大違反
        if has_unauthorized:
            return {
                'has_unauthorized': True,
                'has_speculation': has_speculation,
                'has_join_speculation': has_join_speculation,
                'has_confirmation': has_confirmation,
                'is_compliant': False,
                'message': 'Unauthorized requirement change detected'
            }

        # 結合キー推測は重大違反
        if has_join_speculation:
            return {
                'has_unauthorized': False,
                'has_speculation': has_speculation,
                'has_join_speculation': True,
                'has_confirmation': has_confirmation,
                'is_compliant': False,
                'message': 'Join key speculation detected (forbidden)'
            }

        # 推測による実装は違反
        if has_speculation:
            return {
                'has_unauthorized': False,
                'has_speculation': True,
                'has_join_speculation': False,
                'has_confirmation': has_confirmation,
                'is_compliant': False,
                'message': 'Speculative implementation detected'
            }

        return {
            'has_unauthorized': False,
            'has_speculation': False,
            'has_join_speculation': False,
            'has_confirmation': has_confirmation,
            'is_compliant': True,
            'message': 'No unauthorized requirement changes'
        }


def main():
    if len(sys.argv) < 3:
        print("[ERROR] Usage: requirement_change_detector.py check <response_log>")
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

    detector = RequirementChangeDetector()
    result = detector.check(text)

    if result['is_compliant']:
        print(f"[OK] {result['message']}")
        sys.exit(0)
    else:
        print(f"[VIOLATION] {result['message']}")
        if result['has_unauthorized']:
            print("           NEVER change requirements without user approval")
            print("           Implement EXACTLY as specified")
        if result['has_join_speculation']:
            print("           NEVER guess join keys")
            print("           ALWAYS ask: 'どのフィールドで結合しますか？'")
        if result['has_speculation']:
            print("           Remove speculative phrases:")
            print("           'おそらく', 'たぶん', '推測', '〜だろう'")
        sys.exit(1)


if __name__ == '__main__':
    main()
