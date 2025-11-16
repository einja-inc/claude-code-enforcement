# CLAUDE.md Rule Enforcement System - Complete Guide

**Status**: ✅ FULLY OPERATIONAL
**Last Updated**: 2025-11-17
**Purpose**: 違反蓄積システムでCLAUDE.mdルールを強制

---

## 🎯 概要

このシステムは **ULTRA THINK MODE** と **CLAUDE.mdルール** を実際に強制します：

- ✅ `<thinking>`ブロック使用を検証
- ✅ 違反を自動記録
- ✅ 違反が蓄積するとプロンプトをブロック
- ✅ リセット機能で再開可能

---

## 🔧 コンポーネント

### 1. Violation Tracker (違反追跡システム)

**ファイル**: [.claude/scripts/violation_tracker.py](.claude/scripts/violation_tracker.py)

**機能**:
- 違反の種類ごとに重みを設定
- 違反スコアを累積
- ブロック閾値を超えたら警告

**違反の種類と重み**:
```python
"no_thinking": 10           # thinkingブロックなし
"no_codex": 15             # Codex協力なし（複数ファイル）
"no_todowrite": 5          # TodoWrite不足
"unauthorized_change": 25  # 勝手な要件変更
"sample_data_confusion": 20 # サンプルデータ誤表示
```

**閾値**:
- **警告**: 30点
- **ブロック**: 50点

### 2. User Prompt Submit Hook (強制版)

**ファイル**: [.claude/hooks/user-prompt-submit.bat](.claude/hooks/user-prompt-submit.bat)

**機能**:
- プロンプト送信前に違反スコアをチェック
- スコアが50点以上 → **プロンプトをブロック**
- ブロック時にリセット方法を表示

### 3. Assistant Response Hook (違反記録版)

**ファイル**: [.claude/hooks/assistant-response.bat](.claude/hooks/assistant-response.bat)

**機能**:
- 応答完了後にthinkingブロックをチェック
- thinkingブロックなし → **違反を自動記録**
- 違反スコアと警告を表示
- デスクトップ通知送信

### 4. Violation Reset Script

**ファイル**: [.claude/scripts/reset_violations.bat](.claude/scripts/reset_violations.bat)

**機能**:
- 違反履歴をリセット
- ブロックを解除
- 確認プロンプト付き

---

## 🚀 動作フロー

### 正常フロー

```
1. ユーザーがプロンプト入力
   ↓
2. user-prompt-submit.bat:
   - 違反スコアをチェック
   - OK (< 50点) → 通過
   - ULTRA THINK MODEリマインダー表示
   ↓
3. Claude処理（<thinking>使用）
   ↓
4. assistant-response.bat:
   - thinkingブロック検証 → ✅ OK
   - 違反記録なし
   - デスクトップ通知
```

### 違反発生フロー

```
1. ユーザーがプロンプト入力
   ↓
2. user-prompt-submit.bat: 通過 (まだスコア低い)
   ↓
3. Claude処理（thinkingブロック使わず）
   ↓
4. assistant-response.bat:
   - thinkingブロック検証 → ❌ NG
   - [VIOLATION] no_thinking (+10点) 記録
   - 警告表示
   ↓
5. 次回プロンプト:
   - スコア累積で50点超過
   - user-prompt-submit.bat: [BLOCKED] プロンプト拒否
   - リセット方法を表示
```

---

## 💻 使い方

### 違反ステータス確認

```bash
py .claude\scripts\violation_tracker.py check
```

**出力例**:
```
==============================================================
  CLAUDE.md Rule Compliance - Violation Status
==============================================================

Total Violation Score: 35
Warning Threshold:     30
Block Threshold:       50

[STATUS] WARNING - Approaching block threshold

Recent Violations (3 total):
--------------------------------------------------------------
  [2025-11-17T01:15:23]
  Type: no_thinking (Weight: 10)
  Details: Response without thinking blocks
...
==============================================================
```

### 違反リセット

**方法1: バッチファイル**
```bash
.claude\scripts\reset_violations.bat
```

**方法2: 直接コマンド**
```bash
py .claude\scripts\violation_tracker.py reset
```

### 手動で違反を追加（テスト用）

```bash
py .claude\scripts\violation_tracker.py add no_thinking "Test violation"
```

### ブロック状態確認

```bash
py .claude\scripts\violation_tracker.py is_blocked
```

**Exit Code**:
- `0`: ブロックされていない
- `1`: ブロック中

---

## 🧪 テスト

### 統合テスト実行

```bash
.claude\scripts\test_enforcement.bat
```

