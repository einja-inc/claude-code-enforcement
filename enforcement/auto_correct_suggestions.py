"""
自動修正提案システム

8-Layer Enforcement System - Layer 7
違反検出時に正しいパターンを自動提示し、ユーザーに修正案を提供する
"""

import sys
import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Windows環境でのカラー出力用
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # coloramaが無い場合のフォールバック
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = Back = Style = DummyColor()


@dataclass
class CorrectionSuggestion:
    """修正提案"""
    violation_type: str
    wrong_pattern: str
    correct_pattern: str
    explanation: str
    auto_fixable: bool = False


class AutoCorrectSuggester:
    """自動修正提案エンジン"""

    def __init__(self):
        """初期化"""
        self.correction_patterns = self._load_correction_patterns()

    def _load_correction_patterns(self) -> Dict[str, Dict]:
        """
        9種類の違反ごとの修正パターン定義

        Returns:
            修正パターン辞書
        """
        return {
            # 違反1: Codex協力なし
            "no_codex_collaboration": {
                "wrong": """❌ 違反パターン:
Read "file.lkml"
Edit "file.lkml"  # Codex協力なし""",

                "correct": """✅ 正しいパターン:
[Single Message]:
  Read "file.lkml"
  Task("Codex Analyst", "ファイル構造を分析して最適な修正箇所を特定", "analyst")
  # ↓ Codex結果を待つ
  Edit "file.lkml"  # Codexの分析を踏まえて修正""",

                "explanation": """
【重要】単一ファイルの修正であっても、必ずCodex analystエージェントと協力する

理由:
- SQL構造の正確な理解が必要
- 既存ロジックとの整合性確認
- 見落としを防止
- 複数の視点からの検証

違反時のペナルティ: -20点
""",
                "auto_fixable": False
            },

            # 違反2: TodoWrite項目数不足
            "insufficient_todowrite": {
                "wrong": """❌ 違反パターン:
TodoWrite {{ todos: [
  {{content: "分析", status: "pending", activeForm: "分析中"}},
  {{content: "実装", status: "pending", activeForm: "実装中"}}
]}}  # 2個のみ（8個必要）""",

                "correct": """✅ 正しいパターン:
TodoWrite {{ todos: [
  {{content: "Byterover知識検索実行", status: "pending", activeForm: "知識検索中"}},
  {{content: "要件分析", status: "pending", activeForm: "要件分析中"}},
  {{content: "Codex協力でファイル構造分析", status: "pending", activeForm: "構造分析中"}},
  {{content: "実装計画策定", status: "pending", activeForm: "計画策定中"}},
  {{content: "コード実装", status: "pending", activeForm: "実装中"}},
  {{content: "テスト実行", status: "pending", activeForm: "テスト中"}},
  {{content: "Byterover知識保存", status: "pending", activeForm: "知識保存中"}},
  {{content: "ドキュメント更新", status: "pending", activeForm: "更新中"}}
]}}  # 8個以上

または自動生成ツールを使用:
```bash
python .claude/scripts/auto-todowrite-generator.py --message "タスク内容"
```""",

                "explanation": """
【重要】TodoWriteは必ず8-10個の詳細タスクに分解する

理由:
- タスクの明確化
- 進捗の可視化
- 抜け漏れ防止

違反時のペナルティ: -10点
""",
                "auto_fixable": False
            },

            # 違反3: Byterover retrieve未実行
            "missing_byterover_retrieve": {
                "wrong": """❌ 違反パターン:
# タスク開始
Task("Analyst", "分析開始", "analyst")  # Byterover検索なし""",

                "correct": """✅ 正しいパターン:
[Single Message]:
  byterover-retrieve-knowledge  # 必ず最初に実行
  Task("Analyst", "過去知識を踏まえて分析開始", "analyst")""",

                "explanation": """
【重要】タスク開始前に必ずByterover知識検索を実行する

理由:
- 過去の類似タスクから学習
- 既知の問題を回避
- 車輪の再発明を防止

違反時のペナルティ: -15点
""",
                "auto_fixable": False
            },

            # 違反4: Byterover store未実行
            "missing_byterover_store": {
                "wrong": """❌ 違反パターン:
# 作業完了
git add .
git commit -m "完了"  # Byterover保存なし""",

                "correct": """✅ 正しいパターン:
# 作業完了
byterover-store-knowledge  # 必ず保存
git add .
git commit -m "完了" """,

                "explanation": """
【重要】タスク完了後に必ずByterover知識保存を実行する

理由:
- 学習内容の蓄積
- 将来のタスクで活用
- チーム知識の共有

違反時のペナルティ: -15点
""",
                "auto_fixable": False
            },

            # 違反5: 逐次実行
            "sequential_execution": {
                "wrong": """❌ 違反パターン:
Message 1: Read file1.lkml
Message 2: Read file2.lkml
Message 3: Task("Analyst", "分析", "analyst")  # 逐次実行""",

                "correct": """✅ 正しいパターン:
[Single Message]:  # 並列実行
  Read "file1.lkml"
  Read "file2.lkml"
  Task("Analyst", "分析", "analyst")""",

                "explanation": """
【重要】並列実行可能な操作は必ず1メッセージで実行する

理由:
- 実行速度の向上
- リソース効率化
- 並列処理の推奨

違反時のペナルティ: -20点
""",
                "auto_fixable": False
            },

            # 違反6: Seraphina相談なし
            "missing_seraphina": {
                "wrong": """❌ 違反パターン:
# 複雑度スコア: 50以上
Task("Analyst 1", "分析", "analyst")
Task("Analyst 2", "分析", "analyst")
# ... 複雑なタスク ...
# Seraphina相談なし""",

                "correct": """✅ 正しいパターン:
# 複雑度スコア50以上の場合
[Single Message]:
  byterover-retrieve-knowledge
  Task("Seraphina", "複雑なタスクの戦略立案", "consultant")
  # ↓ Seraphina の提案を待つ
  Task("Analyst 1", "Seraphina の提案に基づき分析", "analyst")
  Task("Analyst 2", "分析", "analyst")

または自動相談システムを使用:
```bash
python .claude/scripts/seraphina-auto-consult.py --task "タスク内容"
```""",

                "explanation": """
【重要】複雑度スコア50以上の場合、必ずSeraphina相談を実行する

複雑度スコア計算式:
- ファイル数 × 5点
- エージェント数 × 10点
- 複雑キーワード × 5点

理由:
- 複雑なタスクの戦略立案
- リスク評価
- 最適なアプローチの提案

違反時のペナルティ: -20点
""",
                "auto_fixable": False
            },

            # 違反7: ルートディレクトリへのファイル作成
            "root_file_creation": {
                "wrong": """❌ 違反パターン:
Write "README.md"  # ルートディレクトリに作成""",

                "correct": """✅ 正しいパターン:
# ドキュメントは docs/ 配下に作成
Write "docs/README.md"

# 設定ファイルは .claude/ 配下
Write ".claude/config.yaml"

# スクリプトは scripts/ 配下
Write "scripts/setup.py"

【重要】ルートディレクトリへの直接作成は禁止
- ファイル構造の混乱を防止
- プロジェクトの整理整頓
- 明確なディレクトリ構造の維持""",

                "explanation": """
【重要】ルートディレクトリに直接ファイルを作成しない

理由:
- ファイル構造の混乱を防止
- プロジェクトの整理整頓
- 明確なディレクトリ構造の維持

違反時のペナルティ: -25点（重大違反）
""",
                "auto_fixable": True  # パス変換で自動修正可能
            },

            # 違反8: ビジネスロジック判断でGemini未使用
            "no_gemini_validation": {
                "wrong": """❌ 違反パターン:
# ビジネスロジック判断
User: "要件Aと要件Bのどちらを優先しますか？"
Assistant: "要件Aを優先します"  # Gemini相談なし""",

                "correct": """✅ 正しいパターン:
[Single Message]:
  Task("Gemini", "要件AとBの優先度をビジネス観点で評価", "business_analyst")
  # ↓ Geminiの評価を待つ
  Task("Codex", "Geminiの評価を踏まえて実装", "coder")""",

                "explanation": """
【重要】ビジネスロジック・要件判断は必ずGeminiに相談する

対象キーワード:
- business, requirement, logic
- ビジネス、要件、判断
- 優先度、妥当性

理由:
- ビジネス観点の専門知識
- 要件の妥当性検証
- リスク評価

違反時のペナルティ: -10点
""",
                "auto_fixable": False
            },

            # 違反9: サンプルデータの明示なし
            "sample_data_confusion": {
                "wrong": """❌ 違反パターン:
User: "データを見せて"
Assistant:
{{
  "user_id": 123,
  "name": "Test User",
  "score": 85
}}  # サンプルデータだが明示なし""",

                "correct": """✅ 正しいパターン:
User: "データを見せて"
Assistant:

━━━━━━━━━━━━━━━━━━━━━━
⚠️ データ種別: サンプルデータ
出所: テスト用に手動作成
実データではありません
━━━━━━━━━━━━━━━━━━━━━━

{{
  "data_type": "SAMPLE",
  "source": "manually_created_for_testing",
  "note": "これはサンプルデータです",
  "data": {{
    "user_id": 123,
    "name": "Test User",
    "score": 85
  }}
}}

【重要】実データとサンプルデータを明確に区別
- ⚠️マークで明示
- data_type フィールド追加
- source を明記
""",

                "explanation": """
【重要】サンプルデータと実データを明確に区別する

必須表示:
⚠️ これは**サンプルデータ**です（動作確認用）
実際のデータソースから取得したものではありません。

理由:
- ユーザーの誤解を防止
- データの信頼性確保
- 意思決定の正確性

違反時のペナルティ: -50点（最重大違反）
""",
                "auto_fixable": False
            }
        }

    def suggest(self, violation_type: str, context: Optional[Dict] = None) -> Optional[CorrectionSuggestion]:
        """
        違反タイプに応じた修正案を生成

        Args:
            violation_type: 違反タイプ
            context: コンテキスト情報（オプション）

        Returns:
            修正提案オブジェクト
        """
        pattern = self.correction_patterns.get(violation_type)
        if not pattern:
            return None

        # コンテキスト情報で置換（該当する場合）
        wrong = pattern['wrong']
        correct = pattern['correct']
        explanation = pattern['explanation']

        if context:
            wrong = wrong.format(**context)
            correct = correct.format(**context)
            explanation = explanation.format(**context)

        return CorrectionSuggestion(
            violation_type=violation_type,
            wrong_pattern=wrong,
            correct_pattern=correct,
            explanation=explanation,
            auto_fixable=pattern.get('auto_fixable', False)
        )

    def display_suggestion(self, suggestion: CorrectionSuggestion, use_color: bool = True):
        """
        修正提案を表示（カラー出力）

        Args:
            suggestion: 修正提案
            use_color: カラー出力を使用するか
        """
        if not COLORAMA_AVAILABLE or not use_color:
            self._display_plain(suggestion)
            return

        print()
        print(Fore.RED + Back.BLACK + Style.BRIGHT + "=" * 80)
        print(Fore.YELLOW + Style.BRIGHT + f"🚨 違反検出: {suggestion.violation_type}")
        print(Fore.RED + Back.BLACK + Style.BRIGHT + "=" * 80)
        print()

        # 間違ったパターン
        print(Fore.RED + Style.BRIGHT + "❌ 間違ったパターン:")
        print(Fore.RED + suggestion.wrong_pattern)
        print()

        # 正しいパターン
        print(Fore.GREEN + Style.BRIGHT + "✅ 正しいパターン:")
        print(Fore.GREEN + suggestion.correct_pattern)
        print()

        # 説明
        print(Fore.CYAN + Style.BRIGHT + "📖 詳細説明:")
        print(Fore.CYAN + suggestion.explanation)
        print()

        # 自動修正可能か
        if suggestion.auto_fixable:
            print(Fore.MAGENTA + Style.BRIGHT + "🔧 この違反は自動修正可能です")
            print(Fore.MAGENTA + "   修正を適用しますか？ [Y/n]")
        else:
            print(Fore.YELLOW + Style.BRIGHT + "⚠️  この違反は手動修正が必要です")

        print(Fore.WHITE + Back.BLACK + Style.BRIGHT + "=" * 80)
        print()

    def _display_plain(self, suggestion: CorrectionSuggestion):
        """
        修正提案を表示（プレーンテキスト）

        Args:
            suggestion: 修正提案
        """
        print()
        print("=" * 80)
        print(f"違反検出: {suggestion.violation_type}")
        print("=" * 80)
        print()

        print("❌ 間違ったパターン:")
        print(suggestion.wrong_pattern)
        print()

        print("✅ 正しいパターン:")
        print(suggestion.correct_pattern)
        print()

        print("説明:")
        print(suggestion.explanation)
        print()

        if suggestion.auto_fixable:
            print("[自動修正可能] 修正を適用しますか？ [Y/n]")
        else:
            print("[手動修正必要]")

        print("=" * 80)
        print()

    def get_all_suggestions(self) -> Dict[str, CorrectionSuggestion]:
        """
        全ての修正提案を取得

        Returns:
            違反タイプ -> 修正提案のマッピング
        """
        suggestions = {}
        for vtype in self.correction_patterns.keys():
            suggestions[vtype] = self.suggest(vtype)
        return suggestions

    def generate_correction_guide(self, output_path: str = "correction_guide.md"):
        """
        修正ガイドをMarkdown形式で生成

        Args:
            output_path: 出力ファイルパス
        """
        guide_content = """# 8-Layer Enforcement System - 修正ガイド

**自動生成日時**: {datetime}

このガイドは、CLAUDE.mdのルール違反に対する修正パターンを提供します。

---

"""
        import datetime as dt
        guide_content = guide_content.format(datetime=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        for idx, (vtype, pattern) in enumerate(self.correction_patterns.items(), 1):
            guide_content += f"""
## {idx}. {vtype}

### ❌ 間違ったパターン

```
{pattern['wrong']}
```

### ✅ 正しいパターン

```
{pattern['correct']}
```

### 📖 説明

{pattern['explanation']}

### 🔧 自動修正

{'✅ 可能' if pattern.get('auto_fixable') else '❌ 不可（手動修正必要）'}

---

"""

        output_file = Path(output_path)
        output_file.write_text(guide_content, encoding='utf-8')
        print(f"修正ガイドを生成しました: {output_file.absolute()}")


def main():
    """テスト実行"""
    # Windows環境でのUTF-8出力設定
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    suggester = AutoCorrectSuggester()

    # テストケース: 全違反タイプの修正提案を表示
    print()
    print(Fore.CYAN + Style.BRIGHT + "=" * 80 if COLORAMA_AVAILABLE else "=" * 80)
    print(Fore.CYAN + Style.BRIGHT + "8-Layer Enforcement System - 自動修正提案システム" if COLORAMA_AVAILABLE else "8-Layer Enforcement System - 自動修正提案システム")
    print(Fore.CYAN + Style.BRIGHT + "=" * 80 if COLORAMA_AVAILABLE else "=" * 80)
    print()

    violation_types = [
        "no_codex_collaboration",
        "insufficient_todowrite",
        "missing_byterover_retrieve",
        "sample_data_confusion"
    ]

    for vtype in violation_types:
        suggestion = suggester.suggest(vtype)
        if suggestion:
            suggester.display_suggestion(suggestion, use_color=COLORAMA_AVAILABLE)
            input("Enter キーで次の提案へ...")

    # Markdown ガイド生成
    print()
    print(Fore.GREEN + "Markdown修正ガイドを生成しますか？ [Y/n]: " if COLORAMA_AVAILABLE else "Markdown修正ガイドを生成しますか？ [Y/n]: ", end="")
    response = input().strip().lower()
    if response in ['y', 'yes', '']:
        output_path = Path(__file__).parent / "correction_guide.md"
        suggester.generate_correction_guide(str(output_path))

    print()
    print(Fore.GREEN + Style.BRIGHT + "[OK] テスト完了" if COLORAMA_AVAILABLE else "[OK] テスト完了")


if __name__ == "__main__":
    main()
