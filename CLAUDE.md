# ⚡ ULTRA PRIORITY RULES - AUTOMATIC ENFORCEMENT (最優先・自動適用)

## 🧠 Rule 1: ULTRA THINK MODE (必須・常時有効)

**このルールは全ての会話で自動的に適用されます。**

### 必須事項（MANDATORY）

**全てのタスクで以下を実行：**

1. **Extended Thinking（拡張思考）を使用**
   - `

## 🎯 サンプルデータと実データの明確な区別（CRITICAL RULE）

**基本原則: サンプルデータと実データを明確に区別し、誤解を招かない**

### ✅ 必ず守るべきルール（絶対厳守）

**1. データの出所を常に明示する（全てのデータ出力時に必須）**
- ✅ **正しい**: データの種別と出所を明確に表示
- ❌ **禁止**: データの出所を曖昧にする、推測データを事実として提示する

**適用範囲**:
- AWS（DynamoDB/S3/Lambda/API Gateway等）
- データベース（MySQL/PostgreSQL/MongoDB等）
- API（REST/GraphQL等）
- ファイル（CSV/JSON/Excel等）
- スクレイピング結果
- **全てのデータ出力**

**2. サンプルデータを使用する場合の必須表示**
```
⚠️ これは**サンプルデータ**です（動作確認用）
実際のデータソースから取得したものではありません。
テスト・デモ・動作確認のために作成された架空のデータです。
```

**3. 実データを使用する場合の必須表示**
```
✅ これは**実データ**です
データソース: [具体的な出所を明記]
  例: DynamoDB テーブル 'users'
      S3 バケット 'production-data'
      MySQL データベース 'analytics'
      API エンドポイント 'https://api.example.com/data'
取得日時: 2025-11-05 12:34:56
```

### 🚨 違反パターンと修正

**❌ 違反例: サンプルデータを事実のように提示**
```
User: "ビッグファイブの推定値を見せて"
↓
Assistant: matching_results.jsonを提示（サンプルデータだが明記せず）
↓
User: 実データだと誤解
```

**✅ 正しい例: 明確に区別**
```
User: "ビッグファイブの推定値を見せて"
↓
Assistant:
「⚠️ 実際の推定値はまだ生成されていません。
マッチングシステムの動作確認用に作成した**サンプルデータ**がありますが、
これは実データではありません。

実データを生成するには、SageMakerエンドポイントをデプロイして
推定処理を実行する必要があります。

どちらを確認しますか？
1. サンプルデータでの動作確認
2. 実データの生成プロセス開始」
```

### 📋 データ種別の明示方法

**ファイル名での区別**:
- `sample_bigfive_predictions.json` - サンプルデータ
- `bigfive_predictions_20251105_123456.json` - 実データ（タイムスタンプ付き）

**ファイル内での明示**:
```json
{
  "data_type": "SAMPLE",  // または "REAL"
  "source": "manually_created_for_testing",  // または "dynamodb", "s3", etc.
  "created_at": "2025-11-05T01:24:56",
  "note": "これはサンプルデータです。実際のAWSリソースから取得したものではありません。",
  "predictions": [...]
}
```

**出力時の明示**:
```
📊 出力結果:
━━━━━━━━━━━━━━━━━━━━━━
⚠️ データ種別: サンプルデータ
出所: テスト用に手動作成
実データではありません
━━━━━━━━━━━━━━━━━━━━━━

{
  "Agreeableness": 70,
  ...
}
```

### 🎯 実装時のチェックリスト

データを提示する前に必ず確認:

- [ ] このデータは実データか、サンプルデータか？
- [ ] データの出所（AWS/DB/手動作成）を明記したか？
- [ ] サンプルデータの場合、⚠️マークで明示したか？
- [ ] 実データの場合、取得元（DynamoDB/S3など）を明記したか？
- [ ] ファイル名でサンプルか実データか区別できるか？
- [ ] ユーザーが誤解する可能性はないか？

### 💡 ユーザーへの確認フロー

**データが存在しない場合**:
```
1. 実データを確認する
   ↓
2. 存在しない場合、ユーザーに報告
   「実データは存在しません。以下の選択肢があります：
    A) 実データを生成する（推定処理を実行）
    B) サンプルデータで動作確認する」
   ↓
3. ユーザーの選択を待つ
   ↓
