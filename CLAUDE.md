# ⚡ ULTRA PRIORITY RULES - AUTOMATIC ENFORCEMENT (最優先・自動適用)

## 🖥️ Rule 0: 長時間処理は別ターミナルで実行（MANDATORY TERMINAL EXECUTION）

**基本原則: スクレイピング・分析・バッチ処理など長時間かかる処理は、必ず別ターミナルで直接実行する**

### ✅ 必ず守るべきルール（絶対厳守）

**1. 別ターミナルで実行すべき処理**
- スクレイピング（Webからのデータ取得）
- 大量データの分析・処理
- 機械学習モデルの学習
- 画像処理（大量ファイル）
- バッチ処理（100件以上）
- 10分以上かかる見込みの処理

**2. 実行方法**
```bash
# ❌ 禁止: バックグラウンド実行（セッション切断で停止する）
py script.py &
run_in_background: true

# ✅ 正しい: 別ターミナルで直接実行
start cmd /k "py script.py"
```

**3. 理由**
- Claude Codeのバックグラウンドタスクはセッション切断で停止する
- 別ターミナルで実行すれば、Claude Codeを閉じても処理が継続する
- 進捗が直接確認できる

### 📋 チェックリスト

処理を開始する前に確認:
- [ ] 処理時間は10分以上かかりそうか？
- [ ] スクレイピングやバッチ処理か？
- [ ] 進捗ファイルは設定されているか？

**1つでも「はい」があれば、`start cmd /k` で別ターミナル実行**

---

## 🧠 Rule 1: ULTRA THINK MODE (必須・常時有効)

**このルールは全ての会話で自動的に適用されます。**

### 必須事項（MANDATORY）

**全てのタスクで以下を実行：**

1. **Extended Thinking（拡張思考）を使用**
   - `

## 📚 Git履歴参照ルール（MANDATORY GIT HISTORY CHECK）

**基本原則: ファイル修正時は必ずgit履歴を参照し、過去の修正意図・経緯を理解してから作業する**

### ✅ 必ず守るべきルール（絶対厳守）

**1. ファイル修正前のgit履歴確認（必須）**
- ✅ **正しい**: `git log --oneline -10 <ファイル名>` で最近の修正履歴を確認
- ✅ **正しい**: `git show <commit-hash>` で具体的な変更内容を確認
- ❌ **禁止**: 履歴を確認せずに修正を開始

**適用範囲**:
- LookMLファイル（`.view.lkml`, `.model.lkml`）
- Pythonスクリプト（`.py`）
- 設定ファイル（`.json`, `.yaml`, `.md`）
- **全てのバージョン管理されたファイル**

**2. 履歴から学ぶべき情報**
```bash
# 最近10件のコミット履歴を確認
git log --oneline -10 views/order_backlog_breakdown_total.view.lkml

# 特定のコミットの詳細を確認
git show <commit-hash>

# ファイルの変更履歴を行単位で確認
git blame views/order_backlog_breakdown_total.view.lkml
```

**確認事項:**
- なぜこの修正が行われたのか？（修正意図）
- 過去に同じようなエラーが発生していないか？
- 同じ修正を他のファイルにも適用すべきか？
- 修正の副作用は何か？

**3. 履歴参照の必須タイミング**
```
ファイル修正タスク受領
  ↓
[ ] git log --oneline -10 <ファイル名> 実行
  ↓
[ ] 最近の修正内容を確認（コミットメッセージ）
  ↓
[ ] 関連する修正があればgit showで詳細確認
  ↓
[ ] 過去の修正意図を理解
  ↓
[ ] 修正開始
```

### 🔧 実装パターン

**パターン1: ファイル修正前の履歴確認**
```bash
# 1. 修正履歴を確認
git log --oneline -10 views/order_backlog_breakdown_total.view.lkml

# 2. 最近のコミットを確認
git show HEAD

# 3. 特定の行の修正履歴を確認
git blame views/order_backlog_breakdown_total.view.lkml | grep "fy.current_fiscal_period"
```

**パターン2: 同様の修正が他にないか検索**
```bash
# 同じパターンが他のファイルにもないか確認
grep -r "fy.current_fiscal_period" views/

# 過去に同じエラーが修正されていないか確認
git log --all --grep="current_fiscal_period"
```

**パターン3: 修正の影響範囲を確認**
```bash
# このファイルを参照している他のファイルを検索
git log --all --source --full-history -- views/order_backlog_breakdown_total.view.lkml

# 同じCTE構造を持つファイルを検索
grep -r "next_fiscal_backlog" views/
```

### 📋 チェックリスト（修正前に確認）

ファイル修正を開始する前に、以下を確認:

- [ ] `git log --oneline -10 <ファイル名>` を実行したか？
- [ ] 最近のコミットメッセージを読んだか？
- [ ] 過去に同じようなエラー修正がないか確認したか？
- [ ] 同じ修正を他のファイルにも適用すべきか検討したか？
- [ ] 過去の修正意図を理解したか？

**1つでも「いいえ」があれば、git履歴を確認してから修正してください。**

### 🎯 具体例：正しい対応 vs 間違った対応

#### ケース1: GROUP BY制約エラーの修正

```
❌ 間違った対応:
BigQueryエラー発生
→ すぐに修正（MAX()で囲む）
→ 他のファイルに同じ問題があることに気づかない

