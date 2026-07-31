#!/bin/bash
# Tests that CRON-SETUP.sh is idempotent: running it N times produces the same
# number of empire cron entries as running it once.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETUP="$SCRIPT_DIR/CRON-SETUP.sh"
PASS=0
FAIL=0

check() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$actual" == "$expected" ]]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc — expected '$expected', got '$actual'"
    FAIL=$((FAIL + 1))
  fi
}

# Save original crontab
ORIGINAL=$(crontab -l 2>/dev/null || true)
restore_crontab() {
  if [[ -n "$ORIGINAL" ]]; then
    echo "$ORIGINAL" | crontab -
  else
    crontab -r 2>/dev/null || true
  fi
}
trap restore_crontab EXIT

echo "=== Cron Idempotency Tests ==="

# Run once
bash "$SETUP" >/dev/null 2>&1
COUNT_AFTER_ONE=$(crontab -l 2>/dev/null | grep -c "openclaw" || true)

# Run again
bash "$SETUP" >/dev/null 2>&1
COUNT_AFTER_TWO=$(crontab -l 2>/dev/null | grep -c "openclaw" || true)

check "job count stable after 2 runs" "$COUNT_AFTER_ONE" "$COUNT_AFTER_TWO"

# Run a third time
bash "$SETUP" >/dev/null 2>&1
COUNT_AFTER_THREE=$(crontab -l 2>/dev/null | grep -c "openclaw" || true)

check "job count stable after 3 runs" "$COUNT_AFTER_ONE" "$COUNT_AFTER_THREE"

# Verify approval-safe task names — no autonomous send/post/fix
CRON_CONTENT=$(crontab -l 2>/dev/null || true)

if echo "$CRON_CONTENT" | grep -q "send_batch"; then
  echo "  FAIL: Found 'send_batch' — must be 'draft_batch'"
  FAIL=$((FAIL + 1))
else
  echo "  PASS: No 'send_batch' (approval-safe)"
  PASS=$((PASS + 1))
fi

if echo "$CRON_CONTENT" | grep -q "post_scheduled"; then
  echo "  FAIL: Found 'post_scheduled' — must be 'queue_posts'"
  FAIL=$((FAIL + 1))
else
  echo "  PASS: No 'post_scheduled' (approval-safe)"
  PASS=$((PASS + 1))
fi

if echo "$CRON_CONTENT" | grep -qE "doctor.*--fix"; then
  echo "  FAIL: Found 'doctor --fix' — must be '--check' only"
  FAIL=$((FAIL + 1))
else
  echo "  PASS: No 'doctor --fix' (diagnostic-only)"
  PASS=$((PASS + 1))
fi

# Verify markers present
if echo "$CRON_CONTENT" | grep -q "ADAI-EMPIRE-CRON-START"; then
  echo "  PASS: START marker present"
  PASS=$((PASS + 1))
else
  echo "  FAIL: START marker missing"
  FAIL=$((FAIL + 1))
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] && echo "✅ All cron idempotency tests passed" || { echo "❌ $FAIL test(s) failed"; exit 1; }