4. サンプルデータを使う場合、必ず明示する
```

### 🔴 重大性

この違反は以下の理由で重大です:
- ✗ ユーザーの意思決定を誤らせる
- ✗ データの信頼性を損なう
- ✗ 実装済みと誤解させ、後続作業に影響
- ✗ システムの現状認識を誤らせる

**違反時の対応**:
1. 即座に謝罪
2. サンプルデータであることを明確に訂正
3. 実データの有無を確認
4. 正しい状況を説明

### 📊 コンプライアンススコアへの影響

- **明確な区別あり**: +5点
- **曖昧な表現**: -20点
- **サンプルを実データとして提示**: -50点（重大違反）

---

## 📂 ファイル処理の基本ルール（DEFAULT BEHAVIOR）

### Excel/バイナリファイルの処理

**デフォルト動作: Excelファイルは必ずPythonスクリプトで処理する**

#### ✅ 基本原則（絶対厳守）

1. **Excelファイル（.xlsx, .xls）の読み込み**
   - ❌ **禁止**: Read toolで直接読み込もうとする
   - ✅ **必須**: Pythonスクリプト（pandas）を使用する

2. **エラーメッセージへの対応**
   ```
   エラー: "This tool cannot read binary files"
   　↓
   ✅ 即座にPythonスクリプトで処理
   ❌ 「CSVに変換してください」と依頼しない
   ```

3. **実装パターン**
   ```python
   import pandas as pd
   import sys
   sys.stdout.reconfigure(encoding='utf-8')  # 文字化け防止（必須）

   df = pd.read_excel('ファイル名.xlsx', sheet_name='シート名')
   print(df.head())
   ```

#### 📋 対応ファイル形式

| 形式 | 処理方法 | ツール |
|------|---------|--------|
| **Excel (.xlsx, .xls)** | ✅ Pythonスクリプト | pandas |
| **PDF (.pdf)** | ✅ Read tool（直接読込可） | Read |
| **画像 (.png, .jpg)** | ✅ Read tool（直接読込可） | Read |
| **CSV (.csv)** | ✅ Read tool or Python | Read / pandas |
| **テキスト (.txt, .md)** | ✅ Read tool | Read |

#### 🚨 違反パターンと正しい対応

**❌ 違反例: 無駄なやり取り**
```
User: "このExcelファイルを読んでください"
Assistant: Read toolを実行
Error: "This tool cannot read binary files"
Assistant: "CSVに変換していただけますか？"  ← これは禁止
```

**✅ 正しい例: 即座にPython処理**
```
User: "このExcelファイルを読んでください"
Assistant: 即座にPythonスクリプトで読み込み
Success: データ表示・処理実行
```

#### 💡 頻出パターン

**パターン1: Excel → LookML生成**
```python
# データ定義書.xlsxとDB項目.xlsxからLookMLビューを自動生成
import pandas as pd

df_def = pd.read_excel('データ定義書.xlsx', sheet_name='タスク')
df_db = pd.read_excel('DB項目.xlsx', sheet_name='sheet1')

# LookMLファイル生成ロジック
# ...
```

**パターン2: Excelデータ分析**
```python
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('分析対象.xlsx')
print(df.describe())
print(df.groupby('カラム名').sum())
```

#### 🔧 トラブルシューティング

**Q: 文字化けする**
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')  # 必ず追加
```

**Q: モジュールがない**
```bash
py -m pip install pandas openpyxl
```

**Q: 複数シート処理**
```python
df_dict = pd.read_excel('ファイル.xlsx', sheet_name=None)
for sheet_name, df in df_dict.items():
    print(f"Sheet: {sheet_name}")
    print(df.head())
```

#### 📊 コンプライアンススコアへの影響

- **Python即座使用**: +5点
- **Read tool試行後Python**: 0点（標準）
- **ユーザーに変換依頼**: -10点（違反）

#### 💾 永続化ルール

このルールは `.claude/CLAUDE.md` に永続化されます。
Excelファイルに遭遇した際は、必ずこのルールを参照してください。

---

## ⚡ CRITICAL: 全タスクで必須の3ステップ（違反時は自動ブロック）

### 📋 タスク開始時（STEP 1: BEFORE）
```bash
# 1. Byterover知識検索（必須）
byterover-retrieve-knowledge

# 2. TodoWrite一括作成（8-10個必須）
TodoWrite { todos: [...8-10 items...] }

# 3. 並列実行計画（複数Task()必須）
[Single Message]:
  Task("agent1", "description", "type")
  Task("agent2", "description", "type")
  # ... minimum 2+ agents for complex tasks
```

### 🎯 タスク実行中（STEP 2: DURING）
- **複雑度スコア自動計算**（ファイル数×5 + エージェント数×10 + ...）
- **Score >= 50 → Seraphina自動相談**
- **2ファイル以上 → 並列Codex必須**
- **ビジネスロジック → Gemini追加必須**

### ✅ タスク完了時（STEP 3: AFTER）
```bash
# 学習内容をByteroverに保存（必須）
byterover-store-knowledge
```

---

## 🛡️ 8層強制システム（100%ブロック体制）

