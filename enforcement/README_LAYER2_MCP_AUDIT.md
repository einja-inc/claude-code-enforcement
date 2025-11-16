# Layer 2: MCP監査エージェント（AI分析）

**バージョン**: 1.0.0
**最終更新**: 2025-11-15

---

## 📋 概要

Claude APIを使用して会話ログをAI分析し、正規表現では検出困難な複雑な違反パターンを検出するシステム。

### 主要機能

- **AI分析**: Claude Sonnet 4.5による会話ログの文脈理解
- **9種類の違反検出**: Codex協力不足、TodoWrite不足、並列実行漏れ等
- **バッチ処理**: 5分ごとの定期分析（設定可能）
- **レート制限**: 1分間に3リクエスト以下に自動調整
- **サマリーレポート**: 分析結果の統計・推奨事項生成

---

## 🎯 検出される9種類の違反パターン

| 違反タイプ | スコア減点 | 説明 |
|-----------|-----------|------|
| **no_codex_collaboration** | -20点 | Codex協力なしでファイル編集 |
| **insufficient_todowrite** | -10点 | TodoWrite項目数が8未満 |
| **missing_byterover_retrieve** | -15点 | タスク開始前のByterover検索なし |
| **missing_byterover_store** | -15点 | タスク完了後のByterover保存なし |
| **sequential_execution** | -20点 | 並列実行可能なTask()を逐次実行 |
| **missing_seraphina** | -20点 | 複雑度50以上でSeraphina相談なし |
| **root_file_creation** | -25点 | ルートディレクトリにファイル作成 |
| **no_gemini_validation** | -10点 | ビジネスロジック判断でGemini未使用 |
| **sample_data_confusion** | -50点 | サンプルデータの明示なし |

---

## 🚀 セットアップ

### 1. 依存パッケージのインストール

```bash
pip install anthropic apscheduler psutil
```

### 2. APIキーの設定

**Windows（永続設定）:**

```cmd
setx ANTHROPIC_API_KEY "your-api-key-here"
```

**一時設定（現在のセッションのみ）:**

