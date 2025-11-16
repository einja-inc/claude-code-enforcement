"""
統合修正システム

violation_detector と auto_correct_suggestions を統合し、
違反検出時に自動的に修正提案を表示する
"""

import sys
from pathlib import Path
from typing import List, Dict

# Windows環境でのUTF-8出力設定
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from violation_detector import ViolationDetector, Violation
from auto_correct_suggestions import AutoCorrectSuggester


class IntegratedCorrectionSystem:
    """統合修正システム"""

    def __init__(self):
        """初期化"""
        self.detector = ViolationDetector()
        self.suggester = AutoCorrectSuggester()

    def analyze_and_suggest(self, content: str, show_suggestions: bool = True) -> Dict:
        """
        コンテンツを分析し、違反があれば修正提案を表示

        Args:
            content: 分析対象のコンテンツ
            show_suggestions: 修正提案を表示するか

        Returns:
            分析結果の辞書
        """
        # 違反検出
        violations = self.detector.detect(content)

        result = {
            'violations': violations,
            'violation_count': len(violations),
            'compliance_score': self._calculate_compliance_score(violations),
            'suggestions': []
        }

        # 修正提案生成
        if violations and show_suggestions:
            print("\n" + "=" * 80)
            print(f"🔍 違反検出: {len(violations)}件")
            print("=" * 80)

            for violation in violations:
                print(f"\n[{violation.severity}] {violation.type}")
                print(f"メッセージ: {violation.message}")
                print(f"スコア影響: {violation.score_impact}")
                print(f"行番号: {violation.line_number}")
                print("-" * 80)

                # 修正提案生成
                suggestion = self.suggester.suggest(violation.type)
                if suggestion:
                    result['suggestions'].append(suggestion)
                    self.suggester.display_suggestion(suggestion)

        return result

    def _calculate_compliance_score(self, violations: List[Violation]) -> int:
        """
        コンプライアンススコア計算

        Args:
            violations: 違反リスト

        Returns:
            スコア（0-100）
        """
        base_score = 100
        for violation in violations:
            base_score += violation.score_impact

        return max(0, min(100, base_score))

    def analyze_file(self, filepath: str) -> Dict:
        """
        ファイルを分析

        Args:
            filepath: 分析対象ファイルパス

        Returns:
            分析結果
        """
        file_path = Path(filepath)
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {filepath}")

        content = file_path.read_text(encoding='utf-8')
        print(f"\n📄 ファイル分析: {file_path.name}")
        print(f"サイズ: {len(content)} 文字")

        return self.analyze_and_suggest(content)

    def analyze_conversation_log(self, log_file: str) -> Dict:
        """
        Claude Code会話ログを分析

        Args:
            log_file: ログファイルパス（JSONL形式）

        Returns:
            分析結果
        """
        import json

        log_path = Path(log_file)
        if not log_path.exists():
            raise FileNotFoundError(f"ログファイルが見つかりません: {log_file}")

        print(f"\n📝 会話ログ分析: {log_path.name}")

        # JSONLファイルを読み込み、全テキストを結合
        conversations = []
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if 'content' in entry:
                        conversations.append(entry['content'])
                except json.JSONDecodeError:
                    continue

        combined_content = "\n".join(conversations)
        print(f"会話エントリ数: {len(conversations)}")
        print(f"総文字数: {len(combined_content)}")

        return self.analyze_and_suggest(combined_content)

    def generate_report(self, result: Dict, output_path: str = "compliance_report.md"):
        """
        コンプライアンスレポートを生成

        Args:
            result: analyze_and_suggest の結果
            output_path: 出力ファイルパス
        """
        import datetime as dt

        report = f"""# コンプライアンスレポート

**生成日時**: {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**コンプライアンススコア**: {result['compliance_score']}%
**違反件数**: {result['violation_count']}件

---

## 評価

"""

        # スコア評価
        score = result['compliance_score']
        if score >= 95:
            report += "✅ **PERFECT**: 模範的なコンプライアンス\n\n"
        elif score >= 75:
            report += "✅ **GOOD**: 良好なコンプライアンス\n\n"
        elif score >= 50:
            report += "⚠️ **WARNING**: 改善が必要\n\n"
        else:
            report += "❌ **FAIL**: 重大な問題あり（コミットブロック対象）\n\n"

        # 違反詳細
        if result['violations']:
            report += "## 違反詳細\n\n"

            for idx, violation in enumerate(result['violations'], 1):
                report += f"""### {idx}. {violation.type}

- **重大度**: {violation.severity}
- **スコア影響**: {violation.score_impact}
- **メッセージ**: {violation.message}
- **行番号**: {violation.line_number}
- **コンテキスト**:
  ```
  {violation.context}
  ```

"""

        # 修正提案
        if result['suggestions']:
            report += "## 修正提案\n\n"

            for idx, suggestion in enumerate(result['suggestions'], 1):
                report += f"""### {idx}. {suggestion.violation_type}

#### ❌ 間違ったパターン

```
{suggestion.wrong_pattern}
```

#### ✅ 正しいパターン

```
{suggestion.correct_pattern}
```

#### 説明

{suggestion.explanation}

#### 自動修正

{'✅ 可能' if suggestion.auto_fixable else '❌ 不可（手動修正必要）'}

---

"""

        # レポート保存
        output_file = Path(output_path)
        output_file.write_text(report, encoding='utf-8')
        print(f"\n📊 レポート生成完了: {output_file.absolute()}")


