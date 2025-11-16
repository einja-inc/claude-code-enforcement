#!/usr/bin/env python3
"""
Ambiguity Detector for User Prompts
プロンプト内の曖昧な表現・不明点を検出し、質問を強制する
"""

import sys
import re
from pathlib import Path

class AmbiguityDetector:
    def __init__(self):
        # 曖昧な表現のパターン
        self.ambiguous_phrases = [
            # 日本語
            r'適当に', r'よしなに', r'いい感じに', r'うまく', r'それっぽく',
            r'なんとなく', r'ざっくり', r'テキトー', r'適宜', r'よろしく',
            r'お任せ', r'勝手に', r'自動で', r'推測して', r'察して',
            # 英語
            r'somehow', r'automatically', r'figure it out', r'guess',
            r'whatever', r'anything', r'something like'
        ]

        # 要件が不明確なパターン
        self.unclear_requirements = [
            r'(?:テーブル|table).*(?:結合|join)',  # テーブル結合（結合キー不明の可能性）
            r'(?:フィルター|filter|絞|抽出)',  # フィルター（条件不明の可能性）
            r'(?:追加|作成|新規)',  # 追加（詳細不明の可能性）
            r'(?:修正|変更|更新)',  # 修正（対象不明の可能性）
            r'(?:似た|同じような|同様)',  # 類似要求（具体性欠如）
        ]

        # 質問が必要なキーワード
        self.question_triggers = [
            r'結合キー', r'join key', r'どのフィールド', r'which field',
            r'条件', r'condition', r'where', r'filter',
            r'営業担当', r'工務担当', r'sales', r'construction',
            r'ディメンション', r'メジャー', r'dimension', r'measure',
        ]

    def detect_ambiguity(self, prompt: str) -> dict:
        """プロンプトの曖昧性を検出"""
        issues = {
            'ambiguous_phrases': [],
            'unclear_requirements': [],
            'question_triggers': [],
            'has_issues': False
        }

        # 曖昧な表現を検出
        for pattern in self.ambiguous_phrases:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            if matches:
                issues['ambiguous_phrases'].extend(matches)

        # 不明確な要件を検出
        for pattern in self.unclear_requirements:
            if re.search(pattern, prompt, re.IGNORECASE):
                issues['unclear_requirements'].append(pattern)

        # 質問が必要なキーワードを検出
        for pattern in self.question_triggers:
            if re.search(pattern, prompt, re.IGNORECASE):
                issues['question_triggers'].append(pattern)

        # いずれかの問題があればフラグを立てる
        issues['has_issues'] = bool(
            issues['ambiguous_phrases'] or
            issues['unclear_requirements'] or
            issues['question_triggers']
        )

        return issues

    def generate_clarification_prompt(self, issues: dict) -> str:
        """不明点を明確化するための追加指示を生成"""

        if not issues['has_issues']:
            return ""

        clarification = "\n\n" + "="*60 + "\n"
        clarification += "🚨 MANDATORY CLARIFICATION PROTOCOL\n"
        clarification += "="*60 + "\n\n"

        clarification += "⚠️ このプロンプトには不明点・曖昧な表現が検出されました。\n\n"

        clarification += "**絶対厳守ルール（ZERO TOLERANCE）**:\n"
        clarification += "1. ✅ 不明点を**必ず質問**してから実装を開始する\n"
        clarification += "2. ❌ 推測で実装を進めることは**絶対禁止**\n"
        clarification += "3. ❌ 「おそらく」「たぶん」で判断することは**絶対禁止**\n"
        clarification += "4. ❌ 要件を勝手に変更することは**絶対禁止**\n\n"

        if issues['ambiguous_phrases']:
            clarification += "📋 検出された曖昧な表現:\n"
            for phrase in set(issues['ambiguous_phrases']):
                clarification += f"   - 「{phrase}」\n"
            clarification += "\n"

        if issues['unclear_requirements']:
            clarification += "📋 不明確な要件:\n"
            clarification += "   以下の点を明確化してください:\n"

            if any('結合' in p or 'join' in p for p in issues['unclear_requirements']):
                clarification += "   - ✋ テーブル結合の結合キーは何ですか？\n"
                clarification += "   - ✋ 結合タイプは何ですか？（INNER/LEFT/RIGHT）\n"

            if any('フィルター' in p or 'filter' in p for p in issues['unclear_requirements']):
                clarification += "   - ✋ フィルター条件を具体的に指定してください\n"

            if any('追加' in p or '作成' in p for p in issues['unclear_requirements']):
                clarification += "   - ✋ 追加する内容の詳細を教えてください\n"

            if any('修正' in p or '変更' in p for p in issues['unclear_requirements']):
                clarification += "   - ✋ 修正対象と修正内容を具体的に教えてください\n"

            clarification += "\n"

        if issues['question_triggers']:
            clarification += "📋 質問が必要なキーワード検出:\n"
            clarification += "   以下について確認が必要です:\n"

            if any('営業担当' in str(p) or 'sales' in str(p) for p in issues['question_triggers']):
                clarification += "   - ✋ 営業担当者フィールド: bqbusiness_discussions___sales_staff_namebq を使用しますか？\n"

            if any('工務担当' in str(p) or 'construction' in str(p) for p in issues['question_triggers']):
                clarification += "   - ✋ 工務担当者フィールド: bqbusiness_discussions___employee_name___construction_employeebq を使用しますか？\n"

            if any('結合' in str(p) or 'join' in str(p) for p in issues['question_triggers']):
                clarification += "   - ✋ 結合キーを明示的に指定してください\n"

            clarification += "\n"

        clarification += "="*60 + "\n"
        clarification += "**実装開始前に、上記の不明点を必ず質問してください**\n"
        clarification += "="*60 + "\n"

        return clarification

def main():
    if len(sys.argv) < 2:
        print("Usage: python ambiguity_detector.py <prompt_text_or_file>")
        sys.exit(1)

    # 引数からプロンプトを取得
    arg = sys.argv[1]

    # ファイルパスの場合は読み込む
    if Path(arg).exists():
        with open(arg, 'r', encoding='utf-8') as f:
            prompt = f.read()
    else:
        # 直接テキストとして扱う
        prompt = arg

    detector = AmbiguityDetector()
    issues = detector.detect_ambiguity(prompt)

    if issues['has_issues']:
        print("\n" + "="*60)
        print("⚠️  AMBIGUITY DETECTED - CLARIFICATION REQUIRED")
        print("="*60)

        if issues['ambiguous_phrases']:
            print("\n📋 Ambiguous phrases found:")
            for phrase in set(issues['ambiguous_phrases']):
                print(f"   - '{phrase}'")

        if issues['unclear_requirements']:
            print(f"\n📋 Unclear requirements detected: {len(issues['unclear_requirements'])} patterns")

        if issues['question_triggers']:
            print(f"\n📋 Question triggers detected: {len(issues['question_triggers'])} keywords")

        print("\n" + detector.generate_clarification_prompt(issues))

        sys.exit(1)  # 曖昧性検出時はエラー終了
    else:
        print("[OK] No ambiguity detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