✅ 正しい対応:
BigQueryエラー発生
→ git log --oneline -10 views/order_backlog_breakdown_total.view.lkml
→ 過去に同様のエラーがないか確認
→ git grep "fy.current_fiscal_period" views/
→ 2つのファイルで同じパターン発見
→ 両方を同時に修正
```

#### ケース2: フィールド名の変更

```
❌ 間違った対応:
フィールド名変更要求
→ 即座に変更
→ 過去に同じフィールドが別の理由で変更されていたことに気づかない

✅ 正しい対応:
フィールド名変更要求
→ git log --oneline -20 views/daily_sales_report.view.lkml
→ git show <commit-hash> で過去の変更理由を確認
→ 「入力率99.8%のフィールドに変更した」という経緯を発見
→ 同じ理由で今回も変更すべきか判断
→ 変更実施
```

### 📊 コンプライアンススコアへの影響

- **修正前にgit履歴確認**: +10点
- **git blame/showで詳細確認**: +5点
- **履歴確認せずに修正**: -20点（重大違反）
- **過去の同様エラーを見落とし**: -15点

### 💾 永続化ルール

このルールは `.claude/CLAUDE.md` に永続化されます。
ファイル修正時は、必ずこのルールを参照してください。

### 🚨 重大性

git履歴を確認しないことによる問題:
- ✗ 過去の修正意図を無視した変更
- ✗ 同じエラーを複数ファイルで繰り返す
- ✗ 過去に修正済みの問題を再発させる
- ✗ 他の開発者の意図を理解せずに上書き

**違反時の対応**:
1. 即座に作業を停止
2. git履歴を確認
3. 過去の修正意図を理解
4. 必要なら修正をやり直す

---

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

## 🎨 UI設計スキル自動適用ルール（DEFAULT BEHAVIOR）

**基本原則: UI/Webコンポーネント作成時は必ずスキルファイルを参照する**

### ✅ 必ず守るべきルール（絶対厳守）

**1. スキルファイルの自動参照**
- **対象ファイル**: `.html`, `.css`, `.tsx`, `.jsx`, `.vue`, `.svelte`
- **スキル場所**: `.claude/skills/ui-design.md`
- ✅ **正しい**: スキルのデザインパターンに従ってUI生成
- ❌ **禁止**: デフォルトの「AIっぽい」デザインで生成

**2. 適用タイミング**
- UI/Webコンポーネントの新規作成時
- 既存UIの大幅改修時
- ランディングページ・ダッシュボード作成時
- Reactコンポーネント作成時

### 🎯 デザインパターン（必須適用）

| 項目 | ❌ 避けるべき | ✅ 推奨 |
|------|-------------|--------|
| **フォント** | Inter, Roboto, Open Sans | JetBrains Mono, Space Grotesk, Playfair Display |
| **カラー** | 紫グラデーション | カスタムCSS変数パレット |
| **背景** | フラットな白/グレー | グラデーション、パターン、幾何学的エフェクト |
| **タイポ** | 均一なウェイト | 極端なコントラスト（100/200 vs 800/900） |

### 🔧 実装パターン

**パターン1: 新規UI作成時**
```
[フロー]:
1. スキルファイル(.claude/skills/ui-design.md)を参照
2. Typography/Color/Motion/Backgrounds の4要素を適用
3. Anti-patterns を避ける
4. CSS変数を使用して一貫性を確保
```

**パターン2: CSS変数の必須使用**
```css
:root {
  --color-primary: #2D3748;
  --color-accent: #F56565;
  --color-bg: #F7FAFC;
  --color-text: #1A202C;
  --color-muted: #718096;
}
```

### 📋 チェックリスト（UI作成前に確認）

- [ ] スキルファイル(.claude/skills/ui-design.md)を参照したか？
- [ ] Inter/Roboto以外のフォントを使用しているか？
- [ ] 紫グラデーションを避けているか？
- [ ] CSS変数でカラーパレットを定義しているか？
- [ ] フラットな白背景ではなく視覚的な深度があるか？

### 📊 コンプライアンススコアへの影響

- **スキル適用あり**: +5点
- **デフォルトAIデザイン使用**: -10点（違反）
- **スキル参照なし**: -15点

### 💾 スキルファイル場所

```
C:\Users\musta\.claude\skills\ui-design.md
```

このルールは全てのUI生成タスクで自動適用されます。

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

## 🔧 コード汎用性ルール（MANDATORY GENERICITY）

**基本原則: 作成するコードは常に汎用的に設計し、ハードコードを避ける**

### ✅ 必ず守るべきルール（絶対厳守）

**1. ファイルパスのハードコード禁止**
- ❌ **禁止**: `main()`内で具体的なパスを直接記述
- ✅ **必須**: コマンドライン引数（argparse）または設定ファイルで外部化

```python
# ❌ 禁止パターン
def main():
    video_path = r"C:\Users\musta\Desktop\PJ\project\video.mp4"  # ハードコード

