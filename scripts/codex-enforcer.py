#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Collaboration Enforcer
Ensures Codex collaboration for all required tasks per CLAUDE.md rules
"""

import sys
import os
import re
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Color codes for terminal output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class CodexEnforcer:
    def __init__(self):
        self.violations = []
        self.warnings = []

    def check_lookml_task(self, message):
        """Check if task involves LookML files - Codex collaboration required"""
        lookml_patterns = [
            r'\.lkml',
            r'\.view\.lkml',
            r'\.model\.lkml',
            r'lookml',
            r'ディメンション',
            r'メジャー',
            r'dimension',
            r'measure',
        ]

        for pattern in lookml_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False

    def check_multi_file_task(self, message):
        """Check if task involves multiple files - Codex parallel required"""
        # Count file references
        file_count = len(re.findall(r'\.lkml|\.py|\.js|\.ts|\.sql', message, re.IGNORECASE))
        return file_count >= 2

    def check_data_analysis_task(self, message):
        """Check if task involves data analysis - Codex required"""
        data_patterns = [
            r'\.xlsx',
            r'\.csv',
            r'excel',
            r'マッピング',
            r'辞書',
            r'分析',
            r'analysis',
            r'mapping',
        ]

        for pattern in data_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False

    def check_codex_evidence(self, message):
        """Check if there's evidence of Codex collaboration"""
        codex_evidence = [
            r'codex',
            r'Task\(',
            r'mcp__codex',
            r'analyst',
        ]

        for pattern in codex_evidence:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False

    def validate(self, user_message):
        """Main validation logic"""

        # Check if Codex collaboration is required
        requires_codex = False
        reasons = []

        if self.check_lookml_task(user_message):
            requires_codex = True
            reasons.append("LookML file modification detected")

        if self.check_multi_file_task(user_message):
            requires_codex = True
            reasons.append("Multiple file modification detected")

        if self.check_data_analysis_task(user_message):
            requires_codex = True
            reasons.append("Data analysis task detected")

        if not requires_codex:
            # No Codex required for this task
            return True

        # Codex is required - check if it's being used
        has_codex_evidence = self.check_codex_evidence(user_message)

        if not has_codex_evidence:
            self.violations.append({
                'type': 'MISSING_CODEX_COLLABORATION',
                'reasons': reasons,
                'severity': 'CRITICAL'
            })
            return False

        return True

    def print_report(self):
        """Print validation report"""
        if not self.violations and not self.warnings:
            print(f"{GREEN}✅ All compliance checks passed{RESET}")
            return True

        if self.violations:
            print(f"\n{RED}❌ CRITICAL VIOLATIONS DETECTED{RESET}\n")
            for v in self.violations:
                print(f"{RED}[{v['severity']}] {v['type']}{RESET}")
                for reason in v.get('reasons', []):
                    print(f"  - {reason}")
            print()
            return False

        if self.warnings:
            print(f"\n{YELLOW}⚠️  WARNINGS{RESET}\n")
            for w in self.warnings:
                print(f"{YELLOW}[WARNING] {w}{RESET}")
            print()

        return True

def main():
    """Main entry point"""
    enforcer = CodexEnforcer()

    # Get user message from command line or stdin
    if len(sys.argv) > 1:
        user_message = ' '.join(sys.argv[1:])
    else:
        # Try to read from conversation history
        user_message = sys.stdin.read() if not sys.stdin.isatty() else ""

    # If no message, skip validation (hook not applicable)
    if not user_message:
        print(f"{BLUE}ℹ️  No user message detected - skipping Codex validation{RESET}")
        sys.exit(0)

    # Validate
    is_valid = enforcer.validate(user_message)

    # Print report
    success = enforcer.print_report()

    # Exit with appropriate code
    # Exit code 2 = Blocking error (stops tool execution and feeds error to Claude)
    # Exit code 1 = Non-blocking error (warning only, execution continues)
    sys.exit(0 if success else 2)

if __name__ == '__main__':
    main()