### Layer 1: Pre-commit Git Hook
- **ブロック条件**:
  - Byterover retrieve/store未実行
  - TodoWrite < 8項目
  - 並列実行証拠なし
  - Session compliance < 70%
- **回避不可**: `--no-verify`も無効化
- **場所**: `.git/hooks/pre-commit`

### Layer 2: MCP監査エージェント（AI分析）
- **機能**: 全Claude行動をCodexで分析
- **スコアリング**: 0-100%（50%未満でコミットブロック）
- **検出項目**: 9種類のMCP規則違反
- **場所**: `.claude/scripts/mcp-audit-agent.py`

### Layer 3: 並列実行強制Wrapper
- **機能**: Task()呼び出しを自動並列化
- **自動修正**: 逐次パターン → 並列パターン変換
- **エージェント追加**: 不足エージェントを自動提案
- **場所**: `.claude/scripts/force-parallel-wrapper.py`

### Layer 4: Seraphina自動相談システム
- **トリガー**: complexity_score >= 50で自動発動
- **回避不可**: 複雑タスクは必ずSeraphina相談
- **統合**: session-monitorと連携
- **場所**: `.claude/scripts/seraphina-auto-consult.py`

### Layer 5: Session監視（リアルタイム）
- **監視**: 全会話をリアルタイム分析
- **違反スコア**: 累積60点以上で警告
- **通知**: デスクトップ通知 + VS Code統合
- **場所**: `.claude/scripts/session-monitor.py`

### Layer 6: Post-task検証Hook
- **検証**: タスク完了時の必須チェック
- **ブロック**: Byterover保存漏れで失敗
- **場所**: `.claude/hooks/post-task-verify.sh`

### Layer 7: 自動修正提案システム
- **機能**: 違反検出時に正しいパターン提示
- **比較**: ❌ WRONG vs ✅ CORRECT表示
- **場所**: `.claude/scripts/auto-correct-violation.py`

### Layer 8: リアルタイム通知システム
- **通知**: Windows toast notification
- **重大度**: INFO/WARNING/ERROR
- **VS Code**: ステータスバー統合
- **場所**: `.claude/scripts/realtime-notifier.py`

---

## 📊 MCP完全活用マトリックス（100%適用）

| 状況 | Byterover | Codex | Gemini | Seraphina | Claude Flow | TodoWrite | CodeRabbit |
|------|-----------|-------|--------|-----------|-------------|-----------|------------|
| **タスク開始** | ✅ retrieve | - | - | - | - | ✅ 8-10個 | - |
| **単一ファイル** | - | ✅必須 (1) | - | - | - | - | ✅ |
| **2+ファイル** | - | ✅ (N) | - | - | ✅ | - | ✅ |
| **ビジネス要件** | ✅ retrieve | ✅ | ✅ | - | ✅ | - | - |
| **複雑判断** | ✅ retrieve | ✅ (N) | ✅ | ✅ | ✅ | - | - |
| **Score≥50** | ✅ retrieve | ✅ (N) | ✅ | ✅必須 | ✅ | - | - |
| **ファイル保存** | - | - | - | - | - | - | ✅ |
| **コミット前** | - | - | - | - | - | - | ✅ |
| **タスク完了** | ✅ store | - | - | - | - | ✅更新 | - |

---

## 🤝 Codex常時協力ルール（DEFAULT BEHAVIOR）

**全ての修正タスクでCodexと協力することをデフォルト動作とする**

**📖 詳細ルール**: [MANDATORY_CODEX_CHECK.md](.claude/MANDATORY_CODEX_CHECK.md) を参照

### ✅ 基本原則（絶対厳守）

**単一ファイルの修正であっても、必ずCodex analyst エージェントと協力する**

- ❌ **禁止**: 単独で分析・修正を完結させる
- ✅ **必須**: 常にCodex analystを起動して分析させる
- ✅ **必須**: Codexの分析結果を踏まえて修正する

**🚨 特に重要: データ分析・マッピング作成・辞書作成は必ずCodex協力**
- Excel/CSVファイルの分析
- 英語→日本語のマッピング
- キーワード辞書の作成
- 推測を含む処理

**違反時のペナルティ: -20点〜-25点（重大違反）**

### 🎯 実行パターン（全タスク共通）

#### Pattern 1: 単一ファイル修正
```
[Single Message]:
  Read "file.lkml"
  Task("Codex Analyst", "ファイル構造を分析して最適な修正箇所を特定", "analyst")
  # Codex結果を待つ
  # ↓
  Write/Edit "file.lkml"  # Codexの分析を踏まえて修正
  TodoWrite { todos: [...] }
```

