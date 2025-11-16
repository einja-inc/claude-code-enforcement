"""
Session監視システム（Layer 5）

8-Layer Enforcement System - Real-time Session Monitor
Claude Codeの会話ログをリアルタイムで監視し、違反を検出する
"""

import time
import json
import yaml
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import deque
from typing import Dict, Optional
from datetime import datetime

from violation_detector import ViolationDetector
from notification_manager import NotificationManager
from compliance_scorer import ComplianceScorer


class SessionMonitor(FileSystemEventHandler):
    """Claude Code会話ログ監視"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Session監視システムの初期化

        Args:
            config_path: 設定ファイルのパス
        """
        # 設定ファイル読み込み
        config_file = Path(config_path)
        if not config_file.is_absolute():
            # 相対パスの場合、このスクリプトと同じディレクトリを基準にする
            config_file = Path(__file__).parent / config_path

        if not config_file.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # サブシステム初期化
        self.detector = ViolationDetector(str(config_file))
        self.notifier = NotificationManager(str(config_file))
        self.scorer = ComplianceScorer(str(config_file))

        # ファイルごとの読み込み位置記録（増分読み込み用）
        self.file_positions: Dict[str, int] = {}

        # 違反履歴（最新100件をメモリに保持）
        self.violation_history = deque(maxlen=100)

        # 監視対象ディレクトリ
        self.log_directory = Path(self.config['monitoring']['log_directory'])

        # 統計情報
        self.stats = {
            'files_monitored': 0,
            'lines_analyzed': 0,
            'violations_detected': 0,
            'start_time': time.time()
        }

        print(f"[OK] Session Monitor initialized")
        print(f"[INFO] Watching: {self.log_directory}")
        print(f"[INFO] Initial Compliance Score: {self.scorer.get_current_score()}%")

    def on_modified(self, event):
        """
        ファイル変更時のイベントハンドラ

        Args:
            event: watchdogのFileSystemEvent
        """
        if event.is_directory:
            return

        filepath = event.src_path

        # JSONLファイルのみ監視
        if not filepath.endswith('.jsonl'):
            return

        # session_*.jsonl パターンに一致するか確認
        filename = Path(filepath).name
        if not filename.startswith('session_'):
            return

        # デバッグモード
        if self.config.get('debug', {}).get('verbose', False):
            print(f"[INFO] File modified: {filename}")

        # 新規追加行を分析
        self.analyze_new_lines(filepath)

    def on_created(self, event):
        """
        ファイル作成時のイベントハンドラ

        Args:
            event: watchdogのFileSystemEvent
        """
        if event.is_directory:
            return

        filepath = event.src_path

        # session_*.jsonl パターンに一致するか確認
        filename = Path(filepath).name
        if filename.startswith('session_') and filepath.endswith('.jsonl'):
            self.stats['files_monitored'] += 1
            print(f"[START] New session started: {filename}")

            # 新しいファイルの位置を0で初期化
            self.file_positions[filepath] = 0

    def analyze_new_lines(self, filepath: str):
        """
        新規追加行のみを分析（増分読み込み）

        Args:
            filepath: 監視対象ファイルのパス
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # 前回の読み込み位置
                last_pos = self.file_positions.get(filepath, 0)
                f.seek(last_pos)

                # 新規行を読み込み
                new_lines = f.readlines()

                # 現在位置を保存
                self.file_positions[filepath] = f.tell()

            # 各行を解析
            for i, line in enumerate(new_lines):
                line = line.strip()
                if not line:
                    continue

                try:
                    log_entry = json.loads(line)
                    self.process_log_entry(log_entry, last_pos + i + 1, filepath)
                    self.stats['lines_analyzed'] += 1
                except json.JSONDecodeError as e:
                    if self.config.get('debug', {}).get('verbose', False):
                        print(f"[WARNING] JSON parse error at line {i+1}: {e}")

        except FileNotFoundError:
            # ファイルが削除された場合（セッション終了など）
            if filepath in self.file_positions:
                del self.file_positions[filepath]
                print(f"[DIR] Session file removed: {Path(filepath).name}")
        except Exception as e:
            print(f"[ERROR] Error analyzing {filepath}: {e}")

    def process_log_entry(self, log_entry: dict, line_number: int, filepath: str):
        """
        ログエントリを処理

        Args:
            log_entry: JSONLから読み込んだログエントリ
            line_number: 行番号
            filepath: ファイルパス
        """
        content = log_entry.get('content', '')
        role = log_entry.get('role', 'unknown')

        # Assistantのメッセージのみ検査
        # （ユーザーメッセージは違反対象外）
        if role != 'assistant':
            return

        # 空のメッセージをスキップ
        if not content or len(content.strip()) == 0:
            return

        # 違反検出
        violations = self.detector.detect(content, line_number)

        if violations:
            self.handle_violations(violations, log_entry, filepath)

    def handle_violations(self, violations: list, context: dict, filepath: str):
        """
        違反処理

        Args:
            violations: 検出された違反のリスト
            context: ログエントリの完全なコンテキスト
            filepath: 違反が検出されたファイルパス
        """
        for violation in violations:
            # スコア更新
            new_score = self.scorer.add_violation(violation)

            # 通知送信
            self.notifier.send(
                title=f"Compliance Violation: {violation.type}",
                message=violation.message,
                severity=violation.severity,
                score=new_score
            )

            # 履歴記録
            violation_record = {
                'timestamp': time.time(),
                'datetime': datetime.now().isoformat(),
                'type': violation.type,
                'severity': violation.severity,
                'score_impact': violation.score_impact,
                'current_score': new_score,
                'message': violation.message,
                'context': violation.context,
                'line_number': violation.line_number,
                'file': Path(filepath).name
            }
            self.violation_history.append(violation_record)

            # ログ保存
            self._save_violation_log(violation_record)

            # 統計更新
            self.stats['violations_detected'] += 1

            # コンソール出力
            print(f"\n{'='*70}")
            print(f"[{violation.severity}] {violation.type}")
            print(f"{'-'*70}")
            print(f"メッセージ: {violation.message}")
            print(f"スコア影響: {violation.score_impact}")
            print(f"現在スコア: {new_score}%")
            print(f"ファイル: {Path(filepath).name} (Line {violation.line_number})")
            print(f"{'='*70}\n")

            # 重大違反の場合は特別な警告
            if new_score < self.config['scoring']['minimum_passing']:
                self._warn_failing_score(new_score)

    def _save_violation_log(self, violation_record: dict):
        """
        違反ログをJSONL形式で保存

        Args:
            violation_record: 違反記録辞書
        """
        log_file = Path(self.config['logging']['violation_log'])

        # ログディレクトリが存在しない場合は作成
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump(violation_record, f, ensure_ascii=False)
            f.write('\n')

    def _warn_failing_score(self, score: int):
        """
        不合格スコアの警告

        Args:
            score: 現在のスコア
        """
        print(f"\n{'!'*70}")
        print(f"[WARNING]  CRITICAL WARNING: Compliance Score Below Minimum")
        print(f"{'!'*70}")
        print(f"Current Score: {score}%")
        print(f"Minimum Required: {self.config['scoring']['minimum_passing']}%")
        print(f"Deficit: {self.config['scoring']['minimum_passing'] - score}%")
        print(f"\n[WARNING]  Commits will be BLOCKED until score improves")
        print(f"{'!'*70}\n")

        # 重大違反通知
        self.notifier.send(
            title="CRITICAL: Failing Compliance Score",
            message=f"Score: {score}% (Minimum: {self.config['scoring']['minimum_passing']}%)\n"
                   f"Commits are BLOCKED",
            severity="ERROR",
            score=score
        )

    def get_stats(self) -> dict:
        """
        統計情報取得

        Returns:
            統計情報の辞書
        """
        uptime = time.time() - self.stats['start_time']
        return {
            **self.stats,
            'uptime_seconds': uptime,
            'current_score': self.scorer.get_current_score(),
            'is_passing': self.scorer.is_passing()
        }

    def print_stats(self):
        """統計情報をコンソール出力"""
        stats = self.get_stats()

        print(f"\n{'='*70}")
        print(f"[STATS] Session Monitor Statistics")
        print(f"{'='*70}")
        print(f"稼働時間: {stats['uptime_seconds']:.1f}秒")
        print(f"監視ファイル数: {stats['files_monitored']}")
        print(f"分析行数: {stats['lines_analyzed']}")
        print(f"検出違反数: {stats['violations_detected']}")
        print(f"現在スコア: {stats['current_score']}%")
        print(f"合格状態: {'[OK] PASSING' if stats['is_passing'] else '[ERROR] FAILING'}")
        print(f"{'='*70}\n")


def start_monitoring(config_path: str = "config.yaml"):
    """
    監視開始

    Args:
        config_path: 設定ファイルのパス
    """
    # 設定ファイルの絶対パス解決
    config_file = Path(config_path)
    if not config_file.is_absolute():
        config_file = Path(__file__).parent / config_path

    # 設定読み込み
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    log_dir = Path(config['monitoring']['log_directory'])

    # ログディレクトリ存在確認
    if not log_dir.exists():
        print(f"[WARNING]  Warning: Log directory does not exist: {log_dir}")
        print(f"   Creating directory...")
        log_dir.mkdir(parents=True, exist_ok=True)

    # イベントハンドラとオブザーバー初期化
    event_handler = SessionMonitor(str(config_file))
    observer = Observer()
    observer.schedule(event_handler, str(log_dir), recursive=False)
    observer.start()

    print(f"\n{'='*70}")
    print(f"[START] 8-Layer Enforcement System - Session Monitor Started")
    print(f"{'='*70}")
    print(f"[DIR] Monitoring: {log_dir}")
    print(f"[STATS] Initial Compliance Score: {event_handler.scorer.get_current_score()}%")
    print(f"[INFO] Watching for violations...")
    print(f"   Press Ctrl+C to stop")
    print(f"{'='*70}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n{'='*70}")
        print(f"[INFO]  Session Monitor Stopped")
        print(f"{'='*70}")

        # 最終統計表示
        event_handler.print_stats()

    observer.join()


if __name__ == "__main__":
    # コマンドライン引数から設定ファイルパス取得（任意）
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"

    try:
        start_monitoring(config_path)
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
