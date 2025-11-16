"""
コンプライアンススコア計算
"""

import json
import time
import yaml
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from violation_detector import Violation

class ComplianceScorer:
    """スコア計算・管理"""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.current_score = self.config['scoring']['initial_score']
        self.score_log = self.config['logging']['score_log']

        # ログファイル初期化
        Path(self.score_log).parent.mkdir(parents=True, exist_ok=True)

        # 初期スコア記録
        self._save_score("session_start")

    def add_violation(self, violation: 'Violation') -> int:
        """違反によるスコア減点"""
        self.current_score += violation.score_impact  # score_impactは負数
        self.current_score = max(0, self.current_score)  # 0未満にしない

        self._save_score(f"violation:{violation.type}")

        return self.current_score

    def get_current_score(self) -> int:
        """現在のスコア取得"""
        return self.current_score

    def is_passing(self) -> bool:
        """合格基準チェック"""
        minimum = self.config['scoring']['minimum_passing']
        return self.current_score >= minimum

    def reset(self):
        """スコアリセット"""
        self.current_score = self.config['scoring']['initial_score']
        self._save_score("reset")

    def _save_score(self, event: str):
        """スコア履歴保存（JSONL）"""
        with open(self.score_log, 'a', encoding='utf-8') as f:
            json.dump({
                'timestamp': time.time(),
                'event': event,
                'score': self.current_score
            }, f)
            f.write('\n')

    def get_score_history(self, last_n: int = 10) -> list:
        """スコア履歴取得"""
        if not Path(self.score_log).exists():
            return []

        with open(self.score_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        history = []
        for line in lines[-last_n:]:
            history.append(json.loads(line))

        return history


if __name__ == "__main__":
    # テスト
    from violation_detector import ViolationDetector

    scorer = ComplianceScorer()
    detector = ViolationDetector()

    print(f"Initial Score: {scorer.get_current_score()}%")

    # 違反を模擬
    test_content = 'Edit "test.lkml"'
    violations = detector.detect(test_content)

    for v in violations:
        new_score = scorer.add_violation(v)
        print(f"Violation: {v.type} → New Score: {new_score}%")

    print(f"\nPassing: {scorer.is_passing()}")
    print(f"\nHistory:")
    for entry in scorer.get_score_history():
        print(f"  {entry}")
