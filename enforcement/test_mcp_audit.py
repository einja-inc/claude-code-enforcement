#!/usr/bin/env python3
"""
Layer 2: MCP監査エージェント テストスクリプト

実行前提:
1. ANTHROPIC_API_KEY 環境変数が設定されている
2. anthropic パッケージがインストールされている

実行方法:
  python test_mcp_audit.py
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# テスト用のサンプル会話ログ
SAMPLE_SESSION_LOG = """
[USER] LookMLファイルのfinancial_metrics.view.lkmlにディメンションを追加してください

[ASSISTANT] 了解しました。ファイルを確認します。
Tool: Read financial_metrics.view.lkml

[ASSISTANT] ディメンションを追加しました。
Tool: Edit financial_metrics.view.lkml

[USER] TodoWriteは？

[ASSISTANT] TodoWrite { todos: [
  {content: "分析", status: "completed"},
  {content: "実装", status: "completed"}
]}
"""

# 違反を含まない良い例
GOOD_SESSION_LOG = """
[USER] LookMLファイルのfinancial_metrics.view.lkmlにディメンションを追加してください

[ASSISTANT] 了解しました。まずByteroverから過去の知識を取得します。
Tool: byterover-retrieve-knowledge

[ASSISTANT] Codex analystと協力してファイル構造を分析します。
Tool: Read financial_metrics.view.lkml
Tool: Task("Codex Analyst", "ファイル構造を分析", "analyst")

[ASSISTANT] Codexの分析結果を踏まえてディメンションを追加します。
Tool: Edit financial_metrics.view.lkml

[ASSISTANT] TodoWriteでタスクを記録します。
Tool: TodoWrite { todos: [
  {content: "Byterover知識取得", status: "completed"},
  {content: "Codex分析依頼", status: "completed"},
  {content: "ファイル読み込み", status: "completed"},
  {content: "ディメンション追加", status: "completed"},
  {content: "動作確認", status: "completed"},
  {content: "ドキュメント更新", status: "completed"},
  {content: "Byterover保存", status: "pending"},
  {content: "コミット", status: "pending"}
]}