**テスト内容**:
1. ✅ 違反リセット
2. ✅ 初期状態（ブロックなし）
3. ✅ 小さい違反追加
4. ✅ まだブロックされない
5. ✅ 複数違反追加で閾値超過
6. ✅ ブロック状態確認
7. ✅ プロンプトブロック動作
8. ✅ リセット後ブロック解除

**結果**: 全8テスト合格 ✅

---

## 📊 違反の記録場所

**ファイル**: `C:\Users\<username>\.claude\logs\violations.json`

**フォーマット**:
```json
{
  "total_score": 35,
  "violations": [
    {
      "type": "no_thinking",
      "weight": 10,
      "details": "Response without thinking blocks",
      "timestamp": "2025-11-17T01:15:23.456789"
    }
  ],
  "last_reset": "2025-11-17T00:00:00.000000"
}
```

---

## ⚠️ ブロックされた場合の対処

### 状況確認

1. **現在のスコアを確認**:
   ```bash
   py .claude\scripts\violation_tracker.py check
   ```

2. **違反履歴を確認**:
   - どの違反が多いか確認
   - thinking使用忘れ？Codex協力忘れ？

### リセット

**注意**: リセットは違反履歴を完全に消去します。

```bash
.claude\scripts\reset_violations.bat
```

または

```bash
py .claude\scripts\violation_tracker.py reset
```

### 今後の対策

- ✅ `<thinking>`ブロックを常に使う
- ✅ 複数ファイル修正時はTask(codex)を呼ぶ
- ✅ TodoWriteで8-10項目作成
- ✅ CLAUDE.mdルールを守る

---

## 🔧 カスタマイズ

### 閾値変更

[violation_tracker.py:29-30](.claude/scripts/violation_tracker.py#L29-L30)を編集:

```python
self.block_threshold = 50   # この値を変更
self.warning_threshold = 30 # この値を変更
```

### 違反の重み変更

[violation_tracker.py:22-27](.claude/scripts/violation_tracker.py#L22-L27)を編集:

```python
self.violation_weights = {
    "no_thinking": 10,          # 重みを変更
    "no_codex": 15,             # 重みを変更
    # ...
}
```

### 新しい違反タイプ追加

1. `violation_weights`に追加:
   ```python
   "new_violation_type": 20,
   ```

2. assistant-response.batまたは他のhookで検出:
   ```bat
   py "%VIOLATION_TRACKER%" add new_violation_type "Details"
   ```

---

## 📈 統計と監視

### 違反トレンド確認

```bash
# violations.jsonを直接確認
type %USERPROFILE%\.claude\logs\violations.json
```

### 自動監視（将来実装予定）

- Session Monitorとの統合
- グラフィカルなダッシュボード
- 週次レポート

---

## 🎓 ベストプラクティス

### 違反を避けるために

1. **毎回thinkingブロックを使う**
   ```
   <thinking>
   1. タスクの理解
   2. アプローチ検討
   3. ルール確認
   4. 実装計画
   </thinking>
   ```

2. **複雑なタスクでCodex協力**
   - 2ファイル以上の修正
   - データ分析
   - LookML編集

3. **TodoWriteで計画**
   - 8-10項目に分解
   - 進捗を追跡

4. **CLAUDE.mdを定期確認**
   - [.claude/CLAUDE.md](.claude/CLAUDE.md)

### リセットのタイミング

**リセットすべき時**:
- ✅ 違反が蓄積したが、ルールを理解した
- ✅ テスト用の違反を消したい
- ✅ 新しいセッション開始時

**リセットすべきでない時**:
- ❌ 単にブロックを回避したいだけ
- ❌ ルールを理解していない状態
- ❌ 違反が繰り返される

---

## 🔗 関連ドキュメント

- **CLAUDE.md**: 全ルールの詳細
- **THINKING_ENFORCEMENT_GUIDE.md**: thinking強制の詳細
- **IMPLEMENTATION_SUMMARY.md**: 実装サマリー
- **8-Layer Enforcement System**: `.claude/enforcement/SYSTEM_READY.md`

---

## ✨ まとめ

### システムの特徴

✅ **自動検出**: thinkingブロック使用を自動チェック
✅ **段階的警告**: 30点で警告、50点でブロック
✅ **可逆性**: リセット機能で再開可能
✅ **透明性**: 違反履歴と理由を明示
✅ **拡張性**: 新しい違反タイプを追加可能

### 期待される効果

- 🎯 ULTRA THINK MODE使用率 100%
- 🎯 CLAUDE.mdルール遵守率 95%+
- 🎯 コード品質向上
- 🎯 一貫性のある開発プロセス

---

**システムは完全に稼働中です。今後のClaude Codeセッションで自動的に機能します。**