# ✅ 正しいパターン
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', '-v', required=True, help='入力動画のパス')
    parser.add_argument('--output', '-o', default='output', help='出力ディレクトリ')
    args = parser.parse_args()
    video_path = args.video
```

**2. クロスプラットフォーム対応**
- ❌ **禁止**: Windows専用のフォントパス、パス区切り文字
- ✅ **必須**: OS判定による分岐、`os.path.join()`、`pathlib.Path`の使用

```python
# ❌ 禁止パターン
font_path = r"C:\Windows\Fonts\msgothic.ttc"

# ✅ 正しいパターン
import platform
if platform.system() == 'Windows':
    font_paths = [r"C:\Windows\Fonts\msgothic.ttc", r"C:\Windows\Fonts\meiryo.ttc"]
elif platform.system() == 'Darwin':  # macOS
    font_paths = ["/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"]
else:  # Linux
    font_paths = ["/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"]
```

**3. 言語・ロケール文字列の外部化**
- ❌ **禁止**: 日本語ラベルをコード内にハードコード
- ✅ **必須**: 定数定義、設定ファイル、またはi18n対応

```python
# ❌ 禁止パターン
cv2.putText(frame, "接地", (x, y), font, 1, color)

# ✅ 正しいパターン
LABELS = {
    'ja': {'contact': '接地', 'liftoff': '離地'},
    'en': {'contact': 'Contact', 'liftoff': 'Liftoff'}
}
lang = args.language or 'ja'
cv2.putText(frame, LABELS[lang]['contact'], (x, y), font, 1, color)
```

**4. マジックナンバーの排除**
- ❌ **禁止**: 閾値や定数を数値でハードコード
- ✅ **必須**: 名前付き定数、クラス属性、または引数で定義

```python
# ❌ 禁止パターン
if velocity < 0.004:  # マジックナンバー
    detect_contact()

# ✅ 正しいパターン
VELOCITY_THRESHOLD = 0.004  # 速度閾値（単位: normalized/frame）

class Detector:
    def __init__(self, velocity_threshold=0.004):
        self.velocity_threshold = velocity_threshold
```

**5. 検索パターンの汎用化**
- ❌ **禁止**: 特定ファイル名パターンをハードコード
- ✅ **必須**: 引数またはワイルドカードパターンで指定

```python
# ❌ 禁止パターン
videos = [f for f in os.listdir(path) if "10m" in f]  # 特定パターン固定

# ✅ 正しいパターン
parser.add_argument('--pattern', default='*.mp4', help='検索パターン')
videos = glob.glob(os.path.join(path, args.pattern))
```

### 🎯 汎用性チェックリスト（コード作成前に確認）

コードを作成・修正する前に以下を確認:

- [ ] `main()`内にハードコードされたパスはないか？
- [ ] argparseまたは設定ファイルで入出力を外部化しているか？
- [ ] フォントパスはOS判定で分岐しているか？
- [ ] 日本語ラベルは定数または設定で定義されているか？
- [ ] マジックナンバーは名前付き定数になっているか？
- [ ] 検索パターンは引数で指定可能か？
- [ ] 別環境（他のPC、他のプロジェクト）でも動作するか？

### 📋 必須の引数パターン

**スクリプト作成時は以下の引数を標準で用意:**

```python
parser = argparse.ArgumentParser(description='スクリプトの説明')

# 必須引数
parser.add_argument('input', help='入力ファイル/ディレクトリ')

# オプション引数（推奨）
parser.add_argument('--output', '-o', default='output', help='出力先')
parser.add_argument('--config', '-c', help='設定ファイル（YAML/JSON）')
parser.add_argument('--verbose', '-v', action='store_true', help='詳細出力')
parser.add_argument('--dry-run', action='store_true', help='実行せずに確認のみ')
```

### 🚨 違反パターンと修正

**❌ 違反例: ハードコードだらけのmain()**
```python
def main():
    video = r"C:\Users\musta\Desktop\video.mp4"
    output = r"C:\Users\musta\Desktop\output"
    process(video, output)
```

**✅ 正しい例: 汎用的なmain()**
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('video', help='入力動画')
    parser.add_argument('--output', '-o', default='output', help='出力先')
    args = parser.parse_args()
    process(args.video, args.output)

if __name__ == '__main__':
    main()
```

### 📊 コンプライアンススコアへの影響

- **完全汎用化**: +10点
- **部分的汎用化（引数あり、一部ハードコード）**: +5点
- **main()にハードコードパス**: -15点（違反）
- **クロスプラットフォーム非対応**: -10点
- **マジックナンバー多数**: -10点

### 💾 永続化ルール

このルールは `.claude/CLAUDE.md` に永続化されます。
Pythonスクリプトを作成する際は、必ずこのルールを参照してください。