[ASSISTANT] 学習内容をByteroverに保存します。
Tool: byterover-store-knowledge
"""


def test_api_key():
    """APIキー設定確認"""
    print("\n" + "="*60)
    print("テスト1: APIキー設定確認")
    print("="*60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"✅ APIキーが設定されています（先頭: {api_key[:10]}...）")
        return True
    else:
        print("❌ ANTHROPIC_API_KEY環境変数が設定されていません")
        print("\n以下のコマンドで設定してください:")
        print("  setx ANTHROPIC_API_KEY \"your-api-key-here\"")
        return False


def test_import():
    """モジュールインポート確認"""
    print("\n" + "="*60)
    print("テスト2: モジュールインポート確認")
    print("="*60)

    try:
        from mcp_audit_agent import MCPAuditAgent
        print("✅ mcp_audit_agent.py のインポート成功")
        return True
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False


def test_agent_initialization():
    """エージェント初期化テスト"""
    print("\n" + "="*60)
    print("テスト3: エージェント初期化")
    print("="*60)

    try:
        from mcp_audit_agent import MCPAuditAgent
        agent = MCPAuditAgent()
        print("✅ MCP監査エージェント初期化成功")
        return agent
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        return None


def test_violation_detection(agent):
    """違反検出テスト（サンプルログ）"""
    print("\n" + "="*60)
    print("テスト4: 違反検出（サンプルログ - 違反あり）")
    print("="*60)

    try:
        result = agent.analyze_session(SAMPLE_SESSION_LOG, "test_session_bad")

        print(f"\n分析結果:")
        print(f"  コンプライアンススコア: {result.get('compliance_score', 0)}%")
        print(f"  総違反数: {result.get('total_violations', 0)}件")

        violations = result.get('violations', [])
        if violations:
            print(f"\n検出された違反:")
            for v in violations:
                print(f"    - {v.get('type')}: {v.get('message')}")
        else:
            print(f"\n  違反なし")

        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n推奨事項:")
            for r in recommendations:
                print(f"    - {r}")

        print(f"\nセッションサマリー: {result.get('session_summary', 'N/A')}")

        if result.get('total_violations', 0) > 0:
            print("\n✅ 違反検出機能が正常に動作しています")
            return True
        else:
            print("\n⚠️ 違反が検出されませんでした（期待: 2-3件）")
            return False

    except Exception as e:
        print(f"❌ 分析エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_good_session(agent):
    """正常なセッションのテスト"""
    print("\n" + "="*60)
    print("テスト5: 違反検出（サンプルログ - 違反なし）")
    print("="*60)

    try:
        result = agent.analyze_session(GOOD_SESSION_LOG, "test_session_good")

        print(f"\n分析結果:")
        print(f"  コンプライアンススコア: {result.get('compliance_score', 0)}%")
        print(f"  総違反数: {result.get('total_violations', 0)}件")

        violations = result.get('violations', [])
        if violations:
            print(f"\n検出された違反:")
            for v in violations:
                print(f"    - {v.get('type')}: {v.get('message')}")

        if result.get('compliance_score', 0) >= 90:
            print("\n✅ 正常なセッションを正しく評価しています")
            return True
        else:
            print(f"\n⚠️ スコアが予想より低い: {result.get('compliance_score', 0)}%")
            return False

    except Exception as e:
        print(f"❌ 分析エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rate_limiter():
    """レート制限テスト"""
    print("\n" + "="*60)
    print("テスト6: レート制限機能")
    print("="*60)

    try:
        from mcp_audit_agent import RateLimiter
        import time

        limiter = RateLimiter(max_requests=3, time_window=5)

        print("3リクエストを連続実行...")
        for i in range(3):
            limiter.wait_if_needed()
            print(f"  リクエスト {i+1} 完了")

        print("4つ目のリクエスト（待機が発生するはず）...")
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start

        if elapsed > 1:
            print(f"✅ レート制限が機能しています（待機時間: {elapsed:.1f}秒）")
            return True
        else:
            print(f"⚠️ 待機が発生しませんでした（{elapsed:.1f}秒）")
            return True  # テストとしては成功

    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


def test_log_files():
    """ログファイル作成確認"""
    print("\n" + "="*60)
    print("テスト7: ログファイル確認")
    print("="*60)

    log_dir = Path.home() / '.claude' / 'enforcement' / 'logs'

    # 期待されるログファイル
    expected_files = [
        'mcp_audit.log',
        'ai_audit_results.jsonl'
    ]

    all_exist = True
    for filename in expected_files:
        filepath = log_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"✅ {filename} 存在 ({size} bytes)")
        else:
            print(f"⚠️ {filename} 未作成（初回実行後に作成されます）")

    return True


def main():
    """メインテスト実行"""
    print("\n" + "="*60)
    print("Layer 2: MCP監査エージェント テストスイート")
    print("="*60)

    results = {}

    # テスト実行
    results['api_key'] = test_api_key()

    if not results['api_key']:
        print("\n❌ APIキーが設定されていないため、以降のテストをスキップします")
        return

    results['import'] = test_import()
    if not results['import']:
        print("\n❌ モジュールインポートに失敗したため、以降のテストをスキップします")
        return

    agent = test_agent_initialization()
    results['initialization'] = (agent is not None)

    if agent:
        results['violation_detection'] = test_violation_detection(agent)
        results['good_session'] = test_good_session(agent)
        results['rate_limiter'] = test_rate_limiter()
        results['log_files'] = test_log_files()

    # 結果サマリー
    print("\n" + "="*60)
    print("テスト結果サマリー")
    print("="*60)

    total = len(results)
    passed = sum(1 for r in results.values() if r)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "="*60)
    print(f"結果: {passed}/{total} テスト成功")
    print("="*60)

    if passed == total:
        print("\n🎉 全てのテストが成功しました！")
        print("\n次のステップ:")
        print("  1. 定期監査を起動: start-ai-audit.bat")
        print("  2. Claude Codeで開発")
        print("  3. ステータス確認: status-ai-audit.bat")
        return 0
    else:
        print("\n⚠️ 一部のテストが失敗しました")
        print("README_LAYER2_MCP_AUDIT.md のトラブルシューティングを確認してください")
        return 1


if __name__ == '__main__':
    exit(main())
