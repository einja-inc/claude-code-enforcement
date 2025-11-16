# Session Monitor - クイックスタートガイド

**5分で動かす！8-Layer Enforcement System**

## ステップ1: 依存パッケージインストール

```bash
cd C:\Users\musta\.claude\enforcement
pip install watchdog PyYAML
```

**任意（Windows Toast通知を使う場合）**:
```bash
pip install win10toast
```

## ステップ2: 監視開始

```bash
python session_monitor.py
```

**出力例**:
```
✅ Session Monitor initialized
📂 Watching: C:\Users\musta\.claude\shell-snapshots
📊 Initial Compliance Score: 100%

======================================================================
🚀 8-Layer Enforcement System - Session Monitor Started
======================================================================
📂 Monitoring: C:\Users\musta\.claude\shell-snapshots
📊 Initial Compliance Score: 100%
⏳ Watching for violations...
   Press Ctrl+C to stop
======================================================================
```

## ステップ3: Claude Codeを使う

**別のターミナルで**:
```bash
claude
```

通常通りClaude Codeを使用してください。
違反が検出されると、自動的に通知されます。

## ステップ4: 違反を確認

### コンソール出力例
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

### Windows Toast通知（win10toastインストール済みの場合）
- デスクトップ右下に通知が表示されます
- 5秒間表示されます

### ログファイル確認
```bash
# 違反ログ
type C:\Users\musta\.claude\enforcement\logs\violations.jsonl

# スコアログ
type C:\Users\musta\.claude\enforcement\logs\compliance_scores.jsonl
```

## ステップ5: 停止

`Ctrl+C` を押すと、最終統計が表示されて停止します:

```
======================================================================
⏹️  Session Monitor Stopped
======================================================================

======================================================================
📊 Session Monitor Statistics
======================================================================
稼働時間: 123.4秒
監視ファイル数: 2
分析行数: 45
検出違反数: 3
現在スコア: 70%
合格状態: ✅ PASSING
======================================================================
```

## トラブルシューティング

### Q: "設定ファイルが見つかりません"
**A**: session_monitor.pyと同じディレクトリで実行してください。
```bash
cd C:\Users\musta\.claude\enforcement
python session_monitor.py
```

### Q: "log_directoryが存在しません"
**A**: 自動作成されます。もしエラーが出る場合:
```bash
mkdir C:\Users\musta\.claude\shell-snapshots
```

### Q: 文字化けする
**A**: config.yamlの通知設定を確認:
```yaml
notification:
  method: "console"  # "windows" → "console" に変更
```

## 次のステップ

- **違反を減らす**: CLAUDE.mdのルールを確認
- **自動起動**: Windowsタスクスケジューラで起動時に自動実行
- **カスタマイズ**: config.yamlで設定をカスタマイズ

## 詳細情報

- [README.md](README.md) - 完全なドキュメント
- [config.yaml](config.yaml) - 設定ファイル
- [PHASE-1-IMPLEMENTATION-GUIDE.md](../docs/PHASE-1-IMPLEMENTATION-GUIDE.md) - 実装ガイド
