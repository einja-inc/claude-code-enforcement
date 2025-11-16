#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
8-Layer Enforcement System - Integration Test
Tests the complete flow of all layers working together
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path

# Add enforcement directory to path
enforcement_dir = Path(__file__).parent
sys.path.insert(0, str(enforcement_dir))

from violation_detector import ViolationDetector, Violation
from compliance_scorer import ComplianceScorer
from notification_manager import NotificationManager

class IntegrationTester:
    def __init__(self):
        self.detector = ViolationDetector()
        self.scorer = ComplianceScorer()
        self.notifier = NotificationManager()
        self.test_results = []

    def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "="*60)
        print("8-LAYER ENFORCEMENT SYSTEM - INTEGRATION TEST")
        print("="*60 + "\n")

        tests = [
            self.test_violation_detection,
            self.test_scoring_system,
            self.test_notification_system,
            self.test_git_hook_exists,
            self.test_auto_correction_available,
            self.test_session_monitor_running,
            self.test_complete_flow
        ]

        for test in tests:
            try:
                result = test()
                self.test_results.append(result)
            except Exception as e:
                self.test_results.append({
                    'test': test.__name__,
                    'status': 'ERROR',
                    'error': str(e)
                })

        self.print_summary()
        return all(r['status'] == 'PASS' for r in self.test_results)

    def test_violation_detection(self):
        """Test Layer 5: Violation detection"""
        print("[TEST 1/7] Violation Detection System")

        test_content = "Read \"test.py\"\nEdit \"test.py\""

        violations = self.detector.detect(test_content, line_number=0)

        if violations:
            print(f"  [OK] Detected {len(violations)} violation(s)")
            for v in violations:
                print(f"       - {v.type}: {v.score_impact} points")
            return {'test': 'violation_detection', 'status': 'PASS', 'violations': len(violations)}
        else:
            print("  [ERROR] No violations detected (expected at least 1)")
            return {'test': 'violation_detection', 'status': 'FAIL'}

    def test_scoring_system(self):
        """Test Layer 5: Compliance scoring"""
        print("\n[TEST 2/7] Compliance Scoring System")

        # Reset score
        self.scorer.current_score = 100
        initial = self.scorer.get_current_score()
        print(f"  Initial score: {initial}")

        # Add violation
        violation = Violation(
            type='test_violation',
            severity='WARNING',
            score_impact=-20,
            message='Test violation',
            line_number=1,
            context='test context'
        )

        new_score = self.scorer.add_violation(violation)
        print(f"  After violation: {new_score}")

        if new_score == 80:
            print("  [OK] Scoring system working correctly")
            return {'test': 'scoring_system', 'status': 'PASS', 'score_change': f"{initial} -> {new_score}"}
        else:
            print(f"  [ERROR] Expected 80, got {new_score}")
            return {'test': 'scoring_system', 'status': 'FAIL'}

    def test_notification_system(self):
        """Test Layer 5: Notification system"""
        print("\n[TEST 3/7] Notification System")

        try:
            self.notifier.send(
                "Integration Test",
                "Testing notification system",
                "INFO"
            )
            print("  [OK] Notification sent (check Windows Action Center)")
            return {'test': 'notification_system', 'status': 'PASS'}
        except Exception as e:
            print(f"  [WARNING] Notification failed: {e}")
            return {'test': 'notification_system', 'status': 'WARN', 'error': str(e)}

    def test_git_hook_exists(self):
        """Test Layer 1: Git hook installation"""
        print("\n[TEST 4/7] Git Hook Installation")

        project_hook = Path(r"C:\Users\musta\Desktop\PJ\いいんじゃ\フォーム分析\.git\hooks\pre-commit")

        if project_hook.exists():
            print(f"  [OK] Git hook installed at: {project_hook}")
            return {'test': 'git_hook', 'status': 'PASS', 'location': str(project_hook)}
        else:
            print(f"  [ERROR] Git hook not found at: {project_hook}")
            return {'test': 'git_hook', 'status': 'FAIL'}

    def test_auto_correction_available(self):
        """Test Layer 7: Auto-correction system"""
        print("\n[TEST 5/7] Auto-Correction System")

        auto_correct_file = enforcement_dir / 'auto_correct_suggestions.py'

        if auto_correct_file.exists():
            print(f"  [OK] Auto-correction system available")

            # Test import
            try:
                from auto_correct_suggestions import AutoCorrectSuggester
                suggester = AutoCorrectSuggester()
                # Check if suggester has the expected attributes
                patterns_count = len(suggester.correction_patterns) if hasattr(suggester, 'correction_patterns') else 0
                print(f"  [OK] AutoCorrectSuggester loaded with {patterns_count} patterns")
                return {'test': 'auto_correction', 'status': 'PASS', 'patterns': patterns_count}
            except Exception as e:
                print(f"  [ERROR] Failed to load: {e}")
                return {'test': 'auto_correction', 'status': 'FAIL', 'error': str(e)}
        else:
            print(f"  [ERROR] Auto-correction file not found")
            return {'test': 'auto_correction', 'status': 'FAIL'}

    def test_session_monitor_running(self):
        """Test Layer 5: Session monitor daemon"""
        print("\n[TEST 6/7] Session Monitor Daemon")

        pid_file = enforcement_dir / 'daemon' / 'watchdog.pid'

        if pid_file.exists():
            with open(pid_file) as f:
                pid = int(f.read().strip())

            # Check if process is running
            try:
                import psutil
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    print(f"  [OK] Session monitor running (PID: {pid})")
                    print(f"       CPU: {process.cpu_percent()}%, Memory: {process.memory_info().rss / 1024 / 1024:.1f}MB")
                    return {'test': 'session_monitor', 'status': 'PASS', 'pid': pid}
                else:
                    print(f"  [WARNING] PID file exists but process not running")
                    return {'test': 'session_monitor', 'status': 'WARN'}
            except ImportError:
                print(f"  [INFO] psutil not available, cannot verify process")
                return {'test': 'session_monitor', 'status': 'SKIP'}
        else:
            print(f"  [WARNING] Session monitor not running (no PID file)")
            return {'test': 'session_monitor', 'status': 'WARN'}

    def test_complete_flow(self):
        """Test complete flow: violation -> detection -> scoring -> notification"""
        print("\n[TEST 7/7] Complete Integration Flow")

        print("  Step 1: Creating test violation...")
        test_content = 'User: "Add feature X"\nAssistant: Read "feature.py"\nAssistant: Edit "feature.py"'

        print("  Step 2: Detecting violations...")
        violations = self.detector.detect(test_content, line_number=0)

        if not violations:
            print("  [ERROR] No violations detected")
            return {'test': 'complete_flow', 'status': 'FAIL', 'step': 'detection'}

        print(f"  [OK] Detected {len(violations)} violation(s)")

        print("  Step 3: Updating compliance score...")
        self.scorer.current_score = 100
        for v in violations:
            new_score = self.scorer.add_violation(v)

        print(f"  [OK] Score updated: 100 -> {new_score}")

        print("  Step 4: Sending notification...")
        try:
            self.notifier.send(
                "Integration Test",
                f"Flow test complete. Score: {new_score}",
                "INFO"
            )
            print("  [OK] Notification sent")
        except Exception as e:
            print(f"  [WARNING] Notification failed: {e}")

        print("  Step 5: Checking git hook would block...")
        if new_score < 70:
            print(f"  [OK] Score {new_score} < 70, commit would be blocked")
            flow_result = 'COMPLETE_BLOCK'
        else:
            print(f"  [INFO] Score {new_score} >= 70, commit would be allowed")
            flow_result = 'COMPLETE_ALLOW'

        return {
            'test': 'complete_flow',
            'status': 'PASS',
            'result': flow_result,
            'violations': len(violations),
            'final_score': new_score
        }

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        warned = sum(1 for r in self.test_results if r['status'] in ['WARN', 'SKIP'])

        print(f"\nTotal Tests: {len(self.test_results)}")
        print(f"  [OK] Passed: {passed}")
        print(f"  [ERROR] Failed: {failed}")
        print(f"  [WARNING] Warnings/Skipped: {warned}")

        print("\nDetailed Results:")
        for r in self.test_results:
            status_symbol = {
                'PASS': '[OK]',
                'FAIL': '[ERROR]',
                'WARN': '[WARNING]',
                'SKIP': '[INFO]',
                'ERROR': '[ERROR]'
            }.get(r['status'], '[?]')

            print(f"  {status_symbol} {r['test']}: {r['status']}")
            if 'error' in r:
                print(f"       Error: {r['error']}")

        print("\n" + "="*60)

        if failed == 0:
            print("[OK] ALL TESTS PASSED")
        else:
            print(f"[ERROR] {failed} TEST(S) FAILED")

        print("="*60 + "\n")

        # Save results to file
        results_file = enforcement_dir / 'test_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': time.time(),
                'summary': {
                    'total': len(self.test_results),
                    'passed': passed,
                    'failed': failed,
                    'warned': warned
                },
                'results': self.test_results
            }, f, indent=2, ensure_ascii=False)

        print(f"Results saved to: {results_file}\n")

def main():
    tester = IntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
