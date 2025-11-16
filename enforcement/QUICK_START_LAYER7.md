# Layer 7: 自動修正提案システム - クイックスタート

**最短5分で動作確認できるガイド**

---

## 🚀 5分で始める

### Step 1: 依存関係インストール（1分）

```bash
cd C:\Users\musta\.claude\enforcement
pip install colorama PyYAML
```

### Step 2: 動作確認（2分）

```bash
# 簡単なテスト実行
py integrated_correction.py --text "Edit 'test.lkml'"
```

**期待される出力**:
```
🔍 違反検出: 1件
[ERROR] no_codex_collaboration
コンプライアンススコア: 80%
✅ 評価: GOOD（良好）
```

### Step 3: 詳細テスト（2分）

```bash
# テストスイート実行
test_auto_correction.bat
```

**完了！** これでLayer 7が動作しています。

---

## 📋 よく使うコマンド

### コマンド1: テキスト分析
```bash
py integrated_correction.py --text "あなたのコード"
```

### コマンド2: ファイル分析
```bash
py integrated_correction.py --file "sample.txt"
```

### コマンド3: 会話ログ分析
```bash
py integrated_correction.py --log "C:\Users\musta\.claude\shell-snapshots\session_20251115.jsonl"
```

### コマンド4: レポート生成
```bash
py integrated_correction.py --text "コード" --report
```

---

## 🎯 使用例

### 例1: Codex協力なし違反

**入力**:
```
Edit "file.lkml"
```

**出力**:
```
❌ 違反: no_codex_collaboration (-20点)

正しいパターン:
[Single Message]:
  Read "file.lkml"
  Task("Codex Analyst", "分析", "analyst")
  Edit "file.lkml"
```

### 例2: TodoWrite不足

**入力**:
```
TodoWrite { todos: [
  {content: "修正", status: "pending", activeForm: "修正中"}
]}
```

**出力**:
```
❌ 違反: insufficient_todowrite (-10点)
現在: 1個、必要: 8個
```

### 例3: サンプルデータ明示なし

**入力**:
```
sample data: {"id": 123}
```

**出力**:
```
❌ 違反: sample_data_confusion (-50点)

正しいパターン:
⚠️ これは**サンプルデータ**です
data_type: "SAMPLE"
```

---

## 🔍 トラブルシューティング（1分で解決）

### Q: coloramaエラー
```bash
pip install colorama
```

### Q: 文字化け
既に自動対応済み（UTF-8設定）

### Q: 修正提案が表示されない
```bash
# --no-suggestions フラグを外す
py integrated_correction.py --text "..."
```

---

## 📚 詳細ドキュメント

- **完全ガイド**: `README_AUTO_CORRECTION.md`
- **実装サマリー**: `IMPLEMENTATION_SUMMARY_LAYER7.md`
- **アーキテクチャ**: `docs/8-LAYER-SYSTEM-ARCHITECTURE.md`

---

## 🎓 次のステップ

1. **session_monitor.py への統合**
   - Layer 5（リアルタイム監視）と連携
   - 違反検出時に自動的に修正提案を表示

2. **VS Code統合**
   - Quickfixとして修正提案を表示
   - ショートカットキーで即座に修正

3. **自動修正機能**
   - ユーザーの承認を得て自動修正
   - `root_file_creation` から開始

---

**完了時間**: 約5分
**次の目標**: session_monitor.py統合（10分）
