#!/usr/bin/env python3
"""
Layer 2: MCP監査エージェント（AI分析）
Claude APIを使用して会話ログをAI分析し、複雑な違反パターンを検出

実装内容:
- Anthropic Claude API統合
- バッチ分析ロジック（5分ごと）
- 9種類の違反パターンのAI検出
- session_monitor.pyとの統合
- レート制限考慮（1分間に3リクエスト以下）

Author: 8-Layer Enforcement System
Version: 1.0.0
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import anthropic

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(
            Path.home() / '.claude' / 'enforcement' / 'logs' / 'mcp_audit.log',
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """レート制限管理（1分間に3リクエスト以下）"""

    def __init__(self, max_requests: int = 3, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window  # 秒
        self.request_times = deque(maxlen=max_requests)

    def wait_if_needed(self):
        """必要に応じて待機"""
        now = time.time()

        if len(self.request_times) >= self.max_requests:
            oldest_request = self.request_times[0]
            time_since_oldest = now - oldest_request

            if time_since_oldest < self.time_window:
                wait_time = self.time_window - time_since_oldest
                logger.info(f"レート制限: {wait_time:.1f}秒待機中...")
                time.sleep(wait_time)

        self.request_times.append(time.time())


class MCPAuditAgent:
    """MCP監査エージェント - AIによる会話ログ分析"""

    # AI分析プロンプトテンプレート
    ANALYSIS_PROMPT = """
以下のClaude Code会話ログを分析し、CLAUDE.mdのルール違反を検出してください。

## 検出対象の9種類の違反パターン:

1. **no_codex_collaboration** (-20点)
   - LookMLやコードファイルの編集時にCodex analystエージェントと協力していない
   - 単独で分析・修正を完結させている
   - 特にExcel/CSV分析、マッピング作成、辞書作成で必須

2. **insufficient_todowrite** (-10点)
   - TodoWrite項目数が8個未満
   - タスク分解が不十分

3. **missing_byterover_retrieve** (-15点)
   - タスク開始前にbyterover-retrieve-knowledgeを実行していない
   - 過去の知識を活用していない

4. **missing_byterover_store** (-15点)
   - タスク完了後にbyterover-store-knowledgeを実行していない
   - 学習内容を保存していない

5. **sequential_execution** (-20点)
   - 並列実行可能なTask()を逐次実行している
   - 複数メッセージに分けて実行（1メッセージで複数Task()が正しい）

6. **missing_seraphina** (-20点)
   - 複雑度スコア50以上のタスクでSeraphina相談をしていない
   - 判断が必要な複雑なタスクを単独で実施

7. **root_file_creation** (-25点)
   - ルートディレクトリに.mdファイルや新規ファイルを作成
   - ドキュメントを勝手に作成

8. **no_gemini_validation** (-10点)
   - ビジネスロジックや要件判断でGeminiを使用していない
   - 推測で実装を進めている

9. **sample_data_confusion** (-50点)
   - サンプルデータと実データの区別を明示していない
   - データの出所を曖昧にしている

## 会話ログ:
{session_log}

## 回答形式:
以下のJSON形式で、検出された違反を全て列挙してください。
違反が見つからない場合は、violationsを空配列にしてください。

```json
{{
    "violations": [
        {{
            "type": "no_codex_collaboration",
            "severity": "high",
            "message": "financial_metrics.view.lkmlをCodex協力なしで編集",
            "line_number": 42,
            "context": "Edit file without Task(Codex)"
        }}
    ],
    "compliance_score": 85,
    "total_violations": 1,
    "recommendations": [
        "次回はCodex analystと協力してファイル構造を分析してから編集してください"
    ],
    "session_summary": "LookML修正タスク。Codex協力が不足。"
}}
```