#### Pattern 2: 複数ファイル修正
```
[Single Message]:
  Read "file1.lkml"
  Read "file2.lkml"
  Task("Codex Analyst 1", "file1の構造分析", "analyst")
  Task("Codex Analyst 2", "file2の構造分析", "analyst")
  # 並列分析結果を待つ
  # ↓
  Write/Edit files  # 両Codexの分析を統合して修正
  TodoWrite { todos: [...] }
```

### 📋 協力必須の状況（100%適用）

| 状況 | Codex協力 | 理由 |
|------|-----------|------|
| **LookML修正** | ✅必須 | SQL構造の正確な理解が必要 |
| **ディメンション追加** | ✅必須 | 既存ロジックとの整合性確認 |
| **メジャー追加** | ✅必須 | 集計ロジックの検証 |
| **フィルター追加** | ✅必須 | WHERE句の影響範囲確認 |
| **結合キー変更** | ✅必須 | データ整合性の検証 |
| **パラメータ追加** | ✅必須 | 既存パラメータとの競合確認 |
| **派生テーブル修正** | ✅必須 | SQL構文の複雑性対応 |
| **バグ修正** | ✅必須 | 根本原因の特定 |

### 🚨 違反パターンと修正

#### ❌ 違反例: 単独修正
```
# ユーザー要求: "ディメンション追加して"
↓
Read file
↓
Edit file  # Codex協力なし → 違反
```

#### ✅ 正しい例: Codex協力
```
# ユーザー要求: "ディメンション追加して"
↓
[Single Message]:
  Read file
  Task("Codex", "既存ディメンション構造を分析", "analyst")
↓
# Codex結果を確認
↓
Edit file  # Codexの分析を踏まえて追加
```

### 💡 Codexへの指示例

**明確で具体的な指示を出す:**

```
✅ Good:
"financial_metrics_pivot.view.lkmlを分析して、
 既存の時間系ディメンションの位置と構造を特定し、
 会計年度四半期ディメンションを追加する最適な位置を提案してください"

❌ Bad:
"ファイルを見て"
```

### 🎯 期待される効果

1. **精度向上**: Codexの分析により見落としを防止
2. **整合性確保**: 既存ロジックとの矛盾を事前検出
3. **学習促進**: Codexの分析から新しいパターンを学習
4. **品質保証**: 複数の視点からの検証

### 📊 コンプライアンススコアへの影響

- **Codex協力あり**: +10点
- **Codex協力なし（単一ファイル）**: -15点
- **Codex協力なし（複数ファイル）**: -25点

### 🔧 強制適用方法

このルールは以下で強制されます:
- Layer 2: MCP監査エージェント（Codex協力の検出）
- Layer 5: Session監視（リアルタイム違反検出）
- Layer 6: Post-task検証（完了時チェック）

---

## 🎯 自動TodoWrite生成システム

### 使用方法
```bash
python .claude/scripts/auto-todowrite-generator.py --message "ユーザー要求"
```

### 自動生成内容
- **8-10項目**: フェーズ別タスク分解
- **MCP統合**: Byterover/Codex/Gemini/Seraphina自動検出
- **優先度**: Critical/High/Medium/Low自動割り当て
- **時間見積**: 各タスクの所要時間予測
- **並列グループ**: 同時実行可能タスクをグループ化

### 自動検出ロジック
```python
IF 複雑度スコア >= 50:
    todos += ["Seraphina相談実行"]
IF ファイル数 >= 2:
    todos += ["Claude Flow並列実行"]
IF ビジネスロジック検出:
    todos += ["Gemini妥当性検証"]
```

---

## 🔧 強制システムの起動方法

### 一括セットアップ（初回のみ）
```bash
# Git hooks インストール
python .claude/scripts/install-parallel-hooks.py

# MCP監査システム インストール
.claude/scripts/setup-audit.bat install

# リアルタイム通知システム インストール
.claude/install-notifier.bat
```

### 日常的な使用
```bash
# Session監視 起動（常時推奨）
python .claude/scripts/session-monitor.py start

# リアルタイム通知 起動
.claude/start-realtime-notifier.bat

# CodeRabbit監視 起動
.claude/start-realtime-monitor.bat
```

### VS Code統合（キーボードショートカット）
- **Ctrl+Shift+C**: Mandatory Checklist表示
- **Ctrl+Shift+V**: Post-Task検証実行
- **Ctrl+Shift+A**: 自動修正提案
- **Ctrl+Shift+M**: Session監視起動
- **Ctrl+Shift+P**: コンプライアンスレポート表示

---

## 🎓 違反パターンと自動修正

### ❌ 違反例1: 逐次実行
```
Message 1: Read file
Message 2: Analyze
Message 3: Fix
```

