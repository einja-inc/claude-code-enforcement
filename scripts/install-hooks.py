#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Install Claude Code Hooks
Automatically installs all hooks to enforce CLAUDE.md rules
"""

import os
import sys
import shutil
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def install_git_hooks():
    """Install Git hooks"""
    git_dir = Path('.git')
    if not git_dir.exists():
        print("⚠️  Not a git repository - skipping git hooks installation")
        print("   (Git hooks will be installed when you're in a git repository)")
        return False

    hooks_dir = git_dir / 'hooks'
    hooks_dir.mkdir(exist_ok=True)

    # Install pre-commit hook
    template_path = Path('.claude/templates/git-hooks/pre-commit')
    target_path = hooks_dir / 'pre-commit'

    if template_path.exists():
        shutil.copy(template_path, target_path)
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(target_path, 0o755)
        print(f"✅ Installed: {target_path}")
        return True
    else:
        print(f"❌ Template not found: {template_path}")
        return False

def install_claude_hooks():
    """Install Claude Code hooks"""
    hooks_dir = Path('.claude/hooks')
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hooks_installed = []

    # All hooks should already be created, just verify
    required_hooks = [
        'user-prompt-submit.bat',
        'user-prompt-submit.sh',
        'assistant-response.bat',
        'assistant-response.sh',
        'pre-response.bat',
        'pre-response.sh'
    ]

    for hook in required_hooks:
        hook_path = hooks_dir / hook
        if hook_path.exists():
            if hook.endswith('.sh'):
                os.chmod(hook_path, 0o755)
            hooks_installed.append(hook)
            print(f"✅ Verified: {hook}")
        else:
            print(f"⚠️  Missing: {hook}")

    return len(hooks_installed) == len(required_hooks)

def verify_scripts():
    """Verify required scripts exist"""
    scripts_dir = Path('.claude/scripts')
    scripts_dir.mkdir(parents=True, exist_ok=True)

    required_scripts = [
        'codex-enforcer.py',
        'compliance-checker.py'
    ]

    all_exist = True
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"✅ Verified: {script}")
        else:
            print(f"❌ Missing: {script}")
            all_exist = False

    return all_exist

def main():
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🔧 CLAUDE CODE HOOKS INSTALLER")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    print("📋 Installing Claude Code hooks...")
    claude_hooks_ok = install_claude_hooks()
    print()

    print("📋 Installing Git hooks...")
    git_hooks_ok = install_git_hooks()
    print()

    print("📋 Verifying scripts...")
    scripts_ok = verify_scripts()
    print()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if claude_hooks_ok and scripts_ok:
        print("  ✅ INSTALLATION COMPLETE")
        print()
        print("  Enabled hooks:")
        print("    • user-prompt-submit - Ultra Think Mode")
        print("    • assistant-response - Completion notifications")
        print("    • pre-response - Codex collaboration enforcer")
        if git_hooks_ok:
            print("    • pre-commit - Compliance checker (Git)")
        print()
        print("  🎯 All CLAUDE.md rules will now be enforced!")
    else:
        print("  ⚠️  INSTALLATION INCOMPLETE")
        print("  Some components are missing. Please check the output above.")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

if __name__ == '__main__':
    main()