**適用対象:**
- 全てのPythonスクリプト（`.py`）
- シェルスクリプト（`.sh`, `.bat`）
- 設定を含むあらゆるコード

---

## 🗑️ 一時ファイル自動削除ルール（AUTOMATIC CLEANUP）

**基本原則: タスク完了時に一時ファイルを自動削除し、作業環境をクリーンに保つ**

### ✅ 必須動作（絶対厳守）

**タスク完了時、以下の一時ファイルを必ず削除する:**

#### 削除対象ファイル

1. **一時的なPythonスクリプト**
   - `*_temp.py`, `*_tmp.py`
   - `test_*.py`（テストスクリプト）
   - `verify_*.py`（検証用スクリプト）
   - `analyze_*.py`（分析用スクリプト）
   - `debug_*.py`（デバッグ用スクリプト）
   - タスク固有の名前を持つ一時スクリプト（例: `sensibility_word_mapper_FIXED.py`）

2. **バージョン管理されていない中間ファイル**
   - `*_OLD.py`, `*_BACKUP.py`
   - `*_v1.py`, `*_v2.py`, `*_FIXED.py`, `*_PRODUCTION.py` など複数バージョン
   - 最終版以外のファイル

3. **分析・レポート用の一時ファイル**
   - デバッグログ
   - 一時的な分析結果
   - 作業用のCSV/JSONファイル（最終版以外）

#### 保持すべきファイル

- ✅ **最終成果物**（例: `対訳_厳密版.xlsx`）
- ✅ **ドキュメント**（README.md, レポート等）
- ✅ **元データ**（ユーザー提供のファイル）
- ✅ **プロジェクト固有のスクリプト**（継続使用するもの）

### 🔧 実装パターン

**パターン1: タスク完了時の手動クリーンアップ**

```python
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 削除対象の一時ファイルリスト
temp_files = [
    r"C:\Users\musta\verify_*.py",
    r"C:\Users\musta\analyze_*.py",
    r"C:\Users\musta\*_temp.py",
    r"C:\Users\musta\*_FIXED.py",
    # ... その他の一時ファイル
]

print("🗑️  一時ファイル削除中...")
for pattern in temp_files:
    for file in glob.glob(pattern):
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ 削除: {os.path.basename(file)}")
```

**パターン2: 自己削除スクリプト**

```python
# スクリプトの最後に追加
import os

# タスク完了後、このスクリプト自体を削除
if __name__ == '__main__':
    # メイン処理
    main()

    # 自己削除
    try:
        os.remove(__file__)
        print(f"✅ 削除: {os.path.basename(__file__)}")
    except Exception as e:
        print(f"⚠️  自己削除失敗: {e}")
```

### 📋 チェックリスト（タスク完了時）

タスク完了前に必ず確認:

- [ ] 最終成果物は適切なフォルダに保存されているか？
- [ ] 一時的なPythonスクリプトは全て削除されたか？
- [ ] 複数バージョンのファイルは整理されたか？
- [ ] デバッグ用ファイルは削除されたか？
- [ ] 作業フォルダはクリーンな状態か？

### 🚨 違反パターンと修正

**❌ 違反例: 一時ファイルを放置**
```
タスク完了
　↓
一時ファイル（10個以上）がC:\Users\mustaに残ったまま
　↓
次のタスクで混乱の原因になる
```

**✅ 正しい例: 自動削除**
```
タスク完了
　↓
一時ファイル削除スクリプト実行
　↓
7件削除、作業環境クリーン
　↓
最終成果物のみ整理されたフォルダに残る
```

### 💡 自動化の例

**例1: 日英対訳マッピングタスク完了時**

```
タスク完了時に削除したファイル（実例）:
✅ codex_error_analysis.py
✅ verify_english_list.py
✅ list_files.py
✅ sensibility_word_mapper.py
✅ sensibility_word_mapper_FIXED.py
✅ sensibility_word_mapper_FIXED_v2.py
✅ sensibility_word_mapper_PRODUCTION.py

削除結果: 7件削除 → 作業環境クリーン
```

### 📊 コンプライアンススコアへの影響

- **自動削除実施**: +5点
- **一時ファイル5個以上放置**: -10点（違反）
- **一時ファイル10個以上放置**: -20点（重大違反）

### 💾 永続化とエンフォースメント

このルールは `.claude/CLAUDE.md` に永続化され、以下で強制されます:
- **Layer 6**: Post-task検証（完了時チェック）
- **Session監視**: 一時ファイル数の監視
- **TodoWrite**: タスク完了時にクリーンアップをTODOに追加

### 🎯 ベストプラクティス

1. **タスク開始時**: 一時ファイル保存場所を明確にする
2. **タスク実行中**: 最終版かどうかを明示する（`*_FINAL.py`, `*_厳密版.xlsx`等）
3. **タスク完了時**: 必ずクリーンアップスクリプトを実行
4. **Byterover保存前**: 作業環境がクリーンであることを確認

---

## 🔄 自己テスト・反復改善ルール（ITERATIVE SELF-TESTING）

