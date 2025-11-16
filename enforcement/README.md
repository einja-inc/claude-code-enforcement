# 8-Layer Enforcement System - Session Monitor

**Phase 1 実装完了 - リアルタイム違反検出システム**

## 概要

Claude Codeの会話ログ（`shell-snapshots/*.jsonl`）をリアルタイムで監視し、CLAUDE.mdで定義された9種類の違反パターンを検出します。

## 実装済みコンポーネント

### 1. `session_monitor.py` - メイン監視システム
- **機能**:
  - watchdogでファイル変更をリアルタイム検出
  - 増分読み込み（新規追加行のみ処理）
  - 違反検出・通知・スコアリングの統合
  - 統計情報の収集と表示

- **主要メソッド**:
  - `on_modified()`: ファイル変更時のイベントハンドラ
  - `on_created()`: 新規ファイル作成時のハンドラ
  - `analyze_new_lines()`: 新規追加行の分析
  - `process_log_entry()`: ログエントリの処理
  - `handle_violations()`: 違反処理（通知・スコア更新・ログ保存）

### 2. `violation_detector.py` - 違反検出エンジン
- **検出パターン（9種類）**:
  1. `no_codex_collaboration`: Codex協力なしでファイル編集
  2. `insufficient_todowrite`: TodoWrite項目数不足（8未満）
  3. `missing_byterover_retrieve`: タスク開始前のByterover検索なし
  4. `missing_byterover_store`: タスク完了後のByterover保存なし
  5. `sequential_execution`: 並列実行可能なTask()を逐次実行
  6. `missing_seraphina`: 複雑度50以上でSeraphina相談なし
  7. `root_file_creation`: ルートディレクトリにファイル作成
  8. `no_gemini_validation`: ビジネスロジック判断でGemini未使用
  9. `sample_data_confusion`: サンプルデータの明示なし（重大違反）

- **複雑度計算**:
  - ファイル数 × 5点
  - エージェント数 × 10点
  - 複雑なキーワード × 5点

### 3. `notification_manager.py` - 通知システム
- **対応通知方法**:
  - Windows Toast通知（win10toast使用）
  - コンソール出力（フォールバック）
  - VS Code通知（将来実装予定）

- **通知レベル**:
  - INFO: 情報
  - WARNING: 警告
  - ERROR: エラー（重大違反）

### 4. `compliance_scorer.py` - スコアリングシステム
- **初期スコア**: 100点
- **合格基準**: 70点以上
- **スコア減点**: 違反ごとに定義（config.yamlで設定可能）
- **履歴保存**: JSONL形式でスコア履歴を保存

### 5. `config.yaml` - 設定ファイル
```yaml
monitoring:
  log_directory: "C:/Users/musta/.claude/shell-snapshots"
  file_pattern: "session_*.jsonl"
  poll_interval: 0.1

notification:
  enabled: true
  method: "windows"  # or "console"
  levels:
    INFO: true
    WARNING: true
    ERROR: true

scoring:
  initial_score: 100
  minimum_passing: 70
  violations:
    no_codex_collaboration: -20
    # ... (他の違反スコア)
```

## セットアップ

### 必須要件
- Python 3.8以上
- Windows 10/11（Toast通知の場合）

### インストール
```bash
# 依存パッケージインストール
cd C:\Users\musta\.claude\enforcement
pip install -r requirements.txt

# requirements.txt:
# watchdog==3.0.0
# PyYAML==6.0.1
# win10toast==0.9  # 任意（Windows Toast通知用）
```

### ディレクトリ構造
```
C:\Users\musta\.claude\enforcement\
├── session_monitor.py          # メイン監視システム
├── violation_detector.py       # 違反検出エンジン
├── notification_manager.py     # 通知管理
├── compliance_scorer.py        # スコアリング
├── config.yaml                 # 設定ファイル
├── requirements.txt            # 依存パッケージ
├── README.md                   # このファイル
├── logs/                       # ログディレクトリ
│   ├── violations.jsonl        # 違反ログ
│   ├── compliance_scores.jsonl # スコアログ
│   └── service.log             # サービスログ
└── daemon/                     # デーモン化（Phase 2）
```

## 使用方法

### 基本的な使い方

#### 1. 監視を開始
```bash
cd C:\Users\musta\.claude\enforcement
python session_monitor.py
```