重要: 回答は必ずJSONのみを返してください。説明文は含めないでください。
"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Anthropic APIキー（省略時は環境変数から取得）
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY環境変数が設定されていません。\n"
                "以下のコマンドで設定してください:\n"
                "  set ANTHROPIC_API_KEY=your-api-key-here"
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.rate_limiter = RateLimiter(max_requests=3, time_window=60)

        # ログディレクトリ
        self.log_dir = Path.home() / '.claude' / 'enforcement' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 監査結果保存先
        self.audit_results_file = self.log_dir / 'ai_audit_results.jsonl'

        logger.info("MCP監査エージェント初期化完了")

    def analyze_session(self, session_log: str, session_id: str) -> Dict:
        """
        会話ログをAI分析

        Args:
            session_log: 会話ログ（テキスト形式）
            session_id: セッションID

        Returns:
            分析結果の辞書
        """
        logger.info(f"セッション分析開始: {session_id}")

        # レート制限チェック
        self.rate_limiter.wait_if_needed()

        try:
            # Claude APIで分析
            prompt = self.ANALYSIS_PROMPT.format(session_log=session_log)

            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                temperature=0,  # 決定論的な分析のため0
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # レスポンスからJSON抽出
            response_text = response.content[0].text

            # JSONブロックから抽出（```json ... ``` の場合）
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()

            # JSON解析
            result = json.loads(json_text)

            # メタデータ追加
            result['session_id'] = session_id
            result['analyzed_at'] = datetime.now().isoformat()
            result['model'] = "claude-sonnet-4-5-20250929"

            logger.info(
                f"分析完了: {result.get('total_violations', 0)}件の違反検出 "
                f"(スコア: {result.get('compliance_score', 0)}%)"
            )

            # 結果を保存
            self._save_audit_result(result)

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {e}")
            logger.error(f"レスポンス: {response_text[:500]}...")
            raise

        except anthropic.APIError as e:
            logger.error(f"Claude API エラー: {e}")
            raise

        except Exception as e:
            logger.error(f"予期しないエラー: {e}", exc_info=True)
            raise

    def analyze_session_file(self, session_file: Path) -> Dict:
        """
        セッションファイル（.jsonl）を分析

        Args:
            session_file: セッションログファイルのパス

        Returns:
            分析結果の辞書
        """
        logger.info(f"ファイル分析開始: {session_file.name}")

        # セッションログを読み込み
        session_log = self._load_session_log(session_file)

        if not session_log.strip():
            logger.warning("セッションログが空です")
            return {
                'violations': [],
                'compliance_score': 100,
                'total_violations': 0,
                'recommendations': [],
                'session_summary': 'ログなし'
            }

        # ログが長すぎる場合は最新5000文字のみ分析
        if len(session_log) > 5000:
            logger.info(f"ログが長いため最新5000文字のみ分析（元: {len(session_log)}文字）")
            session_log = "..." + session_log[-5000:]

        session_id = session_file.stem  # ファイル名からセッションID抽出

        return self.analyze_session(session_log, session_id)

    def _load_session_log(self, session_file: Path) -> str:
        """
        セッションログファイルを読み込んでテキスト化

        Args:
            session_file: .jsonlファイルのパス

        Returns:
            テキスト形式の会話ログ
        """
        lines = []

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        role = entry.get('role', 'unknown')
                        content = entry.get('content', '')

                        # ツール呼び出しの場合
                        if 'tool_calls' in entry:
                            for tool_call in entry['tool_calls']:
                                tool_name = tool_call.get('name', 'unknown')
                                lines.append(f"[{role.upper()}] Tool: {tool_name}")

                        # 通常のメッセージ
                        elif content:
                            lines.append(f"[{role.upper()}] {content[:500]}")  # 長すぎる場合は切り詰め

                    except json.JSONDecodeError:
                        continue

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"ログファイル読み込みエラー: {e}")
            return ""

    def _save_audit_result(self, result: Dict):
        """
        監査結果をJSONL形式で保存

        Args:
            result: 分析結果の辞書
        """
        try:
            with open(self.audit_results_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

            logger.info(f"監査結果を保存: {self.audit_results_file}")

        except Exception as e:
            logger.error(f"監査結果保存エラー: {e}")

    def batch_analyze_recent_sessions(
        self,
        lookback_hours: int = 24,
        max_sessions: int = 10
    ) -> List[Dict]:
        """
        最近のセッションをバッチ分析

        Args:
            lookback_hours: 過去何時間のセッションを対象にするか
            max_sessions: 最大分析セッション数

        Returns:
            分析結果のリスト
        """
        logger.info(
            f"バッチ分析開始: 過去{lookback_hours}時間, 最大{max_sessions}セッション"
        )

        # セッションログディレクトリ
        snapshot_dir = Path.home() / '.claude' / 'shell-snapshots'

        if not snapshot_dir.exists():
            logger.warning(f"セッションログディレクトリが存在しません: {snapshot_dir}")
            return []

        # 最近のセッションファイルを取得
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        session_files = []

        for file in snapshot_dir.glob('session_*.jsonl'):
            if file.stat().st_mtime > cutoff_time.timestamp():
                session_files.append(file)

        # 最新順にソート
        session_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        session_files = session_files[:max_sessions]

        logger.info(f"{len(session_files)}個のセッションを分析します")

        # 各セッションを分析
        results = []
        for session_file in session_files:
            try:
                result = self.analyze_session_file(session_file)
                results.append(result)

                # レート制限のため次のセッション前に少し待機
                if len(session_files) > 1:
                    time.sleep(2)

            except Exception as e:
                logger.error(f"セッション分析失敗 {session_file.name}: {e}")
                continue

        logger.info(f"バッチ分析完了: {len(results)}/{len(session_files)}セッション成功")

        return results

    def generate_summary_report(self, results: List[Dict]) -> Dict:
        """
        分析結果のサマリーレポート生成

        Args:
            results: 分析結果のリスト

        Returns:
            サマリーレポート
        """
        if not results:
            return {
                'total_sessions': 0,
                'average_score': 0,
                'total_violations': 0,
                'violation_breakdown': {},
                'common_recommendations': []
            }

        total_violations = sum(r.get('total_violations', 0) for r in results)
        average_score = sum(r.get('compliance_score', 0) for r in results) / len(results)

        # 違反タイプ別の集計
        violation_breakdown = {}
        all_recommendations = []

        for result in results:
            for violation in result.get('violations', []):
                vtype = violation.get('type', 'unknown')
                violation_breakdown[vtype] = violation_breakdown.get(vtype, 0) + 1

            all_recommendations.extend(result.get('recommendations', []))

        # 頻出する推奨事項
        from collections import Counter
        common_recommendations = [
            item for item, count in Counter(all_recommendations).most_common(5)
        ]

        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_sessions': len(results),
            'average_score': round(average_score, 1),
            'total_violations': total_violations,
            'violation_breakdown': violation_breakdown,
            'common_recommendations': common_recommendations
        }

        logger.info(
            f"サマリー: {len(results)}セッション, "
            f"平均スコア {average_score:.1f}%, "
            f"総違反数 {total_violations}件"
        )

        return summary