```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

**確認:**

```cmd
echo %ANTHROPIC_API_KEY%
```

### 3. 動作確認

```bash
python C:\Users\musta\.claude\enforcement\mcp_audit_agent.py --help
```

---

## 💻 使用方法

### 方法1: バッチファイル（推奨）

#### 起動

```cmd
C:\Users\musta\.claude\enforcement\start-ai-audit.bat
```

**カスタム間隔で起動:**

```cmd
C:\Users\musta\.claude\enforcement\start-ai-audit.bat 10
# → 10分ごとに監査
```

#### 停止

```cmd
C:\Users\musta\.claude\enforcement\stop-ai-audit.bat
```

#### ステータス確認

```cmd
C:\Users\musta\.claude\enforcement\status-ai-audit.bat
```

### 方法2: Pythonコマンド

#### 定期監査開始（5分間隔）

```bash
python C:\Users\musta\.claude\enforcement\scheduled_audit.py start
```

#### 定期監査開始（カスタム間隔）

```bash
python C:\Users\musta\.claude\enforcement\scheduled_audit.py start --interval 10
# → 10分ごと
```

#### 停止

```bash
python C:\Users\musta\.claude\enforcement\scheduled_audit.py stop
```

#### ステータス確認

```bash
python C:\Users\musta\.claude\enforcement\scheduled_audit.py status
```

### 方法3: 単発分析（テスト用）

#### 特定のセッションファイルを分析

```bash
python C:\Users\musta\.claude\enforcement\mcp_audit_agent.py --session-file C:\Users\musta\.claude\shell-snapshots\session_20251115_143022.jsonl
```

#### 過去24時間のセッションをバッチ分析

```bash
python C:\Users\musta\.claude\enforcement\mcp_audit_agent.py --batch
```

#### 過去12時間のセッションをバッチ分析

```bash
python C:\Users\musta\.claude\enforcement\mcp_audit_agent.py --batch --lookback-hours 12
```

---

## 📊 出力ファイル

### 1. 監査結果ログ

**場所**: `C:\Users\musta\.claude\enforcement\logs\ai_audit_results.jsonl`

**形式**: JSONL（1行1セッションの分析結果）

**例**:

```json
{
  "violations": [
    {
      "type": "no_codex_collaboration",
      "severity": "high",
      "message": "LookMLファイルをCodex協力なしで編集",
      "line_number": 42,
      "context": "Edit financial_metrics.view.lkml"
    }
  ],
  "compliance_score": 80,
  "total_violations": 1,
  "recommendations": [
    "次回はCodex analystと協力してファイル構造を分析してください"
  ],
  "session_summary": "LookML修正タスク。Codex協力が不足。",
  "session_id": "session_20251115_143022",
  "analyzed_at": "2025-11-15T14:35:10",
  "model": "claude-sonnet-4-5-20250929"
}
```

### 2. サービスログ

**場所**: `C:\Users\musta\.claude\enforcement\logs\scheduled_audit.log`

**形式**: テキストログ

**内容**: 起動・停止・監査実行・エラーの記録

### 3. ステータスファイル

**場所**: `C:\Users\musta\.claude\enforcement\scheduled_audit_status.json`

**形式**: JSON

**例**:

```json
{
  "state": "running",
  "updated_at": "2025-11-15T14:40:00",
  "last_audit": {
    "timestamp": "2025-11-15T14:40:00",
    "sessions_analyzed": 3,
    "average_score": 85.3,
    "total_violations": 4,
    "violation_breakdown": {
      "no_codex_collaboration": 2,
      "insufficient_todowrite": 1,
      "sequential_execution": 1
    }
  }
}
```

---

## 🔧 トラブルシューティング

### 問題1: APIキーエラー

**エラーメッセージ**:

```
ValueError: ANTHROPIC_API_KEY環境変数が設定されていません
```

**解決策**:

1. APIキーを設定:
   ```cmd
   setx ANTHROPIC_API_KEY "sk-ant-..."
   ```

2. 新しいターミナルを開いて再実行

3. 確認:
   ```cmd
   echo %ANTHROPIC_API_KEY%
   ```

### 問題2: モジュールが見つからない

**エラーメッセージ**:

```
ModuleNotFoundError: No module named 'anthropic'
```

**解決策**:

```bash
pip install anthropic apscheduler psutil
```

### 問題3: レート制限エラー

**エラーメッセージ**:

```
anthropic.RateLimitError: Rate limit exceeded
```

**現象**: APIコールが多すぎる

**解決策**:

- 自動的に待機されるため、しばらく待つ
- 間隔を長くする:
  ```bash
  python scheduled_audit.py start --interval 10
  ```

### 問題4: サービスが既に起動中

**エラーメッセージ**:

```
⚠️ Scheduled Audit Service は既に起動中です
```

**解決策**:

1. ステータス確認:
   ```bash
   python scheduled_audit.py status
   ```

2. 停止してから再起動:
   ```bash
   python scheduled_audit.py stop
   python scheduled_audit.py start
   ```

3. または:
   ```bash
   python scheduled_audit.py restart
   ```

### 問題5: セッションログが見つからない

**エラーメッセージ**:

```
WARNING セッションログディレクトリが存在しません
```

**原因**: Claude Codeをまだ使用していない

**解決策**:

- Claude Codeを起動して何か会話する
- `C:\Users\musta\.claude\shell-snapshots\` にログファイルが作成される
- その後、監査を実行

---

## 📈 パフォーマンス

### レート制限

- **制限**: 1分間に3リクエスト
- **自動待機**: 制限に達すると自動的に待機
- **推奨間隔**: 5分（デフォルト）

### リソース使用量

- **CPU**: 分析中 ~10%, 待機中 < 1%
- **メモリ**: ~50MB
- **ネットワーク**: 1リクエストあたり ~10KB

### 分析速度

- **1セッション**: 約5-10秒
- **バッチ（5セッション）**: 約30-60秒（待機時間含む）

---

## 🔗 Session Monitorとの統合

Layer 2（AI分析）とLayer 5（リアルタイム監視）の役割分担:

| 機能 | Layer 5 (Session Monitor) | Layer 2 (MCP Audit Agent) |
|------|---------------------------|---------------------------|
| **検出方法** | 正規表現パターンマッチング | AIによる文脈理解 |
| **実行タイミング** | リアルタイム（即座） | 定期バッチ（5分ごと） |
| **検出精度** | シンプルなパターンのみ | 複雑なパターンも検出 |
| **レスポンス** | 100ms以内 | 5-10秒 |
| **用途** | 即座のフィードバック | 詳細な事後分析 |

**推奨**: 両方を併用することで最大の効果

---

## 🎓 使用例

### 例1: 開発開始時

```bash
# 1. 定期監査を起動（バックグラウンド）
start-ai-audit.bat

# 2. Claude Codeで開発
#    → 5分ごとに自動分析

# 3. ステータス確認（いつでも）
status-ai-audit.bat
```

### 例2: 過去のセッションを振り返る

```bash
# 昨日のセッションを全て分析
python mcp_audit_agent.py --batch --lookback-hours 24
```

### 例3: 特定のセッションだけ詳細分析

```bash
# セッションファイルを見つける
dir C:\Users\musta\.claude\shell-snapshots\session_*.jsonl

# 特定のセッションを分析
python mcp_audit_agent.py --session-file C:\Users\musta\.claude\shell-snapshots\session_20251115_143022.jsonl
```

---

## 📚 関連ドキュメント

- **アーキテクチャ設計**: `C:\Users\musta\Desktop\PJ\いいんじゃ\フォーム分析\docs\8-LAYER-SYSTEM-ARCHITECTURE.md`
- **Layer 5 (Session Monitor)**: `C:\Users\musta\.claude\enforcement\README_LAYER5_SESSION_MONITOR.md`
- **CLAUDE.md**: `C:\Users\musta\.claude\CLAUDE.md`

---

## 🔄 更新履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2025-11-15 | 1.0.0 | 初版リリース |

---

## 📧 サポート

**ログ確認**:

```bash
type C:\Users\musta\.claude\enforcement\logs\scheduled_audit.log
```

**デバッグモード**:

```bash
set ENFORCEMENT_DEBUG=1
python scheduled_audit.py start
```

---

**次のステップ**: [Phase 4: Layer 7 自動修正提案システム](./README_LAYER7_AUTO_CORRECTION.md)
