# Layer 7: 自動修正提案システム

**バージョン**: 1.0.0
**最終更新**: 2025-11-15
**目的**: 違反検出時に正しいパターンを自動提示し、修正を支援する

---

## 📋 概要

Layer 7 自動修正提案システムは、CLAUDE.mdのルール違反を検出した際に、正しいコーディングパターンを自動的に提示します。

### 主な機能

1. **9種類の違反パターンごとの修正テンプレート**
2. **❌ WRONG vs ✅ CORRECT の比較表示**
3. **カラー出力による視認性向上**
4. **violation_detector.py との統合**
5. **Markdownレポート生成**

---

## 🚀 クイックスタート

### 1. 基本的な使用方法

```bash
# 自動修正提案システムのテスト実行
cd C:\Users\musta\.claude\enforcement
python auto_correct_suggestions.py
```

**出力例**:
```
================================================================================
🚨 違反検出: no_codex_collaboration
================================================================================

❌ 間違ったパターン:
Read "file.lkml"
Edit "file.lkml"  # Codex協力なし

✅ 正しいパターン:
[Single Message]:
  Read "file.lkml"
  Task("Codex Analyst", "ファイル構造を分析", "analyst")
  Edit "file.lkml"

📖 説明:
単一ファイルの修正であっても、必ずCodex協力が必要
ペナルティ: -20点
================================================================================
```

### 2. 統合システムでの使用

```bash
# テキストを直接分析
python integrated_correction.py --text "Edit 'test.lkml'"

# ファイルを分析
python integrated_correction.py --file "sample.txt"

# 会話ログを分析
python integrated_correction.py --log "C:\Users\musta\.claude\shell-snapshots\session_20251115.jsonl"

# レポート生成付き
python integrated_correction.py --text "Edit 'test.lkml'" --report
```

---

## 📚 ファイル構成

```
C:\Users\musta\.claude\enforcement\
├── auto_correct_suggestions.py    # Layer 7 メインモジュール
├── integrated_correction.py       # 統合システム
├── violation_detector.py          # Layer 5 違反検出
├── config.yaml                    # 設定ファイル
├── correction_guide.md            # 自動生成される修正ガイド
└── README_AUTO_CORRECTION.md      # このファイル
```

---

## 🔍 対応違反パターン

| No. | 違反タイプ | ペナルティ | 自動修正 |
|-----|----------|----------|---------|
| 1 | `no_codex_collaboration` | -20点 | ❌ 手動 |
| 2 | `insufficient_todowrite` | -10点 | ❌ 手動 |
| 3 | `missing_byterover_retrieve` | -15点 | ❌ 手動 |
| 4 | `missing_byterover_store` | -15点 | ❌ 手動 |
| 5 | `sequential_execution` | -20点 | ❌ 手動 |
| 6 | `missing_seraphina` | -20点 | ❌ 手動 |
| 7 | `root_file_creation` | -25点 | ✅ 自動 |
| 8 | `no_gemini_validation` | -10点 | ❌ 手動 |
| 9 | `sample_data_confusion` | -50点 | ❌ 手動 |

---

## 💻 API リファレンス

### AutoCorrectSuggester クラス

#### メソッド

##### `suggest(violation_type: str, context: Optional[Dict] = None) -> CorrectionSuggestion`

違反タイプに応じた修正提案を生成します。

**パラメータ**:
- `violation_type` (str): 違反タイプ（例: `"no_codex_collaboration"`）
- `context` (dict, optional): コンテキスト情報（プレースホルダー置換用）

**戻り値**:
- `CorrectionSuggestion`: 修正提案オブジェクト

**例**:
```python
from auto_correct_suggestions import AutoCorrectSuggester

suggester = AutoCorrectSuggester()
suggestion = suggester.suggest("no_codex_collaboration")
suggester.display_suggestion(suggestion)
```

##### `display_suggestion(suggestion: CorrectionSuggestion, use_color: bool = True)`

修正提案をカラー出力で表示します。

**パラメータ**:
- `suggestion` (CorrectionSuggestion): 修正提案
- `use_color` (bool): カラー出力を使用するか（デフォルト: True）

##### `generate_correction_guide(output_path: str = "correction_guide.md")`

全ての修正パターンをまとめたMarkdownガイドを生成します。

**パラメータ**:
- `output_path` (str): 出力ファイルパス

**例**:
```python
suggester = AutoCorrectSuggester()
suggester.generate_correction_guide("my_guide.md")
```

---

### IntegratedCorrectionSystem クラス

#### メソッド

##### `analyze_and_suggest(content: str, show_suggestions: bool = True) -> Dict`

コンテンツを分析し、違反があれば修正提案を表示します。

**パラメータ**:
- `content` (str): 分析対象のテキスト
- `show_suggestions` (bool): 修正提案を表示するか

**戻り値**:
- `dict`: 分析結果
  ```python
  {
      'violations': [Violation, ...],
      'violation_count': int,
      'compliance_score': int,  # 0-100
      'suggestions': [CorrectionSuggestion, ...]
  }
  ```

**例**:
```python
from integrated_correction import IntegratedCorrectionSystem

system = IntegratedCorrectionSystem()
result = system.analyze_and_suggest("Edit 'test.lkml'")

print(f"スコア: {result['compliance_score']}%")
print(f"違反数: {result['violation_count']}")
```

##### `analyze_file(filepath: str) -> Dict`

ファイルを分析します。

##### `analyze_conversation_log(log_file: str) -> Dict`

Claude Code会話ログ（JSONL形式）を分析します。

