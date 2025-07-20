#!/bin/bash
# Quick script to run BAML tests and show results

echo "Running BAML tests..."
pytest tests/unit/test_baml*.py -v --tb=short 2>&1 | tee .baml_test_results.log

echo ""
echo "=== Test Summary ==="
grep -E "(PASSED|FAILED|ERROR) tests/unit/test_baml" .baml_test_results.log | sort | uniq -c
echo ""

if grep -q "FAILED" .baml_test_results.log; then
    echo "❌ Some tests are still failing. Check .baml_test_results.log for details."
    exit 1
else
    echo "✅ All BAML tests passed!"
    exit 0
fi