"""
通知管理システム

8-Layer Enforcement System - Windows Toast Notification Manager
違反検出時にリアルタイムで通知を送信する
"""

import yaml
from typing import Literal
from pathlib import Path

Severity = Literal["INFO", "WARNING", "ERROR"]

class NotificationManager:
    """Windows通知管理"""

    def __init__(self, config_path: str = "config.yaml"):
        # 設定ファイル読み込み
        config_file = Path(config_path)
        if not config_file.exists():
            # デフォルト設定を使用
            self.config = self._get_default_config()
        else:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

        # Toast Notifier初期化（遅延インポート）
        self.toaster = None
        try:
            from win10toast import ToastNotifier
            self.toaster = ToastNotifier()
        except ImportError:
            print("[WARNING] Warning: win10toast not installed. Notifications will be console-only.")
            print("   Install with: pip install win10toast")

        # 設定取得
        notification_config = self.config.get('notification', {})
        self.enabled = notification_config.get('enabled', True)
        self.method = notification_config.get('method', 'windows')
        self.levels = notification_config.get('levels', {
            'INFO': True,
            'WARNING': True,
            'ERROR': True
        })
        self.duration = notification_config.get('duration', 5)
        self.sound = notification_config.get('sound', True)

    def _get_default_config(self) -> dict:
        """デフォルト設定を返す"""
        return {
            'notification': {
                'enabled': True,
                'method': 'windows',
                'levels': {
                    'INFO': True,
                    'WARNING': True,
                    'ERROR': True
                },
                'sound': True,
                'duration': 5
            }
        }

    def send(self, title: str, message: str,
             severity: Severity = "INFO", score: int = None):
        """
        通知送信

        Args:
            title: 通知タイトル
            message: 通知メッセージ
            severity: 重要度（INFO/WARNING/ERROR）
            score: 現在のコンプライアンススコア（任意）
        """
        if not self.enabled:
            return

        # レベル確認（このレベルの通知が無効になっていればスキップ）
        if not self.levels.get(severity, True):
            return

        # 重要度に応じたアイコン選択
        icon_map = {
            "INFO": "[INFO]",
            "WARNING": "[WARNING]",
            "ERROR": "[ERROR]"
        }
        icon = icon_map.get(severity, "[INFO]")

        # メッセージ整形
        full_message = f"{icon} {message}"
        if score is not None:
            full_message += f"\n\n[STATS] Current Score: {score}%"

        # 通知方法に応じて送信
        if self.method == "windows":
            self._send_windows_notification(title, full_message, severity)
        elif self.method == "vscode":
            self._send_vscode_notification(title, full_message, severity)
        else:
            # デフォルトはコンソール出力
            print(f"[{severity}] {title}: {full_message}")

    def _send_windows_notification(self, title: str, message: str, severity: Severity):
        """
        Windows Toast通知

        Args:
            title: 通知タイトル
            message: 通知メッセージ
            severity: 重要度（色分けに使用）
        """
        try:
            # タイトルに重要度を含める
            severity_prefix_map = {
                "INFO": "[INFO]",
                "WARNING": "[WARNING]",
                "ERROR": "[ERROR]"
            }
            prefix = severity_prefix_map.get(severity, "")
            full_title = f"8-Layer System {prefix}: {title}"

            # Toast通知送信
            if self.toaster:
                self.toaster.show_toast(
                    title=full_title,
                    msg=message,
                    duration=self.duration,
                    threaded=True,  # 非同期で実行（メインスレッドをブロックしない）
                    icon_path=None  # デフォルトアイコン使用
                )
                # デバッグ出力
                print(f"[OK] Notification sent: [{severity}] {title}")
            else:
                # win10toastが利用できない場合はコンソール出力
                print(f"\n{'='*60}")
                print(f"[{severity}] {full_title}")
                print(f"{'-'*60}")
                print(message)
                print(f"{'='*60}\n")

        except Exception as e:
            # 通知失敗時はコンソールにフォールバック
            print(f"[ERROR] Notification error: {e}")
            print(f"   [{severity}] {title}: {message}")

    def _send_vscode_notification(self, title: str, message: str, severity: Severity):
        """
        VS Code通知（拡張機能経由）

        Note: VS Code拡張機能実装後に完全実装予定
        現在はコンソール出力のみ

        Args:
            title: 通知タイトル
            message: 通知メッセージ
            severity: 重要度
        """
        # TODO: VS Code拡張機能実装後に追加
        # 現在はコンソール出力のみ
        severity_colors = {
            "INFO": "\033[94m",     # 青
            "WARNING": "\033[93m",  # 黄色
            "ERROR": "\033[91m"     # 赤
        }
        reset_color = "\033[0m"

        color = severity_colors.get(severity, "")
        print(f"{color}[VS Code] {severity}: {title} - {message}{reset_color}")

    def test_notification(self, severity: Severity = "INFO"):
        """
        テスト通知送信

        Args:
            severity: テストする重要度
        """
        self.send(
            title=f"Test Notification ({severity})",
            message=f"This is a test message with severity: {severity}",
            severity=severity,
            score=85
        )


if __name__ == "__main__":
    # テスト実行
    print("[INFO] Testing NotificationManager...")

    # 設定ファイルパスを指定（存在しない場合はデフォルト設定を使用）
    config_path = Path(__file__).parent / "config.yaml"

    # NotificationManager初期化
    notifier = NotificationManager(str(config_path) if config_path.exists() else "config.yaml")

    # 各重要度レベルのテスト通知
    print("\n1. Testing INFO notification...")
    notifier.send(
        title="Information",
        message="This is an informational message",
        severity="INFO",
        score=95
    )

    import time
    time.sleep(2)

    print("\n2. Testing WARNING notification...")
    notifier.send(
        title="Warning Detected",
        message="TodoWrite項目数が8未満です（現在: 5個）",
        severity="WARNING",
        score=80
    )

    time.sleep(2)

    print("\n3. Testing ERROR notification...")
    notifier.send(
        title="Critical Violation",
        message="Codex協力なしでファイル編集を検出しました",
        severity="ERROR",
        score=65
    )

    print("\n[OK] Test notifications sent. Check your Windows notifications.")
    print("   Waiting 6 seconds for notifications to display...")
    time.sleep(6)

    print("\n[OK] NotificationManager test completed!")
