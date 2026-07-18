#!/bin/bash
# CRON SETUP — Schedules all empire automations
# Safe to rerun: removes previous block then reinstalls (idempotent).
# APPROVAL POLICY: Tasks that send emails, post content, or mutate external
# state require Nathan's explicit GO in the approval queue first.
# Cron tasks here only DRAFT, QUEUE, or DIAGNOSE — never send/post/fix autonomously.

set -euo pipefail

MARKER_START="# ===== ADAI-EMPIRE-CRON-START ====="
MARKER_END="# ===== ADAI-EMPIRE-CRON-END ====="

echo "⏰ Installing empire cron jobs (idempotent)..."

# Snapshot current crontab before any changes
BACKUP_FILE="/tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$BACKUP_FILE" 2>/dev/null || true
echo "  Backup saved: $BACKUP_FILE"

# Strip any previous ADAI Empire block, then append the new one
EXISTING=$(crontab -l 2>/dev/null || true)
STRIPPED=$(echo "$EXISTING" | awk "/$MARKER_START/{found=1} !found{print} /$MARKER_END/{found=0}")

(echo "$STRIPPED"; cat << EOF

$MARKER_START
# ADAI EMPIRE — AUTOMATED SCHEDULE (reinstall via CRON-SETUP.sh)
# All tasks are DRAFT/QUEUE/DIAGNOSTIC only.
# Sending, posting, or external mutations require approval-queue GO.

# Morning brief — 7:00 AM daily
0 7 * * * openclaw run SovereignProxy --task morning_briefing

# System diagnostic (read-only, no --fix) — 5:00 AM daily
0 5 * * * openclaw doctor --check && clawhub scan --security

# Outcome collector — 6:00 AM daily
0 6 * * * openclaw run OutcomeCollector

# Cost guard check — every 4 hours
0 */4 * * * openclaw run CostGuard --alert-threshold 8

# BLCO signal scan — 9 AM and 2 PM weekdays
0 9,14 * * 1-5 openclaw run BLCO_Broker --task scan_signals

# B2B outreach batch — 10 AM weekdays (DRAFT ONLY, awaits approval-queue GO)
0 10 * * 1-5 openclaw run B2B_Outreach --task draft_batch --limit 40

# SEO content generation — 11 AM daily (drafts to review queue)
0 11 * * * openclaw run SEO_Content --task generate_article

# Trading sentinel (read-only signal check, no orders placed) — every 30 min market hours CT
*/30 8-15 * * 1-5 openclaw run Trading_Sentinel --task check_signals

# Social media scheduler — 8 AM and 6 PM daily (QUEUE ONLY, awaits approval-queue GO)
0 8,18 * * * openclaw run Social_Poster --task queue_posts

# Weekly pattern analysis — Sunday 11 PM
0 23 * * 0 openclaw run PatternAnalyzer --weekly

# Memory compression — Sunday midnight
0 0 * * 0 openclaw run MemoryCompressor

# Nightly backup — 2 AM daily
0 2 * * * cp ~/.openclaw/config/soul.md ~/.openclaw/memory/archive/soul_\$(date +\%Y\%m\%d).md && cp ~/.openclaw/config/brain.md ~/.openclaw/memory/archive/brain_\$(date +\%Y\%m\%d).md

# 51-Dynamics store check — 9 AM daily
0 9 * * * openclaw run Monitor_51Dynamics --task daily_digest

$MARKER_END
EOF
) | crontab -

INSTALLED=$(crontab -l 2>/dev/null | grep -c "openclaw" || true)
echo "✅ Cron jobs installed ($INSTALLED openclaw tasks scheduled)"
echo "   Backup at: $BACKUP_FILE"
echo "   Re-run at any time — previous block is replaced, not duplicated."
echo ""
echo "🔒 Approval policy: B2B_Outreach=draft_batch, Social_Poster=queue_posts,"
echo "   doctor=--check only. No autonomous sending or external mutation."