### ✅ 自動修正後:
```
[Single Message]:
  Read "file.lkml"
  Task("Analyst", "Analyze structure", "analyst")
  Write "file.lkml"
  TodoWrite { todos: [...8 items...] }
```

### ❌ 違反例2: Byterover未使用
```
# タスク開始
Task("Analyst", "分析開始")
```

### ✅ 自動修正後:
```
[Single Message]:
  byterover-retrieve-knowledge
  Task("Analyst", "過去知識を踏まえて分析", "analyst")
```

### ❌ 違反例3: TodoWrite不足
```
TodoWrite { todos: [
  {content: "分析", status: "pending"},
  {content: "実装", status: "pending"}
]}  # 2個のみ → 違反
```

### ✅ 自動修正後:
```bash
python .claude/scripts/auto-todowrite-generator.py --message "タスク内容"
# → 8-10個の詳細Todoを自動生成
```

---

## 📈 コンプライアンススコア基準

### スコアリング計算式
```python
violations_score = sum([
    root_file_creation × -25,
    sequential_execution × -20,
    missing_seraphina × -20,
    missing_byterover_retrieve × -15,
    missing_byterover_store × -15,
    insufficient_todowrite × -10,
    no_gemini × -10
])

compliance_score = 100 + violations_score
```

### 評価基準
- **95-100%**: PERFECT（模範的）
- **75-94%**: GOOD（良好）
- **50-74%**: WARNING（要改善）
- **0-49%**: FAIL（コミットブロック）

### 目標値
- **開発中**: 75%以上
- **レビュー時**: 85%以上
- **本番投入**: 95%以上

---

## 🚀 完全自動化フロー

### 理想的な作業フロー（全自動）
```
1. ユーザー要求受信
   ↓
2. auto-todowrite-generator.py が8-10個のTodo自動生成
   ↓
3. byterover-retrieve-knowledge 自動実行
   ↓
4. force-parallel-wrapper.py が並列実行プラン生成
   ↓
5. seraphina-auto-consult.py が複雑度判定
   ├─ Score < 50: 通常実行
   └─ Score >= 50: Seraphina相談 → 実行
   ↓
6. Task()で並列エージェント起動（2+個）
   ↓
7. session-monitor.py がリアルタイム監視
   ↓
8. 作業完了
   ↓
9. post-task-verify.sh が検証
   ↓
10. byterover-store-knowledge 自動実行
   ↓
11. git commit
    ↓
12. pre-commit hook が全チェック実行
    ├─ Compliance >= 70%: ✅ コミット成功
    └─ Compliance < 70%: ❌ コミットブロック
    ↓
13. mcp-audit-agent.py がAI分析・ログ記録
```

---

## 🛠️ トラブルシューティング

### Q: コミットがブロックされる
**A**: コンプライアンススコアを確認
```bash
python .claude/scripts/session-monitor.py report
# → 違反項目を確認して修正
```

### Q: Seraphina相談が必要と言われる
**A**: 複雑度スコアが50以上のため必須
```bash
python .claude/scripts/seraphina-auto-consult.py --task "タスク内容"
```

### Q: TodoWriteが不足していると言われる
**A**: 自動生成ツールを使用
```bash
python .claude/scripts/auto-todowrite-generator.py --message "要求内容"
```

### Q: 並列実行が検出されない
**A**: Task()を1メッセージで複数実行
```
[Single Message]:
  Task("agent1", "task1", "analyst")
  Task("agent2", "task2", "coder")
```

---

## 📚 関連ドキュメント

- **完全ガイド**: `.claude/docs/MCP_AUDIT_GUIDE.md`
- **並列実行**: `.claude/docs/FORCE_PARALLEL_WRAPPER.md`
- **Git Hooks**: `.claude/README_GIT_HOOKS.md`
- **通知システム**: `.claude/notifications/README.md`
- **クイックスタート**: `.claude/QUICK_REFERENCE_PARALLEL.md`

---

# 以下、従来のCLAUDE.md内容（参考用）

## CodeRabbitリアルタイム統合 (常時監視・自動フィードバック)

### ✨ リアルタイム自動フィードバックシステム
CodeRabbitが**ファイル保存時に常に自動レビュー**を実行し、Claude Codeにリアルタイムでフィードバックします。

#### 自動実行される処理：

##### 1️⃣ **リアルタイム監視** (ファイル保存時)
```bash
# 監視サービスを開始
python .claude\coderabbit-background-service.py start

# またはバッチファイルで簡単起動
.claude\start-realtime-monitor.bat
```
- **ファイル保存時に即座にレビュー**
- リアルタイムで問題を検出・通知
- `.lkml`, `.py`, `.js`, `.ts`, `.sql`ファイルを監視

##### 2️⃣ **コミット前チェック** (pre-commit hook)
- 自動的にCodeRabbitレビューを実行
- 高リスク変更を検出して警告
- 問題がある場合はコミットを中止

