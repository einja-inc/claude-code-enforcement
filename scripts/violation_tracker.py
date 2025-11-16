#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Violation Tracker - CLAUDE.md Rule Enforcement
違反を記録・カウント・チェックするシステム

Usage:
    py violation_tracker.py check            # 違反履歴を確認
    py violation_tracker.py add <type>       # 違反を記録
    py violation_tracker.py reset            # 違反をリセット
    py violation_tracker.py is_blocked       # ブロック状態か確認

Exit Codes:
    0: OK (ブロックなし)
    1: BLOCKED (違反が閾値超過)
"""

import sys
import json
from pathlib import Path
from datetime import datetime


class ViolationTracker:
    def __init__(self):
        self.violations_file = Path.home() / ".claude" / "logs" / "violations.json"
        self.violations_file.parent.mkdir(parents=True, exist_ok=True)

        # 違反の重みとブロック閾値
        self.violation_weights = {
            "no_thinking": 10,               # thinkingブロックなし
            "no_codex": 10,                  # Codex協力なし（単一ファイルでも）
            "no_todowrite": 10,              # TodoWrite不足（8項目未満）
            "unauthorized_change": 15,       # 勝手な要件変更
            "sample_data_confusion": 20,     # サンプルデータ誤表示
            "no_clarification": 10,          # 曖昧要求を質問せず実装
            "excel_read_tool": 10,           # ExcelにRead tool使用
            "excel_csv_request": 10,         # CSV変換依頼
            "no_parallel_execution": 10,     # 並列実行すべきを逐次実行
            "join_key_speculation": 15,      # 結合キー推測（特に危険）
            "requirement_speculation": 10,   # 推測による実装
        }
        self.block_threshold = 10  # 10点で次回ブロック（1回違反で即ブロック）
        self.warning_threshold = 5  # 5点で警告

    def load_violations(self) -> dict:
        """違反履歴を読み込み"""
        if not self.violations_file.exists():
            return {
                "total_score": 0,
                "violations": [],
                "last_reset": datetime.now().isoformat()
            }

        try:
            with open(self.violations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load violations: {e}")
            return {"total_score": 0, "violations": [], "last_reset": datetime.now().isoformat()}

    def save_violations(self, data: dict):
        """違反履歴を保存"""
        try:
            with open(self.violations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Could not save violations: {e}")

    def add_violation(self, violation_type: str, details: str = ""):
        """違反を記録"""
        if violation_type not in self.violation_weights:
            print(f"[ERROR] Unknown violation type: {violation_type}")
            return

        data = self.load_violations()
        weight = self.violation_weights[violation_type]

        violation_entry = {
            "type": violation_type,
            "weight": weight,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        data["violations"].append(violation_entry)
        data["total_score"] = sum(v["weight"] for v in data["violations"])

        self.save_violations(data)

        print(f"[VIOLATION RECORDED]")
        print(f"  Type: {violation_type}")
        print(f"  Weight: {weight}")
        print(f"  Total Score: {data['total_score']}")

        if data["total_score"] >= self.block_threshold:
            print(f"\n[CRITICAL] Score exceeds block threshold ({self.block_threshold})")
            print(f"           Next prompt will be BLOCKED")
        elif data["total_score"] >= self.warning_threshold:
            print(f"\n[WARNING] Score exceeds warning threshold ({self.warning_threshold})")
            print(f"          Approaching block threshold")

    def check_status(self):
        """現在のステータスを表示"""
        data = self.load_violations()

        print("=" * 60)
        print("  CLAUDE.md Rule Compliance - Violation Status")
        print("=" * 60)
        print()
        print(f"Total Violation Score: {data['total_score']}")
        print(f"Warning Threshold:     {self.warning_threshold}")
        print(f"Block Threshold:       {self.block_threshold}")
        print()

        if data["total_score"] >= self.block_threshold:
            print("[STATUS] BLOCKED - Next prompt will be rejected")
        elif data["total_score"] >= self.warning_threshold:
            print("[STATUS] WARNING - Approaching block threshold")
        else:
            print("[STATUS] OK - Compliance acceptable")

        print()
        print(f"Recent Violations ({len(data['violations'])} total):")
        print("-" * 60)

        for v in data["violations"][-5:]:  # 最新5件
            print(f"  [{v['timestamp']}]")
            print(f"  Type: {v['type']} (Weight: {v['weight']})")
            if v.get('details'):
                print(f"  Details: {v['details']}")
            print()

        print("=" * 60)

    def is_blocked(self) -> bool:
        """ブロック状態かチェック"""
        data = self.load_violations()
        return data["total_score"] >= self.block_threshold

    def reset(self):
        """違反履歴をリセット"""
        data = {
            "total_score": 0,
            "violations": [],
            "last_reset": datetime.now().isoformat()
        }
        self.save_violations(data)
        print("[OK] Violations reset successfully")
        print("     You can now continue with clean slate")


def main():
    if len(sys.argv) < 2:
        print("Usage: violation_tracker.py <command>")
        print("Commands: check, add <type>, reset, is_blocked")
        sys.exit(1)

    tracker = ViolationTracker()
    command = sys.argv[1]

    if command == "check":
        tracker.check_status()
        sys.exit(0)

    elif command == "add":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: violation_tracker.py add <type> [details]")
            sys.exit(1)
        violation_type = sys.argv[2]
        details = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        tracker.add_violation(violation_type, details)
        sys.exit(0)

    elif command == "reset":
        tracker.reset()
        sys.exit(0)

    elif command == "is_blocked":
        if tracker.is_blocked():
            data = tracker.load_violations()
            print(f"[BLOCKED] Violation score: {data['total_score']}")
            print(f"          Threshold: {tracker.block_threshold}")
            sys.exit(1)
        else:
            print("[OK] Not blocked")
            sys.exit(0)

    else:
        print(f"[ERROR] Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