def main():
    """テスト実行"""
    import argparse

    parser = argparse.ArgumentParser(description='統合修正システム')
    parser.add_argument('--file', type=str, help='分析対象ファイル')
    parser.add_argument('--log', type=str, help='会話ログファイル（JSONL）')
    parser.add_argument('--text', type=str, help='直接テキストを分析')
    parser.add_argument('--report', action='store_true', help='レポート生成')
    parser.add_argument('--no-suggestions', action='store_true', help='修正提案を表示しない')

    args = parser.parse_args()

    system = IntegratedCorrectionSystem()

    result = None

    # ファイル分析
    if args.file:
        result = system.analyze_file(args.file)

    # ログ分析
    elif args.log:
        result = system.analyze_conversation_log(args.log)

    # テキスト分析
    elif args.text:
        result = system.analyze_and_suggest(args.text, show_suggestions=not args.no_suggestions)

    # デフォルト: サンプルテスト
    else:
        print("=" * 80)
        print("統合修正システム - サンプルテスト")
        print("=" * 80)

        test_content = """
User: "ファイルを修正してください"
Assistant:
Edit "test.lkml"

TodoWrite { todos: [
  {content: "修正", status: "pending", activeForm: "修正中"}
]}

Here is sample data:
{"id": 123, "name": "Test"}
"""

        print("\nテストコンテンツ:")
        print("-" * 80)
        print(test_content)
        print("-" * 80)

        result = system.analyze_and_suggest(test_content, show_suggestions=not args.no_suggestions)

    # レポート生成
    if result and args.report:
        system.generate_report(result)

    # サマリー表示
    if result:
        print("\n" + "=" * 80)
        print("分析サマリー")
        print("=" * 80)
        print(f"コンプライアンススコア: {result['compliance_score']}%")
        print(f"違反件数: {result['violation_count']}")
        print(f"修正提案数: {len(result['suggestions'])}")

        # 評価
        score = result['compliance_score']
        if score >= 95:
            print("\n✅ 評価: PERFECT（模範的）")
        elif score >= 75:
            print("\n✅ 評価: GOOD（良好）")
        elif score >= 50:
            print("\n⚠️ 評価: WARNING（要改善）")
        else:
            print("\n❌ 評価: FAIL（コミットブロック対象）")

        print("=" * 80)


if __name__ == "__main__":
    main()