**基本原則: コード作成後は必ず自分で動作テストを行い、問題があれば自動的に改善を繰り返す**

### ✅ 必須動作（絶対厳守）

**スクリプト・アプリケーション作成時は以下のフローを必ず実行:**

#### Step 1: 実装完了後、即座にテスト実行
```
コード実装完了 → Bashツールで実行 → 結果を確認
```

#### Step 2: エラー・問題発見時は自動修正
```
エラー発生 → 原因分析 → コード修正 → 再テスト（Step 1に戻る）
```

#### Step 3: 成功するまで繰り返し
```
❌ 1回目: エラー → 修正 → 再テスト
❌ 2回目: 期待と異なる → 調整 → 再テスト
✅ 3回目: 成功 → 完了報告
```

### 🚨 禁止事項

**❌ 絶対禁止: テストせずに完了報告**
```
❌ 「スクリプトを作成しました。実行してください。」
✅ 「スクリプトを作成し、テスト実行しました。結果: 成功」
```

**❌ 絶対禁止: 1回のエラーで諦める**
```
❌ エラー発生 → 「エラーが出ました。確認してください」
✅ エラー発生 → 原因特定 → 修正 → 再テスト → 成功まで繰り返し
```

### 📋 テスト実行のチェックリスト

- [ ] スクリプトを実際に実行したか？
- [ ] 出力結果を確認したか？
- [ ] エラーがあれば修正して再実行したか？
- [ ] 期待通りの結果が得られたか？

### 🎯 具体例

**例: 接地離地検出スクリプト改善**
```
1. generate_ground_contact_video.py を作成
2. py scripts/generate_ground_contact_video.py 実行
3. 結果: 「2回しか検出されない」→ 期待と異なる
4. 原因分析: 「物理的制約が厳しすぎる」
5. パラメータ調整
6. 再テスト → 結果: 「5回検出」→ 成功
7. ユーザーに報告
```

### 📊 コンプライアンススコアへの影響

- **自己テスト実施・成功**: +10点
- **エラー時に自動修正**: +5点
- **テストせずに完了報告**: -20点（重大違反）
- **1回のエラーで諦める**: -15点（違反）

### 🔧 反復回数の目安

| 複雑度 | 最大反復回数 |
|--------|-------------|
| 単純なスクリプト | 3回 |
| 中程度のアプリ | 5回 |
| 複雑なシステム | 10回 |

**10回を超えても解決しない場合**: ユーザーに状況を報告し、方針を相談

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

## ❓ 曖昧な要求には必ず質問する義務（MANDATORY CLARIFICATION PROTOCOL）

**基本原則: 不明点・曖昧な表現があれば、推測せず必ず質問する**

### ✅ 必ず守るべきルール（絶対厳守）

**1. 曖昧な表現を検出したら即座に質問する**
- ✅ **正しい**: 不明点をリスト化して質問してから実装
- ❌ **禁止**: 「おそらく」「たぶん」「推測すると」で進める

**適用範囲**:
- **全てのユーザープロンプト**
- LookML実装、データ分析、ファイル操作など全タスク

### 🚨 曖昧と判断すべきパターン

#### パターン1: 曖昧な指示語

**日本語:**
- ❌ 「適当に」「よしなに」「いい感じに」「お任せ」
- ❌ 「推測して」「察して」「うまく」「それっぽく」
- ❌ 「ざっくり」「なんとなく」「テキトー」「適宜」

**英語:**
- ❌ "somehow", "automatically", "figure it out"
- ❌ "guess", "whatever", "anything", "something like"

**検出時の対応:**
```
❌ 間違い: 推測で実装を進める
✅ 正しい: 「具体的にどのように実装しますか？」と質問
```

#### パターン2: 結合キーが不明

**シナリオ:**
```
User: "テーブルAとテーブルBを結合して"
```

**検出ポイント:**
- 結合キーが明示されていない
- 結合タイプ（INNER/LEFT/RIGHT）が不明

**必須の質問:**
```
✋ 以下を確認させてください：
   1. 結合キーは何ですか？
      - テーブルA の [フィールド名] = テーブルB の [フィールド名]
   2. 結合タイプは何ですか？
      - INNER JOIN / LEFT JOIN / RIGHT JOIN
   3. 追加のフィルター条件はありますか？
```

#### パターン3: フィルター条件が不明確

**シナリオ:**
```
User: "適切なデータだけ抽出して"
User: "必要なものだけフィルターして"
```

**必須の質問:**
```
✋ フィルター条件を具体的に教えてください：
   - どのフィールドで絞り込みますか？
   - 条件は何ですか？（例: status = 'active'）
   - 複数条件の場合、AND/ORどちらですか？
```

#### パターン4: フィールド名が曖昧

**シナリオ:**
```
User: "営業担当者を追加して"
User: "売上を表示して"
```

**必須の質問:**
```
✋ フィールド名を確認させてください：
   - 営業担当者フィールド: bqbusiness_discussions___sales_staff_namebq ですか？
   - 売上フィールド: detail01（受注時）ですか？それとも detail34（実績）ですか？
```

