#!/usr/bin/env python3
"""
定期AI監査スケジューラー
5分ごとにMCP監査エージェントを実行してバッチ分析

Session Monitorとの統合:
- session_monitor.py: リアルタイム監視（正規表現ベース）
- scheduled_audit.py: 定期AI分析（複雑なパターン検出）

実行方法:
  python scheduled_audit.py start    # バックグラウンドで起動
  python scheduled_audit.py stop     # 停止
  python scheduled_audit.py status   # 状態確認

Author: 8-Layer Enforcement System
Version: 1.0.0
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import signal
import json

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
except ImportError:
    print("エラー: apschedulerがインストールされていません")
    print("以下のコマンドでインストールしてください:")
    print("  pip install apscheduler")
    sys.exit(1)

from mcp_audit_agent import MCPAuditAgent

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(
            Path.home() / '.claude' / 'enforcement' / 'logs' / 'scheduled_audit.log',
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ScheduledAuditService:
    """定期AI監査サービス"""

    def __init__(self, interval_minutes: int = 5):
        """
        初期化

        Args:
            interval_minutes: 監査間隔（分）
        """
        self.interval_minutes = interval_minutes
        self.scheduler = BackgroundScheduler()
        self.audit_agent = None
        self.pid_file = Path.home() / '.claude' / 'enforcement' / 'scheduled_audit.pid'
        self.status_file = Path.home() / '.claude' / 'enforcement' / 'scheduled_audit_status.json'

        # ディレクトリ作成
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)

    def start(self):
        """サービス起動"""
        # 既に起動中かチェック
        if self.is_running():
            logger.warning("サービスは既に起動中です")
            print("[WARNING] Scheduled Audit Service は既に起動中です")
            return

        logger.info(f"定期AI監査サービス起動中（間隔: {self.interval_minutes}分）...")

        try:
            # MCP監査エージェント初期化
            self.audit_agent = MCPAuditAgent()

            # スケジューラー設定
            self.scheduler.add_job(
                func=self._run_audit,
                trigger=IntervalTrigger(minutes=self.interval_minutes),
                id='periodic_ai_audit',
                name='AI監査バッチ実行',
                replace_existing=True
            )

            # シグナルハンドラ設定
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            # スケジューラー開始
            self.scheduler.start()

            # PIDファイル書き込み
            import os
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))

            # ステータス更新
            self._update_status('running')

            print(f"[OK] Scheduled Audit Service 起動成功")
            print(f"📊 監査間隔: {self.interval_minutes}分")
            print(f"📝 ログファイル: {Path.home() / '.claude' / 'enforcement' / 'logs' / 'scheduled_audit.log'}")
            print(f"🛑 停止方法: python {__file__} stop")

            logger.info("サービス起動完了")

            # 初回実行（即座に1回実行）
            logger.info("初回監査を実行します...")
            self._run_audit()

            # メインループ（Ctrl+C まで待機）
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Ctrl+C 検出 - サービス停止中...")
                self.stop()

        except Exception as e:
            logger.error(f"起動エラー: {e}", exc_info=True)
            self._update_status('error', str(e))
            raise

    def stop(self):
        """サービス停止"""
        logger.info("サービス停止中...")

        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

        # PIDファイル削除
        if self.pid_file.exists():
            self.pid_file.unlink()

        # ステータス更新
        self._update_status('stopped')

        print("[OK] Scheduled Audit Service 停止完了")
        logger.info("サービス停止完了")

    def status(self):
        """ステータス確認"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                status = json.load(f)

            print("\n" + "="*60)
            print("Scheduled Audit Service ステータス")
            print("="*60)
            print(f"状態: {status.get('state', 'unknown').upper()}")
            print(f"最終更新: {status.get('updated_at', 'N/A')}")

            if status.get('state') == 'running':
                print(f"PID: {self._get_pid()}")
                print(f"監査間隔: {self.interval_minutes}分")

            if status.get('last_audit'):
                print(f"最終監査: {status['last_audit'].get('timestamp', 'N/A')}")
                print(f"分析セッション数: {status['last_audit'].get('sessions_analyzed', 0)}")
                print(f"平均スコア: {status['last_audit'].get('average_score', 'N/A')}%")

            if status.get('error'):
                print(f"エラー: {status['error']}")

            print("="*60)
        else:
            print("[WARNING] ステータス情報が見つかりません")

    def is_running(self) -> bool:
        """サービスが実行中か確認"""
        if not self.pid_file.exists():
            return False

        try:
            import psutil
            pid = self._get_pid()
            if pid and psutil.pid_exists(pid):
                # プロセス名も確認（より確実に）
                proc = psutil.Process(pid)
                if 'python' in proc.name().lower():
                    return True
        except ImportError:
            # psutilがない場合はPIDファイルの存在のみで判定
            return self.pid_file.exists()
        except Exception:
            pass

        return False

    def _run_audit(self):
        """AI監査実行"""
        logger.info("="*60)
        logger.info("定期AI監査開始")
        logger.info("="*60)

        try:
            # バッチ分析実行（過去1時間のセッション）
            results = self.audit_agent.batch_analyze_recent_sessions(
                lookback_hours=1,  # 頻繁に実行するため短めに
                max_sessions=5     # 最大5セッション
            )

            if not results:
                logger.info("分析対象のセッションがありません")
                return

            # サマリーレポート生成
            summary = self.audit_agent.generate_summary_report(results)

            # ステータス更新
            self._update_status('running', last_audit={
                'timestamp': datetime.now().isoformat(),
                'sessions_analyzed': len(results),
                'average_score': summary.get('average_score', 0),
                'total_violations': summary.get('total_violations', 0),
                'violation_breakdown': summary.get('violation_breakdown', {})
            })

            # 重大な違反がある場合は警告
            if summary.get('average_score', 100) < 70:
                logger.warning(
                    f"[WARNING] コンプライアンススコアが低下: {summary['average_score']}%"
                )
                logger.warning(f"総違反数: {summary['total_violations']}件")

            logger.info("定期AI監査完了")

        except Exception as e:
            logger.error(f"監査実行エラー: {e}", exc_info=True)
            self._update_status('running', error=str(e))

    def _update_status(self, state: str, error: str = None, last_audit: dict = None):
        """ステータスファイル更新"""
        status = {
            'state': state,
            'updated_at': datetime.now().isoformat()
        }

        if error:
            status['error'] = error

        if last_audit:
            status['last_audit'] = last_audit

        with open(self.status_file, 'w') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)

    def _get_pid(self) -> int:
        """PIDファイルからPID読み込み"""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    return int(f.read().strip())
            except Exception:
                pass
        return None

    def _signal_handler(self, signum, frame):
        """シグナルハンドラ（Ctrl+C等）"""
        logger.info(f"シグナル受信: {signum}")
        self.stop()
        sys.exit(0)


def main():
    """メイン実行関数"""
    import argparse

    parser = argparse.ArgumentParser(description='定期AI監査スケジューラー')
    parser.add_argument(
        'action',
        choices=['start', 'stop', 'status', 'restart'],
        help='実行アクション'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='監査間隔（分）デフォルト: 5'
    )

    args = parser.parse_args()

    service = ScheduledAuditService(interval_minutes=args.interval)

    if args.action == 'start':
        service.start()

    elif args.action == 'stop':
        if not service.is_running():
            print("[WARNING] サービスは起動していません")
        else:
            service.stop()

    elif args.action == 'status':
        service.status()

    elif args.action == 'restart':
        if service.is_running():
            print("サービスを停止中...")
            service.stop()
            time.sleep(1)
        print("サービスを起動中...")
        service.start()


if __name__ == '__main__':
    main()
