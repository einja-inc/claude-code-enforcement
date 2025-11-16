"""
バックグラウンドサービス管理

8-Layer Enforcement System - Service Manager
PIDファイル管理、バックグラウンドプロセス制御、Windows環境対応
"""

import os
import sys
import time
import psutil
import signal
import subprocess
from pathlib import Path
from typing import Optional


class ServiceManager:
    """サービス制御マネージャー"""

    def __init__(self):
        self.pid_file = Path(__file__).parent / "service.pid"
        self.log_file = Path(__file__).parent.parent / "logs" / "service.log"

        # ログディレクトリ作成
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def start(self, background: bool = True):
        """サービス起動"""
        # 既に起動中か確認
        if self.is_running():
            print("[WARNING]  Service is already running")
            return False

        if background:
            # バックグラウンドで起動
            self._start_background()
        else:
            # フォアグラウンドで起動（デバッグ用）
            self._start_foreground()

        return True

    def _start_background(self):
        """バックグラウンド起動"""
        # watchdog_service.py をサブプロセスで起動
        watchdog_script = Path(__file__).parent / "watchdog_service.py"

        # Windowsでは CREATE_NO_WINDOW フラグを使用
        if sys.platform == "win32":
            CREATE_NO_WINDOW = 0x08000000

            process = subprocess.Popen(
                [sys.executable, str(watchdog_script)],
                stdout=open(self.log_file, 'a', encoding='utf-8'),
                stderr=subprocess.STDOUT,
                creationflags=CREATE_NO_WINDOW,
                cwd=Path(__file__).parent.parent
            )
        else:
            # Linux/Mac
            process = subprocess.Popen(
                [sys.executable, str(watchdog_script)],
                stdout=open(self.log_file, 'a', encoding='utf-8'),
                stderr=subprocess.STDOUT,
                start_new_session=True,
                cwd=Path(__file__).parent.parent
            )

        # PIDファイル保存
        with open(self.pid_file, 'w', encoding='utf-8') as f:
            f.write(str(process.pid))

        print(f"[OK] Service started (PID: {process.pid})")
        print(f"[INFO] Log file: {self.log_file}")

    def _start_foreground(self):
        """フォアグラウンド起動（デバッグ用）"""
        watchdog_script = Path(__file__).parent / "watchdog_service.py"

        # 直接実行
        subprocess.run([sys.executable, str(watchdog_script)])

    def stop(self):
        """サービス停止"""
        pid = self._get_pid()

        if pid is None:
            print("[WARNING]  Service is not running")
            return False

        try:
            process = psutil.Process(pid)

            # 終了シグナル送信
            if sys.platform == "win32":
                process.terminate()
            else:
                process.send_signal(signal.SIGTERM)

            # 終了待機（最大10秒）
            process.wait(timeout=10)

            # PIDファイル削除
            self.pid_file.unlink()

            print(f"[OK] Service stopped (PID: {pid})")
            return True

        except psutil.NoSuchProcess:
            print("[WARNING]  Process not found (cleaning up)")
            self.pid_file.unlink(missing_ok=True)
            return False
        except psutil.TimeoutExpired:
            print("[WARNING]  Timeout - forcing kill")
            process.kill()
            self.pid_file.unlink()
            return True

    def restart(self):
        """サービス再起動"""
        print("[INFO] Restarting service...")
        self.stop()
        time.sleep(2)
        self.start()

    def status(self):
        """サービス状態確認"""
        pid = self._get_pid()

        if pid is None:
            print("[INFO]  Service Status: STOPPED")
            return

        try:
            process = psutil.Process(pid)

            # プロセス情報取得
            cpu = process.cpu_percent(interval=1)
            mem = process.memory_info().rss / 1024 / 1024  # MB

            print(f"[OK] Service Status: RUNNING")
            print(f"[INFO] PID: {pid}")
            print(f"[INFO]  CPU: {cpu:.1f}%")
            print(f"[INFO] Memory: {mem:.1f} MB")
            print(f"[INFO]  Running Time: {self._format_uptime(process.create_time())}")

            # コンプライアンススコア取得
            score = self._get_current_score()
            if score is not None:
                print(f"[STATS] Compliance Score: {score}%")

        except psutil.NoSuchProcess:
            print("[WARNING]  Process not found (stale PID file)")
            self.pid_file.unlink()

    def is_running(self) -> bool:
        """起動中か確認"""
        pid = self._get_pid()

        if pid is None:
            return False

        return psutil.pid_exists(pid)

    def _get_pid(self) -> Optional[int]:
        """PIDファイルからPID取得"""
        if not self.pid_file.exists():
            return None

        try:
            with open(self.pid_file, 'r', encoding='utf-8') as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            return None

    def _format_uptime(self, start_time: float) -> str:
        """稼働時間フォーマット"""
        uptime = time.time() - start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        return f"{hours}h {minutes}m"

    def _get_current_score(self) -> Optional[int]:
        """現在のコンプライアンススコア取得"""
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
        except Exception:
            return None


def main():
    """CLI エントリーポイント"""
    import argparse

    parser = argparse.ArgumentParser(description="8-Layer Enforcement Service Manager")
    parser.add_argument('command', choices=['start', 'stop', 'restart', 'status'],
                       help="Service command")
    parser.add_argument('--foreground', action='store_true',
                       help="Run in foreground (for debugging)")

    args = parser.parse_args()

    manager = ServiceManager()

    if args.command == 'start':
        manager.start(background=not args.foreground)
    elif args.command == 'stop':
        manager.stop()
    elif args.command == 'restart':
        manager.restart()
    elif args.command == 'status':
        manager.status()


if __name__ == "__main__":
    main()
