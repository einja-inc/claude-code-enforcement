"""
違反パターン検出エンジン

8-Layer Enforcement System - Layer 5: Session監視
9種類の違反パターンを検出し、コンプライアンススコアを計算する
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Violation:
    """違反情報"""
    type: str
    severity: str  # "INFO", "WARNING", "ERROR"
    score_impact: int
    message: str
    line_number: int
    context: str


class ViolationDetector:
    """違反検出エンジン"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初期化

        Args:
            config_path: 設定ファイルのパス
        """
        config_file = Path(__file__).parent / config_path
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        """
        違反パターン定義

        Returns:
            違反パターン辞書
        """
        return {
            # 違反1: Codex協力なしでファイル編集
            "no_codex_collaboration": {
                "pattern": r'(?:Edit|Write)\s+["\'].*\.(?:lkml|py|js|ts)["\'](?!.*Task\(["\'].*Codex)',
                "severity": "ERROR",
                "message": "Codex協力なしでファイル編集を検出",
                "validator": None
            },

            # 違反2: TodoWrite項目数不足
            "insufficient_todowrite": {
                "pattern": r'TodoWrite\s*\{.*?todos:\s*\[(.*?)\]',
                "severity": "WARNING",
                "message": "TodoWrite項目数が8未満（現在: {count}個）",
                "validator": self._validate_todowrite_count
            },

            # 違反3: Byterover retrieve未実行
            "missing_byterover_retrieve": {
                "pattern": r'Task\(',
                "severity": "WARNING",
                "message": "タスク開始前のByterover検索なし",
                "validator": self._validate_byterover_retrieve
            },

            # 違反4: Byterover store未実行
            "missing_byterover_store": {
                "pattern": r'git\s+commit',
                "severity": "WARNING",
                "message": "タスク完了後のByterover保存なし",
                "validator": self._validate_byterover_store
            },

            # 違反5: 逐次実行（並列化可能タスク）
            "sequential_execution": {
                "pattern": r'Message\s+\d+:.*?\n.*?Message\s+\d+:.*?Task\(',
                "severity": "ERROR",
                "message": "並列実行可能なTask()を逐次実行",
                "validator": None
            },

            # 違反6: Seraphina相談なし（複雑度50以上）
            "missing_seraphina": {
                "pattern": None,  # 複雑度で判定
                "severity": "ERROR",
                "message": "複雑度{score}でSeraphina相談なし（基準: 50以上）",
                "validator": self._validate_seraphina_needed
            },

            # 違反7: ルートディレクトリへのファイル作成
            "root_file_creation": {
                "pattern": r'Write\s+["\'](?!.*/)(?!.*\\)([^/\\]+\.md)["\']',
                "severity": "ERROR",
                "message": "ルートディレクトリにファイル作成: {filename}",
                "validator": self._extract_filename
            },

            # 違反8: ビジネスロジック判断でGemini未使用
            "no_gemini_validation": {
                "pattern": r'(?:business|requirement|logic|ビジネス|要件).*?(?<!Gemini)',
                "severity": "WARNING",
                "message": "ビジネスロジック判断でGemini未使用",
                "validator": None
            },

            # 違反9: サンプルデータの明示なし
            "sample_data_confusion": {
                "pattern": r'(?:sample|サンプル|test\s+data)(?!.*⚠️)(?!.*WARNING)(?!.*注意)',
                "severity": "ERROR",
                "message": "サンプルデータの明示なし（重大違反）",
                "validator": None
            }
        }

    def detect(self, content: str, line_number: int = 0) -> List[Violation]:
        """
        違反検出

        Args:
            content: 検査対象のテキスト
            line_number: 開始行番号

        Returns:
            検出された違反のリスト
        """
        violations = []

        for vtype, config in self.patterns.items():
            pattern = config.get('pattern')

            if pattern is None:
                # 複雑度判定など特殊な検証
                if config.get('validator'):
                    result = config['validator'](content)
                    if result:
                        violations.append(self._create_violation(
                            vtype, config, line_number, content, result
                        ))
            else:
                # 正規表現マッチング
                try:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                    for match in matches:
                        # 追加検証
                        if config.get('validator'):
                            result = config['validator'](match)
                            if not result:
                                continue
                        else:
                            result = {}

                        violations.append(self._create_violation(
                            vtype, config, line_number, match.group(0), result
                        ))
                except re.error as e:
                    print(f"WARNING: Regex error in {vtype}: {e}")

        return violations

    def _create_violation(self, vtype: str, config: Dict,
                         line_number: int, context: str,
                         validator_result: Dict) -> Violation:
        """
        Violationオブジェクト生成

        Args:
            vtype: 違反タイプ
            config: 違反設定
            line_number: 行番号
            context: コンテキスト
            validator_result: バリデータの結果

        Returns:
            Violationオブジェクト
        """
        score = self.config['scoring']['violations'].get(vtype, 0)
        message = config['message'].format(**validator_result) if validator_result else config['message']

        return Violation(
            type=vtype,
            severity=config['severity'],
            score_impact=score,
            message=message,
            line_number=line_number,
            context=context[:200]  # 最初の200文字のみ
        )

    def _validate_todowrite_count(self, match: re.Match) -> Optional[Dict]:
        """
        TodoWrite項目数検証

        Args:
            match: 正規表現マッチオブジェクト

        Returns:
            検証結果（違反の場合のみ）
        """
        content = match.group(1)
        # JSON形式のオブジェクトをカウント（{から始まるパターン）
        count = content.count('{')

        if count < 8:
            return {"count": count}
        return None

    def _validate_seraphina_needed(self, content: str) -> Optional[Dict]:
        """
        Seraphina相談必要性判定

        Args:
            content: 検査対象テキスト

        Returns:
            検証結果（違反の場合のみ）
        """
        complexity_score = self._calculate_complexity(content)

        if complexity_score >= 50 and "Seraphina" not in content:
            return {"score": complexity_score}
        return None

    def _extract_filename(self, match: re.Match) -> Optional[Dict]:
        """
        ファイル名抽出

        Args:
            match: 正規表現マッチオブジェクト

        Returns:
            ファイル名情報
        """
        filename = match.group(1) if match.lastindex and match.lastindex >= 1 else "unknown"
        return {"filename": filename}

    def _validate_byterover_retrieve(self, match: re.Match) -> Optional[Dict]:
        """
        Byterover retrieve検証

        Args:
            match: 正規表現マッチオブジェクト

        Returns:
            検証結果（違反の場合のみ）
        """
        # Task(の前にbyterover-retrieve-knowledgeがあるかチェック
        full_text = match.string
        task_pos = match.start()
        # Task(の前500文字以内をチェック
        context = full_text[max(0, task_pos - 500):task_pos]

        if "byterover-retrieve-knowledge" not in context:
            return {}
        return None

    def _validate_byterover_store(self, match: re.Match) -> Optional[Dict]:
        """
        Byterover store検証

        Args:
            match: 正規表現マッチオブジェクト

        Returns:
            検証結果（違反の場合のみ）
        """
        # git commitの前後にbyterover-store-knowledgeがあるかチェック
        full_text = match.string
        commit_pos = match.start()
        # git commitの前500文字をチェック
        context = full_text[max(0, commit_pos - 500):commit_pos + 500]

        if "byterover-store-knowledge" not in context:
            return {}
        return None

    def _calculate_complexity(self, content: str) -> int:
        """
        複雑度スコア計算

        計算式:
        - ファイル数: 5点/ファイル
        - エージェント数: 10点/エージェント
        - 複雑キーワード: 5点/個

        Args:
            content: 検査対象テキスト

        Returns:
            複雑度スコア
        """
        score = 0

        # ファイル数（5点/ファイル）
        file_count = len(re.findall(r'(?:Read|Write|Edit)\s+["\']', content))
        score += file_count * 5

        # エージェント数（10点/エージェント）
        agent_count = len(re.findall(r'Task\(', content))
        score += agent_count * 10

        # 複雑なキーワード（5点/個）
        complex_keywords = [
            'business logic', 'requirement', 'architecture',
            'ビジネスロジック', '要件', 'アーキテクチャ',
            'integration', 'migration', 'refactoring',
            '統合', '移行', 'リファクタリング'
        ]
        for keyword in complex_keywords:
            if keyword in content.lower():
                score += 5

        return score


def main():
    """テスト実行"""
    import sys
    # Windows環境でのUTF-8出力設定
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    detector = ViolationDetector()

    # テストケース1: Codex協力なし + TodoWrite不足
    test_content_1 = """
    User: "ファイルを修正してください"
    Assistant:
    Edit "test.lkml"

    TodoWrite { todos: [
        {content: "修正", status: "pending"}
    ]}
    """

    print("=" * 60)
    print("テストケース1: Codex協力なし + TodoWrite不足")
    print("=" * 60)
    violations = detector.detect(test_content_1)
    for v in violations:
        print(f"[{v.severity}] {v.type}: {v.message} (Score: {v.score_impact})")

    # テストケース2: サンプルデータ明示なし
    test_content_2 = """
    Here is sample data from the system:
    [{"id": 1, "name": "Test"}]
    """

    print("\n" + "=" * 60)
    print("テストケース2: サンプルデータ明示なし")
    print("=" * 60)
    violations = detector.detect(test_content_2)
    for v in violations:
        print(f"[{v.severity}] {v.type}: {v.message} (Score: {v.score_impact})")

    # テストケース3: 複雑度高いがSeraphina相談なし
    test_content_3 = """
    Task("Analyst 1", "Analyze file1", "analyst")
    Task("Analyst 2", "Analyze file2", "analyst")
    Task("Analyst 3", "Analyze file3", "analyst")
    Read "file1.py"
    Read "file2.py"
    Read "file3.py"
    Read "file4.py"
    Write "output1.py"
    Write "output2.py"
    This requires business logic validation and architecture review.
    Integration and migration planning needed.
    """

    print("\n" + "=" * 60)
    print("テストケース3: 複雑度高 + Seraphina相談なし")
    print("=" * 60)
    violations = detector.detect(test_content_3)
    for v in violations:
        print(f"[{v.severity}] {v.type}: {v.message} (Score: {v.score_impact})")

    # 複雑度スコア表示
    complexity = detector._calculate_complexity(test_content_3)
    print(f"\n複雑度スコア: {complexity}")

    print("\n" + "=" * 60)
    print("[OK] テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
