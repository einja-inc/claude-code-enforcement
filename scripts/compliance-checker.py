#!/usr/bin/env python3
"""
Compliance Score Checker
Calculates compliance score based on CLAUDE.md rules
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class ComplianceChecker:
    def __init__(self):
        self.score = 100
        self.violations = []
        self.checks_passed = []

    def check_git_staged_files(self):
        """Check git staged files"""
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            files = result.stdout.strip().split('\n')
            return [f for f in files if f]
        except Exception as e:
            print(f"{YELLOW}Warning: Could not check git staged files: {e}{RESET}")
            return []

    def check_lookml_files(self, files):
        """Check if LookML files are being committed"""
        lookml_files = [f for f in files if f.endswith('.lkml')]
        if lookml_files:
            # LookML files found - Codex collaboration should have been used
            return lookml_files
        return []

    def check_session_log(self):
        """Check session log for Codex usage, Byterover, TodoWrite"""
        session_log_path = Path('.claude/logs/session.log')
        if not session_log_path.exists():
            return {
                'codex_used': False,
                'byterover_store': False,
                'todowrite_used': False,
                'todowrite_count': 0
            }

        try:
            with open(session_log_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                'codex_used': 'codex' in content.lower() or 'Task(' in content,
                'byterover_store': 'byterover' in content.lower() and 'store' in content.lower(),
                'todowrite_used': 'TodoWrite' in content,
                'todowrite_count': content.count('TodoWrite')
            }
        except Exception as e:
            print(f"{YELLOW}Warning: Could not read session log: {e}{RESET}")
            return {
                'codex_used': False,
                'byterover_store': False,
                'todowrite_used': False,
                'todowrite_count': 0
            }

    def calculate_score(self):
        """Calculate compliance score"""
        files = self.check_git_staged_files()

        if not files:
            print(f"{BLUE}ℹ️  No files staged for commit{RESET}")
            return True

        lookml_files = self.check_lookml_files(files)
        session_data = self.check_session_log()

        # Check LookML files without Codex
        if lookml_files and not session_data['codex_used']:
            self.score -= 25
            self.violations.append({
                'type': 'LookML files without Codex collaboration',
                'penalty': -25,
                'files': lookml_files
            })
        elif lookml_files and session_data['codex_used']:
            self.checks_passed.append('✅ LookML files with Codex collaboration')

        # Check Byterover store
        if not session_data['byterover_store']:
            self.score -= 15
            self.violations.append({
                'type': 'Missing Byterover knowledge store',
                'penalty': -15
            })
        else:
            self.checks_passed.append('✅ Byterover knowledge stored')

        # Check TodoWrite
        if not session_data['todowrite_used']:
            self.score -= 10
            self.violations.append({
                'type': 'Missing TodoWrite',
                'penalty': -10
            })
        elif session_data['todowrite_count'] < 3:
            self.score -= 5
            self.violations.append({
                'type': 'Insufficient TodoWrite usage',
                'penalty': -5,
                'note': f'Only {session_data["todowrite_count"]} todos found (recommended: 8-10)'
            })
        else:
            self.checks_passed.append(f'✅ TodoWrite used ({session_data["todowrite_count"]} todos)')

        return self.score >= 70

    def print_report(self):
        """Print compliance report"""
        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  📊 COMPLIANCE SCORE REPORT")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        # Print passed checks
        if self.checks_passed:
            for check in self.checks_passed:
                print(f"{GREEN}{check}{RESET}")
            print()

        # Print violations
        if self.violations:
            print(f"{RED}❌ VIOLATIONS:{RESET}")
            for v in self.violations:
                print(f"  {RED}[-{abs(v['penalty'])} points] {v['type']}{RESET}")
                if 'files' in v:
                    for f in v['files']:
                        print(f"    - {f}")
                if 'note' in v:
                    print(f"    {v['note']}")
            print()

        # Print score
        score_color = GREEN if self.score >= 95 else YELLOW if self.score >= 70 else RED
        print(f"  Final Score: {score_color}{self.score}/100{RESET}")

        if self.score >= 95:
            print(f"  {GREEN}Grade: PERFECT ⭐⭐⭐{RESET}")
        elif self.score >= 75:
            print(f"  {GREEN}Grade: GOOD ✅{RESET}")
        elif self.score >= 70:
            print(f"  {YELLOW}Grade: WARNING ⚠️{RESET}")
        else:
            print(f"  {RED}Grade: FAIL ❌{RESET}")

        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        if self.score < 70:
            print(f"{RED}⛔ COMMIT BLOCKED - Compliance score too low{RESET}")
            print()
            print("💡 To fix:")
            print("  1. Review .claude/CLAUDE.md rules")
            print("  2. Use Codex for LookML modifications")
            print("  3. Store knowledge with Byterover")
            print("  4. Use TodoWrite (8-10 items)")
            print()
            return False

        return True

def main():
    checker = ComplianceChecker()
    passed = checker.calculate_score()
    success = checker.print_report()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