**出力例**:
```
======================================================================
🚀 8-Layer Enforcement System - Session Monitor Started
======================================================================
📂 Monitoring: C:\Users\musta\.claude\shell-snapshots
📊 Initial Compliance Score: 100%
⏳ Watching for violations...
   Press Ctrl+C to stop
======================================================================
```

#### 2. Claude Codeを使用
- 通常通りClaude Codeを使用
- 違反が検出されると自動的に通知される

#### 3. 違反検出時の出力例
```
======================================================================
[ERROR] no_codex_collaboration
----------------------------------------------------------------------
メッセージ: Codex協力なしでファイル編集を検出
スコア影響: -20
現在スコア: 80%
ファイル: session_20251115_123456.jsonl (Line 42)
======================================================================
```

#### 4. 停止
- `Ctrl+C` で停止
- 最終統計が表示される

### カスタム設定ファイルの使用
```bash
python session_monitor.py /path/to/custom_config.yaml
```

## テスト

### 単体テスト実行
```bash
cd C:\Users\musta\.claude\enforcement
pytest tests/ -v
```

### 手動テスト
```python
# test_session_monitor.py
import sys
sys.stdout.reconfigure(encoding='utf-8')

from session_monitor import SessionMonitor

# 初期化テスト
monitor = SessionMonitor('config.yaml')
print(f"Current score: {monitor.scorer.get_current_score()}%")

# 統計情報表示
monitor.print_stats()
```

## 違反スコア一覧

| 違反タイプ | スコア減点 | 重要度 | 説明 |
|----------|-----------|-------|------|
| `sample_data_confusion` | -50点 | ERROR | サンプルデータを実データとして提示（最重大） |
| `root_file_creation` | -25点 | ERROR | ルートディレクトリにファイル作成 |
| `no_codex_collaboration` | -20点 | ERROR | Codex協力なしでファイル編集 |
| `sequential_execution` | -20点 | ERROR | 並列実行可能なTask()を逐次実行 |
| `missing_seraphina` | -20点 | ERROR | 複雑度50以上でSeraphina相談なし |
| `missing_byterover_retrieve` | -15点 | WARNING | タスク開始前のByterover検索なし |
| `missing_byterover_store` | -15点 | WARNING | タスク完了後のByterover保存なし |
| `insufficient_todowrite` | -10点 | WARNING | TodoWrite項目数不足（8未満） |
| `no_gemini_validation` | -10点 | WARNING | ビジネスロジック判断でGemini未使用 |

## ログファイル

### 違反ログ (`logs/violations.jsonl`)
```json
{
  "timestamp": 1700012345.678,
  "datetime": "2025-11-15T12:34:56",
  "type": "no_codex_collaboration",
  "severity": "ERROR",
  "score_impact": -20,
  "current_score": 80,
  "message": "Codex協力なしでファイル編集を検出",
  "context": "Edit \"test.lkml\"...",
  "line_number": 42,
  "file": "session_20251115_123456.jsonl"
}
```

### スコアログ (`logs/compliance_scores.jsonl`)
```json
{
  "timestamp": 1700012345.678,
  "event": "session_start",
  "score": 100
}
{
  "timestamp": 1700012350.123,
  "event": "violation:no_codex_collaboration",
  "score": 80
}
```

## トラブルシューティング

### Q: win10toastのインポートエラー
**A**: 任意パッケージです。インストールしない場合はコンソール通知になります。
```bash
pip install win10toast
```

### Q: 設定ファイルが見つからない
**A**: session_monitor.pyと同じディレクトリにconfig.yamlを配置してください。

### Q: ログディレクトリが存在しない
**A**: 自動作成されます。権限エラーの場合は手動作成してください。
```bash
mkdir C:\Users\musta\.claude\enforcement\logs
```

### Q: 文字化けする
**A**: UTF-8エンコーディングを設定してください。
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

## パフォーマンス

- **CPU使用率**: < 5%（目標）
- **メモリ使用量**: < 100MB（目標）
- **検出遅延**: < 100ms（ほぼリアルタイム）

## 次のステップ（Phase 2以降）

- [ ] デーモン化（バックグラウンド実行）
- [ ] Windowsタスクスケジューラ統合
- [ ] VS Code拡張機能統合
- [ ] AI監査エージェント（MCP Codex使用）
- [ ] Git pre-commit hook統合
- [ ] レポート生成機能

## ライセンス

内部使用のみ

## 作成者

8-Layer Enforcement System Team
作成日: 2025-11-15
