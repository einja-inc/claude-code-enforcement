#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Claude Code Hooks Configuration
Checks if all hooks are properly configured and ready to execute
"""

import os
import sys
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_settings_json():
    """Check if settings.json has hooks enabled"""
    settings_path = Path('.claude/settings.json')

    if not settings_path.exists():
        print(f"{RED}❌ .claude/settings.json not found{RESET}")
        return False

    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        if 'hooks' not in settings:
            print(f"{RED}❌ 'hooks' section missing in settings.json{RESET}")
            return False

        if not settings['hooks'].get('enabled', False):
            print(f"{RED}❌ Hooks not enabled in settings.json{RESET}")
            return False

        print(f"{GREEN}✅ Hooks enabled in settings.json{RESET}")

        # Check individual hooks
        required_hooks = ['user-prompt-submit', 'assistant-response', 'pre-response']
        for hook in required_hooks:
            if hook in settings['hooks'] and settings['hooks'][hook].get('enabled', False):
                print(f"{GREEN}  ✅ {hook} enabled{RESET}")
            else:
                print(f"{YELLOW}  ⚠️  {hook} not explicitly enabled{RESET}")

        return True

    except Exception as e:
        print(f"{RED}❌ Error reading settings.json: {e}{RESET}")
        return False

def check_hook_files():
    """Check if hook files exist"""
    hooks_dir = Path('.claude/hooks')

    if not hooks_dir.exists():
        print(f"{RED}❌ .claude/hooks directory not found{RESET}")
        return False

    required_hooks = [
        'user-prompt-submit.bat',
        'user-prompt-submit.sh',
        'assistant-response.bat',
        'assistant-response.sh',
        'pre-response.bat',
        'pre-response.sh'
    ]

    all_exist = True
    for hook in required_hooks:
        hook_path = hooks_dir / hook
        if hook_path.exists():
            # Check if executable (Unix)
            if hook.endswith('.sh'):
                is_executable = os.access(hook_path, os.X_OK)
                if is_executable:
                    print(f"{GREEN}✅ {hook} (executable){RESET}")
                else:
                    print(f"{YELLOW}⚠️  {hook} (not executable){RESET}")
            else:
                print(f"{GREEN}✅ {hook}{RESET}")
        else:
            print(f"{RED}❌ {hook} not found{RESET}")
            all_exist = False

    return all_exist

def check_scripts():
    """Check if required scripts exist"""
    scripts_dir = Path('.claude/scripts')

    required_scripts = [
        'codex-enforcer.py',
        'compliance-checker.py',
        'install-hooks.py'
    ]

    all_exist = True
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"{GREEN}✅ {script}{RESET}")
        else:
            print(f"{RED}❌ {script} not found{RESET}")
            all_exist = False

    return all_exist

def main():
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  🔍 HOOKS CONFIGURATION VERIFICATION")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    print("📋 Checking settings.json...")
    settings_ok = check_settings_json()
    print()

    print("📋 Checking hook files...")
    hooks_ok = check_hook_files()
    print()

    print("📋 Checking scripts...")
    scripts_ok = check_scripts()
    print()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if settings_ok and hooks_ok and scripts_ok:
        print(f"  {GREEN}✅ ALL CHECKS PASSED{RESET}")
        print()
        print("  🎯 Hooks are properly configured!")
        print("  Next steps:")
        print("    1. Restart Claude Code session")
        print("    2. Send a test prompt")
        print("    3. Look for hook output messages")
    else:
        print(f"  {RED}❌ SOME CHECKS FAILED{RESET}")
        print()
        print("  Please fix the issues above.")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

if __name__ == '__main__':
    main()
