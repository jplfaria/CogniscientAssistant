#!/usr/bin/env python3
"""
Post-cleanup validation to ensure nothing was broken.
Compares results with pre-cleanup validation.
"""

import json
import sys
from pathlib import Path
from validate_before_cleanup import ValidationTests


def compare_results():
    """Compare pre and post cleanup results."""
    pre_file = "test_results/validation_before_cleanup.json"
    post_file = "test_results/validation_after_cleanup.json"
    
    if not Path(pre_file).exists():
        print("❌ No pre-cleanup validation found. Run validate-before-cleanup.py first!")
        return False
    
    # Run post-cleanup validation
    print("Running post-cleanup validation...\n")
    validator = ValidationTests()
    success = validator.run_all_tests()
    
    # Save post-cleanup results with different filename
    with open(post_file, "w") as f:
        json.dump({
            "timestamp": validator.results[0]["test"] if validator.results else "unknown",
            "passed": validator.passed,
            "failed": validator.failed,
            "results": validator.results
        }, f, indent=2)
    
    # Load both results
    with open(pre_file) as f:
        pre_results = json.load(f)
    
    with open(post_file) as f:
        post_results = json.load(f)
    
    # Compare
    print("\n" + "=" * 80)
    print("CLEANUP VALIDATION COMPARISON")
    print("=" * 80)
    
    print(f"\nPre-cleanup:  {pre_results['passed']} passed, {pre_results['failed']} failed")
    print(f"Post-cleanup: {post_results['passed']} passed, {post_results['failed']} failed")
    
    # Check for regressions
    pre_passing = {r["test"] for r in pre_results["results"] if r["passed"]}
    post_passing = {r["test"] for r in post_results["results"] if r["passed"]}
    
    regressions = pre_passing - post_passing
    improvements = post_passing - pre_passing
    
    if regressions:
        print("\n❌ REGRESSIONS DETECTED:")
        for test in regressions:
            print(f"  - {test}")
        print("\nDO NOT PROCEED - Revert changes or fix regressions!")
        return False
    
    if improvements:
        print("\n✅ IMPROVEMENTS:")
        for test in improvements:
            print(f"  - {test}")
    
    if post_results['failed'] == 0:
        print("\n✅ ALL TESTS PASSING - Cleanup successful!")
    elif post_results['failed'] <= pre_results['failed']:
        print("\n✅ NO REGRESSIONS - Cleanup is safe!")
    else:
        print("\n⚠️  More failures than before, but no regressions in previously passing tests")
    
    return len(regressions) == 0


def main():
    """Main function."""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    success = compare_results()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()