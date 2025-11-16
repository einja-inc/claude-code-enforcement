# Layer 2: MCP監査エージェント クイックスタートガイド

**最短5分で起動できるセットアップガイド**

---

## 🚀 5分セットアップ

### Step 1: APIキー設定（2分）

```cmd
setx ANTHROPIC_API_KEY "sk-ant-api03-your-key-here"
```

**重要**: 新しいターミナルを開く（既存のターミナルでは反映されない）

**確認**:
```cmd
echo %ANTHROPIC_API_KEY%
```

### Step 2: 依存パッケージインストール（2分）

```cmd
pip install anthropic apscheduler psutil
```

### Step 3: テスト実行（1分）

```cmd
cd C:\Users\musta\.claude\enforcement
python test_mcp_audit.py
```

**期待される出力**:
```
✅ PASS - api_key
✅ PASS - import
✅ PASS - initialization
✅ PASS - violation_detection
✅ PASS - good_session
✅ PASS - rate_limiter
✅ PASS - log_files

結果: 7/7 テスト成功
🎉 全てのテストが成功しました！
```

---

## 💻 起動方法（3つの選択肢）

### 方法A: バッチファイル（最も簡単）

#### 起動
```cmd
C:\Users\musta\.claude\enforcement\start-ai-audit.bat
```

#### 停止
```cmd
C:\Users\musta\.claude\enforcement\stop-ai-audit.bat
```

#### ステータス確認
```cmd
C:\Users\musta\.claude\enforcement\status-ai-audit.bat
```

### 方法B: Pythonコマンド

```cmd
# 起動（5分間隔）
python C:\Users\musta\.claude\enforcement\scheduled_audit.py start

# 起動（10分間隔）
python C:\Users\musta\.claude\enforcement\scheduled_audit.py start --interval 10

# 停止
python C:\Users\musta\.claude\enforcement\scheduled_audit.py stop

# ステータス
python C:\Users\musta\.claude\enforcement\scheduled_audit.py status
```

### 方法C: デスクトップショートカット

1. `start-ai-audit.bat` を右クリック → **ショートカットを作成**
2. ショートカットをデスクトップに移動
3. ダブルクリックで起動

---

## 📊 動作確認

### 1. サービスが起動しているか確認

```cmd
status-ai-audit.bat
```

**期待される出力**:
```
========================================
Scheduled Audit Service ステータス
========================================
状態: RUNNING
最終更新: 2025-11-15 17:35:00
PID: 12345
監査間隔: 5分
最終監査: 2025-11-15 17:35:00
分析セッション数: 3
平均スコア: 85.5%
========================================
```

### 2. ログファイルを確認

```cmd
type C:\Users\musta\.claude\enforcement\logs\scheduled_audit.log
```

**期待される内容**:
```
2025-11-15 17:30:00 [INFO] 定期AI監査サービス起動中（間隔: 5分）...
2025-11-15 17:30:05 [INFO] サービス起動完了
2025-11-15 17:30:05 [INFO] 初回監査を実行します...
2025-11-15 17:30:10 [INFO] セッション分析開始: session_20251115_173000
2025-11-15 17:30:15 [INFO] 分析完了: 2件の違反検出 (スコア: 80%)
```

### 3. 監査結果を確認

```cmd
type C:\Users\musta\.claude\enforcement\logs\ai_audit_results.jsonl
```

**形式**: 1行1セッションのJSON

---

## 🎯 使い方（典型的なワークフロー）

### ワークフロー1: 日常開発

```
1. 朝: AI監査を起動
   → start-ai-audit.bat

2. 開発中: Claude Codeで作業
   → 5分ごとに自動分析

3. 昼休み: ステータス確認
   → status-ai-audit.bat

4. 夕方: 結果確認してコミット
   → git commit
   → Layer 1 (pre-commit hook) が自動実行
```

### ワークフロー2: 過去のセッション振り返り

```cmd
# 昨日の全セッションを分析
python mcp_audit_agent.py --batch --lookback-hours 24

# 結果を確認
type C:\Users\musta\.claude\enforcement\logs\ai_audit_results.jsonl | findstr "compliance_score"
```

### ワークフロー3: 特定セッションの詳細分析

```cmd
# セッションファイルを見つける
dir C:\Users\musta\.claude\shell-snapshots\session_*.jsonl /O-D

# 最新のセッションを分析
python mcp_audit_agent.py --session-file "C:\Users\musta\.claude\shell-snapshots\session_20251115_173000.jsonl"
```

---

## ⚠️ よくあるトラブル

### 問題1: "ModuleNotFoundError: No module named 'anthropic'"

**解決策**:
```cmd
pip install anthropic apscheduler psutil
```

### 問題2: "ANTHROPIC_API_KEY環境変数が設定されていません"

**解決策**:
```cmd
# 1. APIキー設定
setx ANTHROPIC_API_KEY "your-key-here"

# 2. 新しいターミナルを開く（重要！）

# 3. 確認
echo %ANTHROPIC_API_KEY%
```

### 問題3: "サービスは既に起動中です"

**解決策**:
```cmd
# 停止してから再起動
stop-ai-audit.bat
start-ai-audit.bat

# または
python scheduled_audit.py restart
```

### 問題4: "セッションログディレクトリが存在しません"

**原因**: Claude Codeをまだ使用していない

**解決策**:
1. Claude Codeを起動
2. 何か会話する（例: "こんにちは"）
3. `C:\Users\musta\.claude\shell-snapshots\` にログファイルが作成される
4. 再度AI監査を実行

---

## 📚 詳細ドキュメント

- **完全ガイド**: `README_LAYER2_MCP_AUDIT.md`
- **アーキテクチャ**: `C:\Users\musta\Desktop\PJ\いいんじゃ\フォーム分析\docs\8-LAYER-SYSTEM-ARCHITECTURE.md`
- **トラブルシューティング**: `README_LAYER2_MCP_AUDIT.md` のトラブルシューティングセクション

---

## 🎓 次のステップ

1. **Layer 5と併用**: リアルタイム監視も起動
   ```cmd
   C:\Users\musta\.claude\enforcement\daemon\start_service.bat
   ```

2. **Layer 1設定**: Git pre-commit hookをインストール
   ```cmd
   C:\Users\musta\.claude\enforcement\git_hooks\install_hooks.bat
   ```

3. **自動修正機能**: Layer 7を有効化
   ```cmd
   set AUTO_CORRECTION_ENABLED=1
   ```

---

## 💡 ヒント

### ヒント1: 間隔の調整

開発スタイルに応じて監査間隔を調整:

- **頻繁に確認したい**: `--interval 3`（3分）
- **標準**: `--interval 5`（5分・デフォルト）
- **負荷を減らす**: `--interval 10`（10分）

### ヒント2: バックグラウンド実行

Windowsタスクスケジューラで自動起動:

```cmd
# TODO: タスクスケジューラ設定スクリプトを作成予定
```

### ヒント3: VS Code統合

`.vscode/settings.json` に追加:

```json
{
    "8layer.enforcement.ai_audit": true,
    "8layer.enforcement.audit_interval": 5
}
```

---

**準備完了！** 開発を始めてください。5分ごとにAIが会話を分析して違反を検出します。