##### `generate_report(result: Dict, output_path: str = "compliance_report.md")`

コンプライアンスレポートをMarkdown形式で生成します。

**例**:
```python
system = IntegratedCorrectionSystem()
result = system.analyze_file("sample.txt")
system.generate_report(result, "report.md")
```

---

## 🎨 カラー出力

coloramaライブラリを使用してカラー出力を実装しています。

### インストール

```bash
pip install colorama
```

### カラーなしで実行

```python
suggester.display_suggestion(suggestion, use_color=False)
```

---

## 📊 出力例

### 違反検出とコンプライアンススコア

```
================================================================================
🔍 違反検出: 3件
================================================================================

[ERROR] no_codex_collaboration
メッセージ: Codex協力なしでファイル編集を検出
スコア影響: -20
行番号: 0
--------------------------------------------------------------------------------

[WARNING] insufficient_todowrite
メッセージ: TodoWrite項目数が8未満（現在: 1個）
スコア影響: -10
行番号: 0
--------------------------------------------------------------------------------

[ERROR] sample_data_confusion
メッセージ: サンプルデータの明示なし（重大違反）
スコア影響: -50
行番号: 0
--------------------------------------------------------------------------------

================================================================================
分析サマリー
================================================================================
コンプライアンススコア: 20%
違反件数: 3
修正提案数: 3

❌ 評価: FAIL（コミットブロック対象）
================================================================================
```

---

## 🔗 session_monitor.py との統合

Layer 5（Session監視）と統合することで、リアルタイムに修正提案を表示できます。

### session_monitor.py への統合例

```python
# session_monitor.py の修正箇所

from auto_correct_suggestions import AutoCorrectSuggester

class SessionMonitor:
    def __init__(self):
        # ... 既存の初期化 ...
        self.suggester = AutoCorrectSuggester()

    def handle_violations(self, violations: list, context: dict):
        """違反処理（修正提案付き）"""
        for name, config in violations:
            # スコア更新
            self.current_session_score += config['score']

            # 通知送信
            send_notification(...)

            # ✅ 修正提案を自動表示
            suggestion = self.suggester.suggest(name)
            if suggestion:
                self.suggester.display_suggestion(suggestion)
```

---

## 📈 評価基準

### コンプライアンススコア

- **95-100%**: ✅ PERFECT（模範的）
- **75-94%**: ✅ GOOD（良好）
- **50-74%**: ⚠️ WARNING（要改善）
- **0-49%**: ❌ FAIL（コミットブロック対象）

---

## 🛠️ カスタマイズ

### 新しい違反パターンの追加

`auto_correct_suggestions.py` の `_load_correction_patterns()` メソッドに追加します。

```python
def _load_correction_patterns(self) -> Dict[str, Dict]:
    return {
        # 既存のパターン...

        # 新しいパターン
        "custom_violation": {
            "wrong": """❌ 間違ったパターン:
...""",

            "correct": """✅ 正しいパターン:
...""",

            "explanation": """説明...""",

            "auto_fixable": False
        }
    }
```

---

## 🐛 トラブルシューティング

### Q1: coloramaが見つからないエラー

```bash
pip install colorama
```

### Q2: 文字化けする

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

### Q3: 修正提案が表示されない

```python
# show_suggestions=True を確認
result = system.analyze_and_suggest(content, show_suggestions=True)
```

---

## 📝 使用例

### 例1: 単純な違反チェック

```python
from auto_correct_suggestions import AutoCorrectSuggester

suggester = AutoCorrectSuggester()

# Codex協力なし違反の修正提案
suggestion = suggester.suggest("no_codex_collaboration")
suggester.display_suggestion(suggestion)
```

### 例2: 複数違反の一括チェック

```python
from integrated_correction import IntegratedCorrectionSystem

system = IntegratedCorrectionSystem()

test_code = """
Edit "test.lkml"
TodoWrite { todos: [{content: "修正", status: "pending", activeForm: "修正中"}]}
sample data: {"id": 123}
"""

result = system.analyze_and_suggest(test_code)
system.generate_report(result, "report.md")
```

### 例3: 会話ログの定期分析

```python
from pathlib import Path
from integrated_correction import IntegratedCorrectionSystem

system = IntegratedCorrectionSystem()

# 最新の会話ログを分析
logs_dir = Path(r"C:\Users\musta\.claude\shell-snapshots")
latest_log = max(logs_dir.glob("session_*.jsonl"), key=lambda p: p.stat().st_mtime)

result = system.analyze_conversation_log(str(latest_log))

if result['compliance_score'] < 70:
    print("⚠️ コンプライアンススコアが低下しています")
    system.generate_report(result, "urgent_report.md")
```

---

## 🔄 今後の拡張予定

### Phase 4+

1. **自動修正適用機能**
   - ユーザーの承認を得て、自動的にコードを修正
   - `root_file_creation` など、パターンが明確な違反に対応

2. **VS Code Quickfix統合**
   - VS Codeのコードアクションとして修正提案を表示
   - ショートカットキーで即座に修正適用

3. **学習機能**
   - ユーザーの修正パターンを学習
   - カスタム修正テンプレートの自動生成

---

## 📞 サポート

**問題報告**: `C:\Users\musta\.claude\enforcement\logs\service.log` を確認
**機能要望**: `.claude/enforcement/config.yaml` でカスタマイズ可能

---

**次のステップ**: [Phase 1実装ガイド](../docs/8-LAYER-SYSTEM-ARCHITECTURE.md) を参照
