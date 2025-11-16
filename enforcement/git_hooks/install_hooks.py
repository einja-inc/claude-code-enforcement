#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
8-Layer Enforcement System - Git Hooks Installer

Purpose:
    Install/uninstall pre-commit hook to git repository
    Verify installation
    Provide easy setup for users

Usage:
    python install_hooks.py install   - Install hooks
    python install_hooks.py uninstall - Remove hooks
    python install_hooks.py verify    - Check installation
    python install_hooks.py test      - Test hook execution
"""

import sys
import os
import shutil
from pathlib import Path
import subprocess

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        RED = GREEN = YELLOW = CYAN = WHITE = MAGENTA = ""
    class Style:
        BRIGHT = RESET_ALL = ""


# Paths
SCRIPT_DIR = Path(__file__).parent
PRE_COMMIT_SOURCE = SCRIPT_DIR / "pre-commit"
ENFORCEMENT_DIR = Path(r"C:\Users\musta\.claude\enforcement")

# Find git repository root
def find_git_repo():
    """
    Find .git directory by traversing up from current directory

    Returns:
        Path: Git repository root, or None if not found
    """
    current = Path.cwd()

    # Check common project locations
    common_locations = [
        Path(r"C:\Users\musta\Desktop\PJ\いいんじゃ\フォーム分析"),
        current
    ]

    for location in common_locations:
        git_dir = location / ".git"
        if git_dir.exists() and git_dir.is_dir():
            return location

    # Traverse up from current directory
    for parent in [current] + list(current.parents):
        git_dir = parent / ".git"
        if git_dir.exists() and git_dir.is_dir():
            return parent

    return None


def install_hooks():
    """Install pre-commit hook to git repository"""

    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}8-Layer Enforcement System - Git Hooks Installer{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    # Find git repository
    print(f"{Fore.WHITE}Searching for git repository...{Style.RESET_ALL}")
    repo_root = find_git_repo()

    if not repo_root:
        print(f"{Fore.RED}Error: Git repository not found.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please run this script from within a git repository.{Style.RESET_ALL}")
        return False

    print(f"{Fore.GREEN}Found git repository: {repo_root}{Style.RESET_ALL}\n")

    # Paths
    hooks_dir = repo_root / ".git" / "hooks"
    pre_commit_dest = hooks_dir / "pre-commit"

    # Create hooks directory if not exists
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # Check if hook already exists
    if pre_commit_dest.exists():
        print(f"{Fore.YELLOW}Warning: pre-commit hook already exists.{Style.RESET_ALL}")
        response = input(f"{Fore.CYAN}Overwrite existing hook? [y/N]: {Style.RESET_ALL}").strip().lower()

        if response != 'y':
            print(f"{Fore.YELLOW}Installation cancelled.{Style.RESET_ALL}")
            return False

        # Backup existing hook
        backup_path = pre_commit_dest.with_suffix('.backup')
        shutil.copy2(pre_commit_dest, backup_path)
        print(f"{Fore.GREEN}Existing hook backed up to: {backup_path}{Style.RESET_ALL}\n")

    # Copy hook file
    try:
        shutil.copy2(PRE_COMMIT_SOURCE, pre_commit_dest)
        print(f"{Fore.GREEN}✓ Copied pre-commit hook{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error copying hook: {e}{Style.RESET_ALL}")
        return False

    # Make executable (Unix-style permissions, may not apply on Windows)
    try:
        os.chmod(pre_commit_dest, 0o755)
        print(f"{Fore.GREEN}✓ Set executable permissions{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Could not set permissions: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This is normal on Windows and should not affect functionality.{Style.RESET_ALL}")

    # Verify installation
    print(f"\n{Fore.WHITE}Verifying installation...{Style.RESET_ALL}")

    if pre_commit_dest.exists():
        size = pre_commit_dest.stat().st_size
        print(f"{Fore.GREEN}✓ Hook file exists ({size} bytes){Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Hook file not found{Style.RESET_ALL}")
        return False

    # Check Python shebang
    with open(pre_commit_dest, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        if first_line.startswith('#!') and 'python' in first_line.lower():
            print(f"{Fore.GREEN}✓ Python shebang detected{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Warning: Unexpected shebang: {first_line}{Style.RESET_ALL}")

    # Install colorama if not present
    print(f"\n{Fore.WHITE}Checking dependencies...{Style.RESET_ALL}")
    try:
        import colorama
        print(f"{Fore.GREEN}✓ colorama installed{Style.RESET_ALL}")
    except ImportError:
        print(f"{Fore.YELLOW}Installing colorama...{Style.RESET_ALL}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'colorama'],
                          check=True, capture_output=True)
            print(f"{Fore.GREEN}✓ colorama installed successfully{Style.RESET_ALL}")
        except subprocess.CalledProcessError:
            print(f"{Fore.YELLOW}Warning: Could not install colorama. Hook will work without colors.{Style.RESET_ALL}")

    # Success message
    print(f"\n{Fore.GREEN}{'='*80}")
    print(f"{Fore.GREEN}{Style.BRIGHT}Installation Complete! ✅{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")

    print(f"{Fore.WHITE}Pre-commit hook installed at:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{pre_commit_dest}{Style.RESET_ALL}\n")

    print(f"{Fore.WHITE}Next steps:{Style.RESET_ALL}")
    print(f"1. Test the hook: {Fore.CYAN}python {__file__} test{Style.RESET_ALL}")
    print(f"2. Make a test commit: {Fore.CYAN}git commit -m \"Test commit\"{Style.RESET_ALL}")
    print(f"3. Hook will run automatically before each commit\n")

    return True


def uninstall_hooks():
    """Remove pre-commit hook from git repository"""

    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}Uninstalling Git Hooks{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    # Find git repository
    repo_root = find_git_repo()

    if not repo_root:
        print(f"{Fore.RED}Error: Git repository not found.{Style.RESET_ALL}")
        return False

    pre_commit_dest = repo_root / ".git" / "hooks" / "pre-commit"

    if not pre_commit_dest.exists():
        print(f"{Fore.YELLOW}No pre-commit hook found. Nothing to uninstall.{Style.RESET_ALL}")
        return True

    # Confirm uninstallation
    response = input(f"{Fore.YELLOW}Remove pre-commit hook? [y/N]: {Style.RESET_ALL}").strip().lower()

    if response != 'y':
        print(f"{Fore.YELLOW}Uninstallation cancelled.{Style.RESET_ALL}")
        return False

    try:
        pre_commit_dest.unlink()
        print(f"{Fore.GREEN}✓ Pre-commit hook removed{Style.RESET_ALL}\n")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error removing hook: {e}{Style.RESET_ALL}")
        return False


def verify_installation():
    """Verify hook installation"""

    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}Verifying Git Hooks Installation{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    repo_root = find_git_repo()

    if not repo_root:
        print(f"{Fore.RED}✗ Git repository not found{Style.RESET_ALL}")
        return False

    print(f"{Fore.GREEN}✓ Git repository: {repo_root}{Style.RESET_ALL}")

    pre_commit_dest = repo_root / ".git" / "hooks" / "pre-commit"

    if not pre_commit_dest.exists():
        print(f"{Fore.RED}✗ Pre-commit hook not installed{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Run: python {__file__} install{Style.RESET_ALL}")
        return False

    print(f"{Fore.GREEN}✓ Pre-commit hook exists{Style.RESET_ALL}")

    # Check file content
    with open(pre_commit_dest, 'r', encoding='utf-8') as f:
        content = f.read()
        if '8-Layer Enforcement System' in content:
            print(f"{Fore.GREEN}✓ Hook content verified{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Warning: Hook may be from different source{Style.RESET_ALL}")

    # Check enforcement system
    if ENFORCEMENT_DIR.exists():
        print(f"{Fore.GREEN}✓ Enforcement directory exists{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Warning: Enforcement directory not found at {ENFORCEMENT_DIR}{Style.RESET_ALL}")

    logs_dir = ENFORCEMENT_DIR / "logs"
    if logs_dir.exists():
        print(f"{Fore.GREEN}✓ Logs directory exists{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Warning: Logs directory not found{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}Verification complete!{Style.RESET_ALL}\n")
    return True


def test_hook():
    """Test hook execution"""

    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}Testing Pre-commit Hook{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    repo_root = find_git_repo()

    if not repo_root:
        print(f"{Fore.RED}Error: Git repository not found.{Style.RESET_ALL}")
        return False

    pre_commit_dest = repo_root / ".git" / "hooks" / "pre-commit"

    if not pre_commit_dest.exists():
        print(f"{Fore.RED}Error: Pre-commit hook not installed.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Run: python {__file__} install{Style.RESET_ALL}")
        return False

    print(f"{Fore.WHITE}Executing hook...{Style.RESET_ALL}\n")

    try:
        # Execute hook directly
        result = subprocess.run(
            [sys.executable, str(pre_commit_dest)],
            capture_output=False,  # Show output directly
            text=True
        )

        print(f"\n{Fore.WHITE}Hook exit code: {result.returncode}{Style.RESET_ALL}")

        if result.returncode == 0:
            print(f"{Fore.GREEN}Hook executed successfully (commit would be allowed){Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Hook blocked commit (exit code: {result.returncode}){Style.RESET_ALL}")

        return True

    except Exception as e:
        print(f"{Fore.RED}Error executing hook: {e}{Style.RESET_ALL}")
        return False


def print_usage():
    """Print usage information"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}8-Layer Enforcement System - Git Hooks Installer{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    print(f"{Fore.WHITE}Usage:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}python {__file__} <command>{Style.RESET_ALL}\n")

    print(f"{Fore.WHITE}Commands:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}install{Style.RESET_ALL}   - Install pre-commit hook to git repository")
    print(f"  {Fore.GREEN}uninstall{Style.RESET_ALL} - Remove pre-commit hook")
    print(f"  {Fore.GREEN}verify{Style.RESET_ALL}    - Verify hook installation")
    print(f"  {Fore.GREEN}test{Style.RESET_ALL}      - Test hook execution")
    print(f"  {Fore.GREEN}help{Style.RESET_ALL}      - Show this help message\n")

    print(f"{Fore.WHITE}Examples:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}python {__file__} install{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}python {__file__} test{Style.RESET_ALL}\n")


def main():
    """Main execution"""

    if len(sys.argv) < 2:
        print_usage()
        return 1

    command = sys.argv[1].lower()

    commands = {
        'install': install_hooks,
        'uninstall': uninstall_hooks,
        'verify': verify_installation,
        'test': test_hook,
        'help': print_usage
    }

    if command not in commands:
        print(f"{Fore.RED}Error: Unknown command '{command}'{Style.RESET_ALL}")
        print_usage()
        return 1

    try:
        success = commands[command]()
        if command != 'help':
            return 0 if success else 1
        return 0
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
        return 1
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
