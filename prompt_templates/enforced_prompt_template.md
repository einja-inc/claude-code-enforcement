# Claude Code 強制プロンプトテンプレート

## 使い方

以下のテンプレートをコピーして、あなたの要求の前に貼り付けてください。

---

## 標準テンプレート（全タスク）

```
【必須ルール】
1. <thinking>ブロックを使用して思考プロセスを明示
2. 不明点があれば必ず質問してから実装
3. Task('Codex', '分析内容', 'analyst')でCodex協力

【あなたの要求】
[ここに実際の要求を書く]
```

---

## ファイル修正テンプレート

```
【必須ルール】
1. <thinking>ブロックで分析
2. Task('Codex', 'ファイル構造を分析して最適な修正箇所を特定', 'analyst')
3. Codexの分析結果を踏まえて修正

【要求】
[ファイル名]を修正して[内容]
```

---

## データ分析テンプレート

```
【必須ルール】
1. <thinking>ブロックで分析計画を立てる
2. サンプルデータと実データを明確に区別
3. Task('Codex', 'データ構造を分析', 'analyst')で協力

【要求】
[データ分析の内容]
```

---

## LookML修正テンプレート

```
【必須ルール】
1. <thinking>ブロックで要件分析
2. 不明なフィールド名・結合キーは必ず質問
3. Task('Codex', 'LookML構造を分析して既存ロジックとの整合性確認', 'analyst')

【要求】
[LookML修正内容]
```

---

## 🔧 VS Codeスニペット版

VS Codeで素早く入力できるスニペットを設定：

1. `Ctrl + Shift + P`
2. `Preferences: Configure User Snippets`
3. `markdown.json` を選択
4. 以下を追加：

```json
{
  "Claude Enforced Prompt": {
    "prefix": "cenforce",
    "body": [
      "【必須ルール】",
      "1. <thinking>ブロックを使用して思考プロセスを明示",
      "2. 不明点があれば必ず質問してから実装",
      "3. Task('Codex', '分析内容', 'analyst')でCodex協力",
      "",
      "【要求】",
      "$1"
    ],
    "description": "Claude Code enforced prompt template"
  },
  "Claude File Modification": {
    "prefix": "cfile",
    "body": [
      "【必須ルール】",
      "1. <thinking>ブロックで分析",
      "2. Task('Codex', 'ファイル構造を分析', 'analyst')",
      "3. Codexの分析結果を踏まえて修正",
      "",
      "【要求】",
      "$1を修正して$2"
    ],
    "description": "File modification with Codex"
  }
}
```

**使い方:**
- `cenforce` と入力 → Tab → 自動展開
- `cfile` と入力 → Tab → ファイル修正テンプレート展開

---

## 📋 チェックリスト付きテンプレート

```
【実行前チェック】
□ <thinking>ブロックを使う
□ 不明点は質問する
□ Codex協力する

【要求】
[あなたの要求]

【期待する動作】
1. thinkingブロックで分析
2. 不明点があれば質問
3. Codex協力してから実装
```

---

## 💡 Tips

### 短縮版（最小限）
```
Think + Codex + 質問義務

[要求内容]
```

### 詳細版（複雑タスク）
```
【必須プロトコル】
1. ULTRA THINK MODE: <thinking>で多角的分析
2. CLARIFICATION: 曖昧な点は全て質問
3. CODEX COLLABORATION: Task('Codex', '詳細', 'analyst')
4. TODOWRITE: 8-10項目に分解

【要求】
[詳細な要求内容]
```

---

## 🎯 おすすめ

**日常的に使うなら:**
→ VS Codeスニペット（`cenforce`で自動展開）

**複雑なタスクなら:**
→ 詳細版テンプレートをコピペ

**最も確実:**
→ 毎回プロンプトの最初に【必須ルール】を明記