#### パターン5: 類似要求（具体性欠如）

**シナリオ:**
```
User: "前と同じように"
User: "似たようなの作って"
```

**必須の質問:**
```
✋ 「前/似た」の具体的な内容を教えてください：
   - どのファイル/実装を参考にしますか？
   - どの部分を同じにして、どの部分を変更しますか？
```

### ✅ 正しい対応フロー

#### ステップ1: 曖昧性を検出

```
<thinking>
ユーザープロンプトを分析：
- 「適当に」という曖昧な表現を検出
- テーブル結合キーが明示されていない
- フィルター条件が不明確

→ 実装を開始せず、質問をリスト化する
</thinking>
```

#### ステップ2: 不明点を質問としてリスト化

```
以下の点が不明です。教えてください：

1. 【結合キー】テーブルAとBの結合キーは何ですか？
   - 例: A.customer_id = B.customer_id

2. 【フィルター条件】どの条件で絞り込みますか？
   - 例: status = 'active' AND created_at > '2025-01-01'

3. 【フィールド名】営業担当者フィールドは以下のどちらですか？
   - bqbusiness_discussions___sales_staff_namebq
   - その他のフィールド

回答いただき次第、実装を開始します。
```

#### ステップ3: ユーザーの回答を待つ

```
❌ 禁止: 回答を待たずに推測で実装
✅ 正しい: ユーザーの明示的な回答を得てから実装
```

#### ステップ4: 回答を得てから実装

```
ありがとうございます。確認した内容で実装します：
- 結合キー: A.customer_id = B.customer_id
- フィルター: status = 'active'
- 営業担当: bqbusiness_discussions___sales_staff_namebq

では実装を開始します。
```

### 🎯 具体例：正しい対応 vs 間違った対応

#### ケース1: 「適当に」要求

```
❌ 間違った対応:
User: "営業担当者を適当に追加して"
→ 推測でbqemployee_namebqを使用して実装

✅ 正しい対応:
User: "営業担当者を適当に追加して"
→ 「営業担当者フィールドは以下のどれですか？
    1. bqbusiness_discussions___sales_staff_namebq（営業担当者名）
    2. bqsales_staffbq（営業担当者ID）
    3. その他

    また、どこに追加しますか？（ファイル名とセクション）」
→ ユーザーの回答を待つ
```

#### ケース2: テーブル結合（キー不明）

```
❌ 間違った対応:
User: "business_discussionsとemployeeを結合して"
→ 他のビューを参考に推測
→ 勝手にbd.employee_id = e.idで実装

✅ 正しい対応:
User: "business_discussionsとemployeeを結合して"
→ 「結合キーを教えてください：
    - business_discussions の [フィールド] = employee の [フィールド]

    また、結合タイプは何ですか？
    - INNER JOIN / LEFT JOIN / RIGHT JOIN」
→ ユーザーの回答を待つ
```

#### ケース3: フィルター条件（条件不明）

```
❌ 間違った対応:
User: "適切なデータだけ表示して"
→ 推測でstatus = 'active'を勝手に追加

✅ 正しい対応:
User: "適切なデータだけ表示して"
→ 「フィルター条件を具体的に教えてください：
    - どのフィールドで絞り込みますか？
    - 条件式を教えてください
      （例: status = 'active', created_at > '2025-01-01'）」
→ ユーザーの回答を待つ
```

### 📋 実装前チェックリスト（必須）

プロンプトを受け取ったら、実装前に以下を確認：

- [ ] 曖昧な指示語（「適当に」等）は使われていないか？
- [ ] テーブル結合がある場合、結合キーは明示されているか？
- [ ] フィルター条件は具体的に指定されているか？
- [ ] フィールド名は明確に指定されているか？
- [ ] 「前と同じ」「似たような」等の曖昧な参照はないか？

**1つでもチェックが入れば、実装を開始せず質問する。**

### 🔴 禁止事項

#### 絶対に使ってはいけない表現

実装時に以下の表現を使うことは**絶対禁止**:

- ❌ 「おそらく〇〇だと思います」
- ❌ 「たぶん〇〇でしょう」
- ❌ 「推測すると〇〇です」
- ❌ 「〇〇だと仮定します」
- ❌ 「〇〇かもしれません」

これらの表現が出そうになったら、**即座に質問に切り替える**。

### 💾 Hooks統合

この質問義務は以下で強制されます:

- **user-prompt-submit.bat**: プロンプト送信時にリマインダー表示
- **ambiguity_detector.py**: 曖昧性自動検出（将来実装）
- **violation_tracker.py**: 推測実装の違反記録

### 📊 違反時の影響

| 違反内容 | 違反スコア | 影響 |
|---------|----------|------|
| 曖昧な要求を質問せず推測実装 | +25点 | 重大違反 |
| 「おそらく」等の推測表現使用 | +15点 | 警告 |
| 結合キー不明のまま実装 | +20点 | 重大違反 |