##### 3️⃣ **コミット後フィードバック** (post-commit hook)
- レビュー結果を自動生成
- `.claude/coderabbit_feedback.json`に保存
- 重大な問題を自動検出して通知

## 📌 開発時の重要ルール（厳守・デフォルト）

### 🚫 忖度修正の絶対禁止（最優先原則）

**基本原則: 指示された内容のみ実行。追加修正は一切行わない。**

#### 必ず守るべきルール（デフォルト動作）：

**1. 変更前の必須確認プロセス**
```
標準フロー:
1. 変更内容を明確に説明
2. ユーザーの明示的な許可を待つ
3. 許可された内容のみ実行
4. 追加修正は提案のみ（実行しない）
```

**2. 指示された内容のみ実行**
- ✅ **正しい動作**: ユーザーが指示した内容を正確に実行
- ❌ **禁止動作**: 「ついでに〜も直す」「こっちの方が良い」と勝手に判断して修正

**3. 関連する問題を見つけた場合**
- ✅ **正しい動作**: 「〜も修正が必要かもしれません。修正しますか？」と提案
- ❌ **禁止動作**: 黙って追加修正を実行

---

### 🔒 要件の勝手な変更・判断の絶対禁止（ZERO TOLERANCE POLICY）

**🚨 このルールの違反は一切許容されません。違反した場合は即座にタスクを停止してください。**

#### ❌ 絶対禁止事項

**1. 要件の勝手な変更**
- ❌ ユーザーが指定した要件を、勝手に別のものに変更する
- ❌ データがない・エラーが出るなどの理由で、勝手に別のフィールドやロジックに変更する
- ❌ 「こっちの方が良い」「これで代替できる」と判断して勝手に実装する
- ❌ 要件を自分で解釈して、勝手に簡略化・最適化する

**例（絶対禁止）:**
```
要件: detail01（売上高_受注時）を使用
　↓
データがない
　↓
❌ 勝手にdetail34（売上高_実績）に変更  ← これは絶対禁止
```

**2. 結合キーの勝手な判断**
- ❌ テーブル結合時に、結合キーを勝手に推測・決定する
- ❌ 「おそらくこのフィールドだろう」と判断して実装する
- ❌ 他のビューファイルを参考にして、勝手に同じキーを使用する

**例（絶対禁止）:**
```
テーブルAとテーブルBを結合する
　↓
❌ 勝手に「A.id = B.id」と判断  ← これは絶対禁止
✅ 「どのフィールドで結合しますか？」と確認  ← 正しい対応
```

**3. フィルター条件の勝手な変更**
- ❌ 要件で指定されたフィルター条件を、勝手に緩和・厳格化する
- ❌ データが少ないからといって、勝手に条件を変更する

**例（絶対禁止）:**
```
要件: 物件状況が「受」(situation_div = 6) のみ
　↓
データが少ない
　↓
❌ 勝手に全ての状況を含める  ← これは絶対禁止
```

**4. 推測による実装**
- ❌ 曖昧な要件があっても、推測で実装する
- ❌ 「おそらく〇〇だろう」と判断して進める
- ❌ ユーザーの意図を勝手に解釈する

#### ✅ 正しい対応フロー

**フロー1: 要件通りに実装したがデータがない場合**
```
1. 要件通りに実装する
2. 実装が完了したことを報告
3. 問題点を明確に説明：
   「要件通りdetail01で実装しましたが、
    detail01にデータが存在しないため表示されません。」
4. 選択肢を提示（実行はしない）：
   「選択肢：
    1. detail01にデータを投入する（要件通り）
    2. 要件を変更して別のフィールドを使う（detail34など）

    どちらにしますか？」
5. ユーザーの明示的な指示を待つ
```

**フロー2: テーブル結合が必要な場合**
```
1. 結合が必要なテーブルを特定
2. ユーザーに確認（必須）：
   「テーブルAとテーブルBを結合します。

    確認事項：
    1. 結合キーは何ですか？
       - テーブルA の [フィールド名] = テーブルB の [フィールド名]
    2. 結合タイプは何ですか？
       - INNER JOIN / LEFT JOIN / RIGHT JOIN
    3. 追加のフィルター条件はありますか？」
3. 回答を得てから実装
4. 勝手に判断・推測しない
```

**フロー3: 要件が曖昧な場合**
```
1. 実装を開始しない
2. 不明点を明確に質問：
   「以下の点が不明です。教えてください：
    - [不明点1]
    - [不明点2]
    - [不明点3]」
3. 回答を得てから実装
4. 推測で進めない
```

#### 🎯 具体例：正しい対応 vs 間違った対応

