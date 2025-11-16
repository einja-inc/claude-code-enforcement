#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDE.md自動チェックシステム
タスク開始時に自動的にCLAUDE.mdのルールをチェックし、違反を検出する
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime

# 文字化け防止
sys.stdout.reconfigure(encoding='utf-8')

class ClaudeMDChecker:
    """CLAUDE.mdルールチェッカー"""

    def __init__(self):
        self.claude_md_path = Path.home() / '.claude' / 'CLAUDE.md'
        self.mandatory_codex_path = Path.home() / '.claude' / 'MANDATORY_CODEX_CHECK.md'
        self.violations = []
        self.warnings = []

    def check_task_type(self, user_message: str) -> dict:
        """
        タスクの種類を判定し、必要なルールをチェック

        Args:
            user_message: ユーザーのメッセージ

        Returns:
            dict: チェック結果
        """
        result = {
            'task_type': None,
            'codex_required': False,
            'todowrite_required': False,
            'rules': []
        }

        # データ分析タスクの検出
        data_analysis_keywords = [
            'Excel', 'CSV', 'データ', '分析', 'マッピング', '辞書',
            '対応', '日本語', '英語', 'タップ数', '集計'
        ]

        if any(keyword in user_message for keyword in data_analysis_keywords):
            result['task_type'] = 'data_analysis'
            result['codex_required'] = True
            result['todowrite_required'] = True
            result['rules'].append('MANDATORY_CODEX_CHECK.md')

        # マッピング・辞書作成タスクの検出
        mapping_keywords = [
            'マッピング', '辞書作成', '対応関係', '英語.*日本語'
        ]

        if any(re.search(keyword, user_message) for keyword in mapping_keywords):
            result['task_type'] = 'mapping_creation'
            result['codex_required'] = True
            result['todowrite_required'] = True
            result['rules'].append('MANDATORY_CODEX_CHECK.md')

        return result

    def check_codex_collaboration(self, conversation_history: list) -> bool:
        """
        会話履歴からCodex協力の証拠を検出

        Args:
            conversation_history: 会話履歴（最新5メッセージ）

        Returns:
            bool: Codex協力が検出されたかどうか
        """
        codex_patterns = [
            r'Task\(.*Codex.*analyst',
            r'Codex analystと協力',
            r'Codexで検証',
            r'Codexに依頼'
        ]

        for message in conversation_history:
            for pattern in codex_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return True

        return False

    def check_todowrite_usage(self, conversation_history: list) -> bool:
        """
        会話履歴からTodoWrite使用の証拠を検出

        Args:
            conversation_history: 会話履歴（最新5メッセージ）

        Returns:
            bool: TodoWrite使用が検出されたかどうか
        """
        todowrite_patterns = [
            r'TodoWrite',
            r'todos.*status',
            r'タスクリスト'
        ]

        for message in conversation_history:
            for pattern in todowrite_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return True

        return False

    def generate_report(self, task_check: dict, conversation_history: list = None) -> str:
        """
        チェック結果レポートを生成

        Args:
            task_check: タスクチェック結果
            conversation_history: 会話履歴（オプション）

        Returns:
            str: レポート
        """
        report = []
        report.append('=' * 60)
        report.append('🛡️ CLAUDE.md ルール自動チェック')
        report.append('=' * 60)
        report.append(f'チェック日時: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report.append('')

        # タスクタイプ
        if task_check['task_type']:
            report.append(f'📋 検出されたタスクタイプ: {task_check["task_type"]}')
        else:
            report.append('📋 タスクタイプ: 通常タスク')

        report.append('')

        # 必須ルール
        if task_check['codex_required']:
            report.append('⚠️ **Codex協力が必須です**')
            report.append('   - データ分析/マッピング/辞書作成タスクのため')
            report.append('   - 参照: .claude/MANDATORY_CODEX_CHECK.md')

            # 会話履歴がある場合、Codex協力を確認
            if conversation_history:
                codex_found = self.check_codex_collaboration(conversation_history)
                if codex_found:
                    report.append('   ✅ Codex協力が検出されました')
                else:
                    report.append('   ❌ Codex協力が検出されませんでした（違反）')
                    self.violations.append('Codex協力なし')

        if task_check['todowrite_required']:
            report.append('⚠️ **TodoWrite使用が必須です**')
            report.append('   - 8-10個のタスク項目を作成してください')

            # 会話履歴がある場合、TodoWrite使用を確認
            if conversation_history:
                todo_found = self.check_todowrite_usage(conversation_history)
                if todo_found:
                    report.append('   ✅ TodoWrite使用が検出されました')
                else:
                    report.append('   ❌ TodoWrite使用が検出されませんでした（違反）')
                    self.violations.append('TodoWrite未使用')

        report.append('')

        # 違反サマリー
        if self.violations:
            report.append('🚨 **検出された違反**')
            for v in self.violations:
                report.append(f'   - {v}')
            report.append('')
            report.append('⚠️ 違反を修正してください。さもなくば、コミットがブロックされます。')
        else:
            report.append('✅ **ルール違反なし**')

        report.append('')
        report.append('=' * 60)

        return '\n'.join(report)

def check_task(user_message: str, conversation_history: list = None):
    """
    タスクをチェックしてレポートを出力

    Args:
        user_message: ユーザーのメッセージ
        conversation_history: 会話履歴（オプション）
    """
    checker = ClaudeMDChecker()
    task_check = checker.check_task_type(user_message)
    report = checker.generate_report(task_check, conversation_history)

    print(report)

    # 違反がある場合は終了コード1を返す
    if checker.violations:
        return 1
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python auto_claude_md_checker.py "user message" [conversation_history_file]')
        sys.exit(1)

    user_message = sys.argv[1]
    conversation_history = []

    if len(sys.argv) > 2:
        # 会話履歴ファイルから読み込み
        history_file = sys.argv[2]
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                conversation_history = f.readlines()

    exit_code = check_task(user_message, conversation_history)
    sys.exit(exit_code)