**50点以上でプロンプトブロック**

### ✨ ベストプラクティス

#### 質問の仕方（良い例）

```
✅ Good:
「以下の点を確認させてください：
 1. 【結合キー】テーブルAとBをどのフィールドで結合しますか？
 2. 【フィルター】どの条件で絞り込みますか？
 3. 【フィールド名】営業担当者は以下のどちらですか？
    - bqbusiness_discussions___sales_staff_namebq
    - bqemployee_namebq

 回答いただき次第、実装を開始します。」
```

```
❌ Bad:
「ちょっと不明点があります。教えてください。」
（具体性がない）
```

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

---

## 📊 商談テーブル（o10936_business_discussions）フィールドマッピング

### 営業担当者フィールド（重要）

**商談テーブルには複数の「営業担当者」関連フィールドがあり、入力率が大きく異なる。**

#### ✅ 正しいフィールド（99.8%入力あり）

| 用途 | BigQueryフィールド | 入力率 |
|------|-------------------|--------|
| **営業担当者名** | `bqbusiness_discussions___employee_namebq` | 99.8% |
| **営業担当者コード** | `bqsales_cdbq` | 99.8% |

#### ❌ 使用しないフィールド（ほぼ空）

| 用途 | BigQueryフィールド | 入力率 |
|------|-------------------|--------|
| 営業担当者ID | `bqsales_staffbq` | 2.9% |
| 営業担当者名（別） | `bqbusiness_discussions___sales_staff_namebq` | 2.9% |

#### 工務担当者フィールド

| 用途 | BigQueryフィールド | 入力率 |
|------|-------------------|--------|
| 工務担当者ID | `bqconstruction_employeebq` | 60% |
| 工務担当者名 | `bqbusiness_discussions___employee_name___construction_employeebq` | 60% |

### CSVとBigQueryの対応

| CSVカラム名（地球UI） | BigQueryフィールド |
|----------------------|-------------------|
| 営業担当者 | `bqbusiness_discussions___employee_namebq` |
| 営業担当者コード | `bqsales_cdbq` |
| 工務担当者 | `bqbusiness_discussions___employee_name___construction_employeebq` |
| 工務担当者コード | `bqconstruction_employeebq` |

### 注意事項

- `bqsales_staffbq` と `bqbusiness_discussions___sales_staff_namebq` は**使用禁止**（ほぼ空）
- 営業担当者名は `bqbusiness_discussions___employee_namebq` を直接使用（JOINは不要）
- 2025-12-19 調査結果

### 修正済みファイル（2025-12-19）

| ファイル | 修正内容 |
|---------|---------|
| `HW_Pipeline_Value_detail.view.lkml` | `bqsales_staffbq` → `bqsales_cdbq`, `bqbusiness_discussions___sales_staff_namebq` → `bqbusiness_discussions___employee_namebq` |
| `marginal_profitforecast_sales_detail.view.lkml` | 同上（7箇所のUNION ALL全て修正） |

### 要修正の可能性があるファイル

`bqbusiness_discussions___sales_staff_namebq` を使用しているファイルは同様の問題が発生する可能性あり。
検索コマンド:
```bash
grep -r "bqsales_staffbq" views/
grep -r "bqbusiness_discussions___sales_staff_namebq" views/
```

---

## 🧠 Serenaメモリ活用ルール（MANDATORY MEMORY USAGE）

**基本原則: 重要な調査結果・学習内容はSerenaメモリに保存し、次回以降のセッションで活用する**

### ✅ 必ず守るべきルール

**1. 調査結果・発見事項の保存**
- 新しいフィールドマッピング情報
- データ入力率の調査結果
- バグの原因と修正方法
- プロジェクト固有のルール

**2. セッション開始時のメモリ確認**
```
タスク開始時:
1. mcp__serena__list_memories で利用可能なメモリを確認
2. 関連するメモリがあれば mcp__serena__read_memory で読み込む
3. 過去の知識を踏まえて作業を開始
```

**3. 保存すべき情報の例**
- BigQueryフィールドマッピング（正しいフィールド vs 使用禁止フィールド）
- LookML実装パターン
- テーブル結合キー
- 修正履歴と根本原因

### 🔧 Serenaメモリコマンド

```python
# メモリ一覧を確認
mcp__serena__list_memories()

# メモリを読み込む
mcp__serena__read_memory(memory_file_name="business_discussions_field_mapping")

# メモリに書き込む
mcp__serena__write_memory(
    memory_file_name="your_memory_name",
    content="# タイトル\n\n内容..."
)

# メモリを編集
mcp__serena__edit_memory(
    memory_file_name="your_memory_name",
    needle="置換前",
    repl="置換後",
    mode="literal"
)

# メモリを削除
mcp__serena__delete_memory(memory_file_name="your_memory_name")
```

### 📋 現在保存されているメモリ

| メモリ名 | 内容 |
|---------|------|
| `business_discussions_field_mapping` | 商談テーブルのフィールドマッピング情報（営業担当者/工務担当者フィールド） |