**ケース1: データが存在しない**
```
❌ 間違った対応:
要件: detail01を使用
→ データがない
→ 勝手にdetail34に変更して実装

✅ 正しい対応:
要件: detail01を使用
→ detail01で実装
→ 「detail01にデータがありません。
   1. データ投入（要件通り）
   2. 要件変更（detail34使用）
   どちらにしますか？」
→ ユーザーの指示を待つ
```

**ケース2: 結合キーが不明**
```
❌ 間違った対応:
→ 他のビューを見て推測
→ 勝手に「A.id = B.id」で実装

✅ 正しい対応:
→ 「テーブルAとBを結合する際の
   結合キーを教えてください」
→ ユーザーの回答を待つ
→ 指定されたキーで実装
```

**ケース3: フィルター条件の結果が少ない**
```
❌ 間違った対応:
要件: situation_div = 6のみ
→ データが少ない
→ 勝手に全ての状況を含める

✅ 正しい対応:
要件: situation_div = 6のみ
→ 要件通り実装
→ 「situation_div = 6でフィルターしましたが、
   該当データが少ないです。
   1. このまま（要件通り）
   2. 条件を変更
   どちらにしますか？」
→ ユーザーの指示を待つ
```

#### 📋 チェックリスト（実装前に必ず確認）

実装を開始する前に、以下を自問してください：

- [ ] 要件は明確に理解できているか？
- [ ] 曖昧な点や不明点はないか？
- [ ] テーブル結合が必要な場合、結合キーは確認済みか？
- [ ] フィールド名は要件で明示されているか？
- [ ] フィルター条件は要件で明示されているか？
- [ ] 推測で判断しようとしていないか？

**1つでも「いいえ」があれば、実装を開始せずユーザーに確認してください。**

#### 🔴 違反時の対応

もし要件を勝手に変更・判断してしまった場合：

1. **即座に停止**: 実装を中断する
2. **謝罪**: 勝手な判断をしたことを謝罪
3. **正しい対応を提示**: 本来すべきだった確認内容を説明
4. **修正**: 要件通りに再実装
5. **再発防止**: このルールを再確認

#### 💾 このルールの永続化

このルールは `.claude/CLAUDE.md` に永続化され、全てのセッションで参照されます。
違反は一切許容されません。必ず守ってください。


---

## 🔍 フィールド参照検証手順（LookML開発の必須ルール）

**最終更新: 2025-10-16 | 目的: フィールド参照ミスの完全撲滅**

### 📌 背景

2025-10-16に発生した営業担当者/工務担当者フィールドの誤用により、同じミスを3つのファイルで繰り返す重大インシデントが発生しました。このセクションは再発防止のためのデフォルトルールです。

### ✅ 実装前の必須チェック（MANDATORY）

**LookMLファイルを編集する際、以下を必ず実行:**

#### Step 1: フィールド名マッピング確認

```bash
# 営業担当者/工務担当者フィールドを使用する場合、必ず docs/field_reference_checklist.md を参照
```

**必須参照ドキュメント:**
- `docs/field_reference_checklist.md` - フィールド参照チェックリスト

#### Step 2: 正しいフィールド名の使用

| 役割 | ❌ 間違い | ✅ 正しい |
|------|----------|----------|
| **営業担当者（名前）** | `employee_namebq` | `bqbusiness_discussions___sales_staff_namebq` |
| **工務担当者（名前）** | `sales_staff_namebq` | `bqbusiness_discussions___employee_name___construction_employeebq` |

#### Step 3: サブクエリ作成時の検証

```sql
-- ✅ 正しいパターン: 全フィールドをSELECT句に定義
WITH base_query AS (
  SELECT
    bd.bqsales_staffbq,
    bd.bqbusiness_discussions___sales_staff_namebq,  -- 営業担当者名（必須）
    bd.bq__custom_object_index_4_idbq,
    bd.bqbusiness_discussions___employee_name___construction_employeebq  -- 工務担当者名（必須）
  FROM `gj-chikyu.prod_mongodb_clean.o10936_business_discussions` bd
)
```

### 🚨 絶対禁止パターン

#### ❌ 禁止1: employee_namebq の営業担当者への使用

```sql
-- ❌ これは間違い（絶対禁止）
SELECT
  employee.bqemployee_namebq AS sales_staff_name

-- ✅ これが正しい
SELECT
  bd.bqbusiness_discussions___sales_staff_namebq AS sales_staff_name
```

#### ❌ 禁止2: サブクエリでのフィールド定義漏れ