def main():
    """メイン実行関数（テスト用）"""
    import argparse

    parser = argparse.ArgumentParser(description='MCP監査エージェント')
    parser.add_argument(
        '--batch',
        action='store_true',
        help='バッチ分析モード（過去24時間のセッション）'
    )
    parser.add_argument(
        '--session-file',
        type=Path,
        help='特定のセッションファイルを分析'
    )
    parser.add_argument(
        '--lookback-hours',
        type=int,
        default=24,
        help='バッチ分析の対象時間（デフォルト: 24時間）'
    )

    args = parser.parse_args()

    try:
        agent = MCPAuditAgent()

        if args.session_file:
            # 単一セッション分析
            result = agent.analyze_session_file(args.session_file)
            print("\n" + "="*60)
            print("分析結果:")
            print("="*60)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.batch:
            # バッチ分析
            results = agent.batch_analyze_recent_sessions(
                lookback_hours=args.lookback_hours
            )

            # サマリーレポート生成
            summary = agent.generate_summary_report(results)

            print("\n" + "="*60)
            print("バッチ分析サマリー:")
            print("="*60)
            print(json.dumps(summary, ensure_ascii=False, indent=2))

        else:
            print("使用方法:")
            print("  単一セッション分析: --session-file <path>")
            print("  バッチ分析: --batch [--lookback-hours N]")

    except Exception as e:
        logger.error(f"実行エラー: {e}", exc_info=True)
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