### 🎯 メモリ保存のタイミング

1. **データ調査後**: フィールド入力率やマッピング情報を発見した時
2. **バグ修正後**: 根本原因と修正方法を記録
3. **新しいパターン発見後**: 再利用可能な実装パターン
4. **ユーザーから「記憶して」と言われた時**: 即座にSerenaメモリに保存

### 📊 コンプライアンススコアへの影響

- **調査結果をメモリに保存**: +5点
- **セッション開始時にメモリ確認**: +3点
- **重要な発見を保存せずに終了**: -10点

---

## 🔴 SQLエラー自動メモリ保存ルール（AUTOMATIC ERROR MEMORY）

**基本原則: SQLエラーが発生したら、その対処法を汎用的にまとめてSerenaメモリに保存する**

### ✅ 必ず守るべきルール（絶対厳守）

**1. SQLエラー発生時の対応フロー**
```
エラー発生
  ↓
原因を特定
  ↓
修正して再実行
  ↓
成功したら、エラーと対処法を汎用的にまとめる
  ↓
Serenaメモリ（sql_runner_tips）に追記
```

**2. メモリに保存する内容**
- エラーメッセージ（例）
- 原因の説明
- ❌ NG例（間違ったコード）
- ✅ OK例（正しいコード）
- 汎用的なポイント

**3. メモリ保存先**
- **メモリ名**: `sql_runner_tips`
- **追記方法**: `mcp__serena__edit_memory` で既存内容に追加

### 🔧 保存フォーマット

```markdown
## エラー: [エラータイプ]

**エラー例:**
\`\`\`
[エラーメッセージ]
\`\`\`

**原因:**
- [原因の説明]

**❌ NG例:**
\`\`\`sql
[間違ったコード]
\`\`\`

**✅ OK例:**
\`\`\`sql
[正しいコード]
\`\`\`
```

### 📋 対象エラー

- BigQuery構文エラー
- SQL Runner固有のエラー
- 日本語文字エラー
- JOIN/UNNEST関連エラー
- その他のSQLエラー

### 🎯 目的

- **同じミスを繰り返さない**
- **過去のエラー対処を即座に参照できる**
- **学習内容をセッション間で共有**

### 📊 コンプライアンススコアへの影響

- **エラー対処をメモリに保存**: +5点
- **同じエラーを2回以上繰り返す**: -15点（違反）
- **メモリを参照せずにエラー**: -10点

<!-- einja-harness:start core -->
## 体制の根幹

チームは自己組織化して、自分で決めて進める。人の判断待ちで止まらない。人の作業待ちで止まるのは、AI チームの怠慢である。人は、筋の悪いものだけ止める。止められたら、仕組みを直して、同じ筋の悪さが出ないようにしてから出し直す。

決めたことは、根拠を1つの URL で示して進める。判断の依頼と、作業の依頼は別である。

作業の依頼は原則禁止。人が行うのは、AI が開いた画面でのパスワード、二段階認証、支払い確定の入力だけである。画面を開くことと、そのあとの作業は AI が行う。WorkOS の再認可、MCP の再認可、ブラウザ操作、設定は、人の操作ではない。手順は渡さない。その入力が要るときだけ、AI が開いたその画面の前で待つ。

次の方針は、一輝さんの合意を取ってから実装する。調査、材料づくり、作業ブランチでの試作は進めてよい。

1. 製品の機能範囲、画面の骨組み、データの正本を決める、または変える
2. 使われている本番の権限、アカウント、見え方を変える
3. 毎月の新しい支出、または外部サービスの契約
4. 戻せない構造の変更（履歴、改名、アーカイブ、削除）
5. 人の時間を使う（作業、会議、レビュー、確認を割り当てる。報告は含まない）
6. 一輝さんの過去の発言と食い違う件、または一輝さんが「一緒に決めたい」と言った件

技術の細部、戻せる設定、手順、名前は、チームで決めて進め、報告する。

合意が要る件は、判断依頼台帳に1件1行で起票する。台帳は Plane の task-force、作業項目タイプ「判断依頼」（id `bdabead8-4ed0-4d53-bd75-63e6431adb9a`）。decider は `human:渡邉`。本文には、何を決めるか、選択肢と選ぶと何が変わるか、推奨と理由、根拠の URL（Doop は Proto リンク）、いまの実装の位置、返事が無いと止まるものを書く。報告の先頭に「判断依頼: <行のURL>」と書く。

判断依頼の宛先は開発統括である。開発統括は T3 の外にいる。T3 で宛先のスレッドを探さない。台帳に起票すれば、開発統括の見回りが拾って一輝さんに送る。

返事を待つ間は、その方針に頼らない作業を進める。「止めない」は、合意なしで実装することではない。「筋が悪ければ止めて」を、判断依頼の代わりにしない。

正本は einja-skills の `docs/ai-ops/judgment-principles.md`（D-2026-11-17-02、D-2026-11-17-03、D-2026-11-17-04、D-2026-11-17-05）。
<!-- einja-harness:end core -->
