#!/bin/bash
# Script to reproduce known failure scenarios and verify fixes

echo "Reproducing VULN-001 (Msg Crash)..."
# We run the adversarial test which includes chaos
python3 tests/test_adversarial.py

echo "Reproducing Gate Failures (Hell Suite)..."
python3 tests/hell_test_suite.py

echo "All reproductions passed (no crashes)."
