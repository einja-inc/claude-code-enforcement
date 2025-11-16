#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for pre-commit hook

Purpose:
    Validate hook functionality with different compliance scores
    Simulate git commit scenarios

Usage:
    python test_hook.py
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Paths
ENFORCEMENT_DIR = Path(r"C:\Users\musta\.claude\enforcement")
LOGS_DIR = ENFORCEMENT_DIR / "logs"
SCORES_FILE = LOGS_DIR / "compliance_scores.jsonl"
VIOLATIONS_FILE = LOGS_DIR / "violations.jsonl"
HOOK_FILE = ENFORCEMENT_DIR / "git_hooks" / "pre-commit"

# Test scenarios
SCENARIOS = [
    {
        "name": "High Score (100%)",
        "score": 100,
        "violation_count": 0,
        "violations": [],
        "expected_exit": 0,
        "expected_output": "COMMIT ALLOWED"
    },
    {
        "name": "Medium Score (85%)",
        "score": 85,
        "violation_count": 2,
        "violations": [
            {
                "timestamp": datetime.now().isoformat(),
                "type": "insufficient_todowrite",
                "score_impact": -10,
                "current_score": 90,
                "message": "TodoWrite項目数が8未満"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "type": "no_gemini_validation",
                "score_impact": -5,
                "current_score": 85,
                "message": "Gemini検証なし"
            }
        ],
        "expected_exit": 0,
        "expected_output": "COMMIT ALLOWED"
    },
    {
        "name": "Low Score (65%) - Should Block",
        "score": 65,
        "violation_count": 5,
        "violations": [
            {
                "timestamp": datetime.now().isoformat(),
                "type": "no_codex_collaboration",
                "score_impact": -20,
                "current_score": 80,
                "message": "Codex協力なしでLookML編集を検出"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "type": "sequential_execution",
                "score_impact": -20,
                "current_score": 60,
                "message": "並列実行可能なTask()を逐次実行"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "type": "insufficient_todowrite",
                "score_impact": -10,
                "current_score": 70,
                "message": "TodoWrite項目数が8未満"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "type": "missing_byterover_retrieve",
                "score_impact": -15,
                "current_score": 85,
                "message": "タスク開始前のByterover検索なし"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "type": "no_gemini_validation",
                "score_impact": -10,
                "current_score": 75,
                "message": "ビジネスロジック判断でGemini未使用"
            }
        ],
        "expected_exit": 1,
        "expected_output": "COMMIT BLOCKED"
    },
    {
        "name": "Critical Score (50%) - Should Block",
        "score": 50,
        "violation_count": 10,
        "violations": [
            {
                "timestamp": datetime.now().isoformat(),
                "type": "sample_data_confusion",
                "score_impact": -50,
                "current_score": 50,
                "message": "サンプルデータの明示なし"
            }
        ],
        "expected_exit": 1,
        "expected_output": "COMMIT BLOCKED"
    }
]


def create_test_environment(scenario):
    """Create test score and violation files"""

    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Write score
    score_entry = {
        "score": scenario["score"],
        "timestamp": datetime.now().isoformat(),
        "violation_count": scenario["violation_count"]
    }

    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        f.write(json.dumps(score_entry) + '\n')

    # Write violations
    if scenario["violations"]:
        with open(VIOLATIONS_FILE, 'w', encoding='utf-8') as f:
            for violation in scenario["violations"]:
                f.write(json.dumps(violation) + '\n')
    else:
        # Clear violations file
        VIOLATIONS_FILE.write_text('')


def run_hook():
    """Execute pre-commit hook"""

    if not HOOK_FILE.exists():
        print(f"Error: Hook file not found at {HOOK_FILE}")
        return None, None

    try:
        result = subprocess.run(
            [sys.executable, str(HOOK_FILE)],
            capture_output=True,
            text=True,
            timeout=10
        )

        return result.returncode, result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        print("Error: Hook execution timed out")
        return None, None
    except Exception as e:
        print(f"Error executing hook: {e}")
        return None, None


def validate_result(scenario, exit_code, output):
    """Validate hook execution result"""

    passed = True

    # Check exit code
    if exit_code != scenario["expected_exit"]:
        print(f"  ✗ Exit code mismatch: expected {scenario['expected_exit']}, got {exit_code}")
        passed = False
    else:
        print(f"  ✓ Exit code correct: {exit_code}")

    # Check output contains expected text
    if scenario["expected_output"] not in output:
        print(f"  ✗ Output missing expected text: '{scenario['expected_output']}'")
        passed = False
    else:
        print(f"  ✓ Output contains: '{scenario['expected_output']}'")

    # Check score displayed
    if f"{scenario['score']}%" not in output:
        print(f"  ✗ Score not displayed in output")
        passed = False
    else:
        print(f"  ✓ Score displayed: {scenario['score']}%")

    return passed


def main():
    """Main test execution"""

    print("\n" + "="*80)
    print("Pre-commit Hook Test Suite")
    print("="*80 + "\n")

    # Check hook exists
    if not HOOK_FILE.exists():
        print(f"Error: Hook file not found at {HOOK_FILE}")
        print("Please install the hook first:")
        print(f"  python {ENFORCEMENT_DIR / 'git_hooks' / 'install_hooks.py'} install")
        return 1

    print(f"Hook file: {HOOK_FILE}")
    print(f"Logs directory: {LOGS_DIR}\n")

    # Run all scenarios
    results = []

    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"\nTest {i}/{len(SCENARIOS)}: {scenario['name']}")
        print("-" * 80)

        # Setup test environment
        print(f"  Setting up: score={scenario['score']}%, violations={scenario['violation_count']}")
        create_test_environment(scenario)

        # Run hook
        print(f"  Executing hook...")
        exit_code, output = run_hook()

        if exit_code is None:
            print(f"  ✗ Hook execution failed")
            results.append((scenario['name'], False))
            continue

        # Validate result
        print(f"  Validating result...")
        passed = validate_result(scenario, exit_code, output)

        results.append((scenario['name'], passed))

        if passed:
            print(f"\n  ✅ Test PASSED")
        else:
            print(f"\n  ❌ Test FAILED")
            print(f"\n  Hook output:\n{output}")

    # Summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80 + "\n")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\n  Total: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n  🎉 All tests passed!")
        return 0
    else:
        print(f"\n  ⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
