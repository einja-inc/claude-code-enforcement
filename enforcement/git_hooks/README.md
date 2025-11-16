# Layer 1: Pre-commit Git Hook

## Overview

This is the **Layer 1** implementation of the 8-Layer Enforcement System. It provides a git pre-commit hook that automatically checks compliance scores before allowing commits.

## Features

- **Automatic Compliance Check**: Runs before every `git commit`
- **Score Threshold Enforcement**: Blocks commits if compliance score < 70%
- **Violation History Display**: Shows recent violations with details
- **Color-coded Output**: Clear visual feedback (green/yellow/red)
- **Bypass Detection**: Warns when `--no-verify` is used
- **Fail-safe Mode**: Allows commits on errors to prevent workflow disruption

## Files

| File | Purpose |
|------|---------|
| `pre-commit` | Main git hook script (Python) |
| `install_hooks.py` | Installation/management tool |
| `install_hooks.bat` | Windows batch wrapper |
| `README.md` | This documentation |

## Installation

### Method 1: Windows Batch (Easiest)

Double-click `install_hooks.bat` or run:

```cmd
install_hooks.bat install
```

### Method 2: Python Script

```bash
python install_hooks.py install
```

### Method 3: Manual Installation

1. Copy `pre-commit` to your git repository:
   ```bash
   cp pre-commit /path/to/your/repo/.git/hooks/pre-commit
   ```

2. Make executable (Unix-like systems):
   ```bash
   chmod +x /path/to/your/repo/.git/hooks/pre-commit
   ```

3. Install colorama (optional, for colored output):
   ```bash
   pip install colorama
   ```

## Usage

### Automatic Execution

Once installed, the hook runs automatically before every commit:

```bash
git commit -m "Your commit message"
```

**If compliance score >= 70%:**
```
================================================================================
8-Layer Enforcement System - Pre-commit Hook (Layer 1)
================================================================================

Checking compliance score...
Last Updated: 2025-11-15 17:30:00
Total Violations: 2

Current Compliance Score: 85%
Status: ✅ PASS

================================================================================
COMMIT ALLOWED ✅
================================================================================

Compliance requirements met.
Your changes will be committed.
```

**If compliance score < 70%:**
```
================================================================================
8-Layer Enforcement System - Pre-commit Hook (Layer 1)
================================================================================

Checking compliance score...
Last Updated: 2025-11-15 17:25:00
Total Violations: 5

Current Compliance Score: 65%
Status: ❌ FAIL

================================================================================
COMMIT BLOCKED
================================================================================

Your compliance score (65%) is below the minimum threshold (70%).
Please fix the following violations before committing:

================================================================================
Recent Violations (Latest 5 items):
================================================================================

1. no_codex_collaboration
   Time: 2025-11-15 17:20:00
   Impact: -20 points
   Current Score: 65%
   Message: Codex協力なしでLookML編集を検出

2. insufficient_todowrite
   Time: 2025-11-15 17:15:00
   Impact: -10 points
   Current Score: 85%
   Message: TodoWrite項目数が8未満

...

================================================================================
How to fix:
1. Review violations above
2. Follow CLAUDE.md guidelines to improve compliance
3. Check session monitor status:
   python C:\Users\musta\.claude\enforcement\daemon\service_manager.py status
4. Retry commit when score >= 70%
================================================================================
```

### Manual Testing

Test the hook without making a commit:

```bash
python install_hooks.py test
```

### Verification

Check if hook is properly installed:

```bash
python install_hooks.py verify
```

### Uninstallation

Remove the hook:

```bash
python install_hooks.py uninstall
```

## Bypass (Not Recommended)

You can bypass the hook with:

```bash
git commit --no-verify -m "Emergency commit"
```

**Warning:** This action is detected and logged. Use only in emergencies.

## Configuration

### Minimum Score Threshold

Edit `pre-commit` line 40:

```python
MIN_COMPLIANCE_SCORE = 70  # Change this value
```

### Maximum Violations Displayed

Edit `pre-commit` line 41:

```python
MAX_VIOLATIONS_DISPLAY = 5  # Change this value
```

## Dependencies

### Required
- Python 3.11+
- Access to `C:\Users\musta\.claude\enforcement\logs\` directory

### Optional
- `colorama` - For colored terminal output
  ```bash
  pip install colorama
  ```

## Data Sources

The hook reads compliance data from:

- **Scores**: `C:\Users\musta\.claude\enforcement\logs\compliance_scores.jsonl`
- **Violations**: `C:\Users\musta\.claude\enforcement\logs\violations.jsonl`

These files are maintained by the **Layer 5 Session Monitor**.

## Troubleshooting

### Hook not executing

**Symptom:** Git commits without running the hook

**Solution:**
1. Verify installation:
   ```bash
   python install_hooks.py verify
   ```

2. Check file exists:
   ```bash
   ls .git/hooks/pre-commit
   ```

3. Reinstall:
   ```bash
   python install_hooks.py install
   ```

### Python not found

**Symptom:** `python: command not found`

**Solution:**
1. Install Python 3.11+ from https://www.python.org/
2. Ensure Python is in PATH
3. On Windows, try `py` instead of `python`

### No color output

**Symptom:** Colors not displayed in terminal

**Solution:**
1. Install colorama:
   ```bash
   pip install colorama
   ```

2. Or edit `pre-commit` to disable colors (set `HAS_COLOR = False`)

### Hook errors on every commit

**Symptom:** Hook fails with exceptions

**Solution:**
1. Check logs:
   ```bash
   cat C:\Users\musta\.claude\enforcement\logs\service.log
   ```

2. The hook has fail-safe mode - it will allow commits if errors occur
3. Fix the underlying issue in enforcement logs

### Wrong git repository

**Symptom:** Hook installed in wrong repository

**Solution:**
1. Navigate to correct repository:
   ```bash
   cd /path/to/correct/repo
   ```

2. Run installer:
   ```bash
   python C:\Users\musta\.claude\enforcement\git_hooks\install_hooks.py install
   ```

## Integration with Other Layers

This hook integrates with:

- **Layer 5 (Session Monitor)**: Reads compliance scores generated by session monitor
- **Layer 2 (MCP Audit)**: Uses violation data from AI audits
- **Layer 7 (Auto-correction)**: Displays fix suggestions from auto-correction engine

## Architecture

```
Git Commit Attempt
    ↓
.git/hooks/pre-commit (Python script)
    ↓
Read compliance_scores.jsonl
    ↓
score >= 70%?
    ├─ YES → Allow commit (exit 0)
    └─ NO  → Read violations.jsonl
                ↓
             Display violations
                ↓
             Block commit (exit 1)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Commit allowed (score >= 70%) |
| 1 | Commit blocked (score < 70% or user cancelled) |

## Future Enhancements

- [ ] Integration with VS Code notifications
- [ ] Auto-fix suggestions displayed inline
- [ ] Interactive mode to fix violations before committing
- [ ] Custom violation filters
- [ ] Per-repository score thresholds

## Support

For issues or questions:

1. Check logs: `C:\Users\musta\.claude\enforcement\logs\`
2. Review documentation: `docs/8-LAYER-SYSTEM-ARCHITECTURE.md`
3. Test hook: `python install_hooks.py test`

## License

Part of the 8-Layer Enforcement System.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-15 | Initial implementation |

---

**Next Steps:** Install Layer 5 Session Monitor to generate compliance scores.