```sql
-- ❌ 間違い: SELECT句にフィールドが定義されていない
WITH base AS (
  SELECT
    bd.bqsales_staffbq
    -- sales_staff_name が定義されていない！
  FROM table
)
SELECT sales_staff_name FROM base  -- エラー発生

-- ✅ 正しい: SELECT句に全フィールドを定義
WITH base AS (
  SELECT
    bd.bqsales_staffbq,
    bd.bqbusiness_discussions___sales_staff_namebq AS sales_staff_name  -- 定義されている
  FROM table
)
SELECT sales_staff_name FROM base  -- OK
```

#### ❌ 禁止3: UNION ALL で一部ブロックのみ定義

```sql
-- ❌ 間違い
SELECT field1, field2 FROM table1
UNION ALL
SELECT field1 FROM table2  -- field2が足りない

-- ✅ 正しい
SELECT field1, field2 FROM table1
UNION ALL
SELECT field1, field2 FROM table2  -- 全ブロックで同じフィールド
```

### 🔧 自動検証ツール

#### 使用方法

```bash
# LookMLファイル保存前に実行（推奨）
python scripts/validate-lookml-fields.py views/your_file.view.lkml
```

#### Git Pre-commit Hook（自動化・毎回実行）

**✅ 推奨: 自動インストール**

```bash
# Windows
scripts\install-git-hooks.bat

# Linux/Mac
bash scripts/install-git-hooks.sh
```

**これにより、以下が自動化されます:**
- ✅ `git commit` 時に全LookMLファイルを自動検証
- ✅ フィールド参照ミスを検出してコミットをブロック
- ✅ 手動検証忘れを防止

**手動インストール（上級者向け）:**

```bash
# Hookファイルを実行可能にする
chmod +x .git/hooks/pre-commit

# 動作確認
git add views/test.view.lkml
git commit -m "Test commit"
# → 自動的にフィールド検証が実行される
```

**Hookのバイパス（非推奨）:**

```bash
# 緊急時のみ使用
git commit --no-verify
```

### 📚 必須参照ファイル

#### 1. フィールドリファレンス

- **`docs/field_reference_checklist.md`** - 営業担当者/工務担当者フィールドの完全ガイド
- **`views/HW_Pipeline_Value_Current.view.lkml`** - 模範実装例（Line 80-82）
- **`views/o10936_business_discussions.view.lkml`** - フィールド定義の標準（Line 120, 125）

#### 2. 検証SQLサンプル

```sql
-- 営業担当者フィールドの存在確認
SELECT
  bqsales_staffbq,
  bqbusiness_discussions___sales_staff_namebq,
  COUNT(*) as record_count
FROM `gj-chikyu.prod_mongodb_clean.o10936_business_discussions`
WHERE bqsales_staffbq IS NOT NULL
GROUP BY 1, 2
LIMIT 10
```

### 🎯 実装フローチャート

```
LookML編集タスク受領
  ↓
[ ] docs/field_reference_checklist.md を確認
  ↓
[ ] 営業担当者/工務担当者フィールドを使用する？
  ├─ Yes → 正しいフィールド名マッピング表を確認
  └─ No → 通常の実装へ
  ↓
[ ] サブクエリを使用する？
  ├─ Yes → SELECT句に全フィールドを定義
  └─ No → 通常の実装へ
  ↓
[ ] UNION ALL を使用する？
  ├─ Yes → 全ブロックで同じフィールド定義
  └─ No → 通常の実装へ
  ↓
[ ] 検証SQL実行（BigQuery UI）
  ↓
[ ] 構文エラーなし？
  ├─ Yes → ファイル保存
  └─ No → 修正して再検証
  ↓
[ ] python scripts/validate-lookml-fields.py 実行
  ↓
[ ] 検証OK？
  ├─ Yes → Git Commit
  └─ No → 修正して再検証
```

### 📊 コンプライアンススコアへの影響

| 違反内容 | スコア減点 |
|---------|----------|
| employee_namebq 誤用 | -20点 |
| サブクエリフィールド定義漏れ | -15点 |
| UNION ALL 不整合 | -15点 |
| 検証ツール未実行 | -10点 |

**目標**: フィールド参照違反ゼロ

### 🛡️ 強制適用

このルールは以下で強制されます:
- **Layer 1**: Git pre-commit hook（フィールド参照検証）
- **Layer 2**: MCP監査エージェント（パターン検出）
- **Layer 6**: Post-task検証（完了時チェック）

### 💡 車輪の再発明を防ぐ

**既存の正しい実装を必ず参照してください:**

```bash
# 営業担当者フィールドの正しい使用例を検索
grep -r "bqbusiness_discussions___sales_staff_namebq" views/ | head -5

# 工務担当者フィールドの正しい使用例を検索
grep -r "bqbusiness_discussions___employee_name___construction_employeebq" views/ | head -5
```

---

**重要**: このルールは過去の実際のミスから学んだ教訓です。必ず守ってください。
