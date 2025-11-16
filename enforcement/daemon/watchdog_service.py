"""
Watchdogサービス（実際の監視プロセス）

バックグラウンドで常時稼働し、Session監視を実行する。
プロセスのクラッシュを検出して自動再起動を行う。
"""

import sys
import time
import signal
import logging
import psutil
from pathlib import Path
from typing import Optional

# 親ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# ログ設定
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            log_dir / "service.log",
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# グローバル変数（シグナルハンドラ用）
observer = None
running = True


def signal_handler(signum, frame):
    """終了シグナルハンドラ

    SIGTERM/SIGINTを受信時にクリーンシャットダウンを実行
    """
    global running, observer

    logger.info(f"Received signal {signum} - shutting down gracefully...")
    running = False

    if observer:
        observer.stop()


def get_memory_usage() -> float:
    """現在のメモリ使用量を取得（MB）"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def get_cpu_usage() -> float:
    """現在のCPU使用率を取得（%）"""
    process = psutil.Process()
    return process.cpu_percent(interval=0.5)


def get_current_score() -> Optional[int]:
    """現在のコンプライアンススコアを取得"""
    score_log = Path(__file__).parent.parent / "logs" / "compliance_scores.jsonl"

    if not score_log.exists():
        return None

    try:
        import json
        with open(score_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                last_entry = json.loads(lines[-1])
                return last_entry.get('score')
    except Exception as e:
        logger.warning(f"Failed to get current score: {e}")
        return None


def main():
    """メインループ

    Session監視を起動し、定期的なステータスレポートを実行
    """
    global observer, running

    # シグナルハンドラ登録
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("=" * 60)
    logger.info("8-Layer Enforcement System - Watchdog Service")
    logger.info("=" * 60)
    logger.info(f"Python: {sys.version}")
    logger.info(f"Working Directory: {Path.cwd()}")

    try:
        # Session監視開始
        from watchdog.observers import Observer

        # session_monitorのインポート
        try:
            from session_monitor import SessionMonitor
        except ImportError:
            logger.error("Failed to import SessionMonitor - module not found")
            logger.info("Make sure session_monitor.py is in the parent directory")
            sys.exit(1)

        # 設定ファイル読み込み
        import yaml

        config_path = Path(__file__).parent.parent / "config.yaml"

        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            logger.info("Creating default config...")

            # デフォルト設定作成
            default_config = {
                'monitoring': {
                    'log_directory': str(Path.home() / '.claude' / 'logs'),
                    'check_interval': 5,
                    'notification_threshold': 60
                },
                'enforcement': {
                    'block_threshold': 70,
                    'enable_git_hook': True
                }
            }

            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, allow_unicode=True)

            logger.info(f"Created default config at: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        log_directory = config['monitoring']['log_directory']

        # ログディレクトリ確認・作成
        Path(log_directory).mkdir(parents=True, exist_ok=True)

        # SessionMonitor初期化
        event_handler = SessionMonitor(str(config_path))

        # Watchdog Observer起動
        observer = Observer()
        observer.schedule(event_handler, log_directory, recursive=False)
        observer.start()

        logger.info(f"[OK] Monitoring started: {log_directory}")

        initial_score = get_current_score()
        if initial_score is not None:
            logger.info(f"[STATS] Initial Score: {initial_score}%")
        else:
            logger.info("[STATS] Initial Score: Not available yet")

        # メインループ
        last_status_time = time.time()
        status_interval = 60  # 1分ごとにステータス表示

        while running:
            time.sleep(1)

            # 定期的なステータスレポート
            current_time = time.time()
            if current_time - last_status_time >= status_interval:
                cpu = get_cpu_usage()
                mem = get_memory_usage()
                score = get_current_score()

                if score is not None:
                    logger.info(
                        f"[STATS] Status - Score: {score}% | "
                        f"CPU: {cpu:.1f}% | Memory: {mem:.1f} MB"
                    )
                else:
                    logger.info(
                        f"[STATS] Status - CPU: {cpu:.1f}% | Memory: {mem:.1f} MB"
                    )

                last_status_time = current_time

        # クリーンアップ
        logger.info("Stopping observer...")
        observer.stop()
        observer.join()

        logger.info("[OK] Service stopped gracefully")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt - stopping...")
        if observer:
            observer.stop()
            observer.join()
        sys.exit(0)

    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}", exc_info=True)

        if observer:
            try:
                observer.stop()
                observer.join()
            except Exception:
                pass

        sys.exit(1)


if __name__ == "__main__":
    main()
