#!/bin/bash
# CRON SETUP — Schedules all empire automations
# Run once on Mac Mini

echo "⏰ Installing empire cron jobs..."

# Backup existing crontab
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d).txt 2>/dev/null

# Add empire cron jobs
(crontab -l 2>/dev/null; cat << 'EOF'

# ============================================
# ADAI EMPIRE — AUTOMATED SCHEDULE
# ============================================

# Morning brief — 7:00 AM daily
0 7 * * * openclaw run SovereignProxy --task morning_briefing

# System doctor + security scan — 5:00 AM daily
0 5 * * * openclaw doctor --fix && clawhub scan --security

# Outcome collector — 6:00 AM daily
0 6 * * * openclaw run OutcomeCollector

# Cost guard check — every 4 hours
0 */4 * * * openclaw run CostGuard --alert-threshold 8

# BLCO signal scan — 9 AM and 2 PM weekdays
0 9,14 * * 1-5 openclaw run BLCO_Broker --task scan_signals

# B2B outreach batch — 10 AM weekdays
0 10 * * 1-5 openclaw run B2B_Outreach --task send_batch --limit 40

# SEO content generation — 11 AM daily
0 11 * * * openclaw run SEO_Content --task generate_article

# Trading sentinel — every 30 min during market hours (Mon-Fri 9:30-16:00 ET = 8:30-15:00 CT)
*/30 8-15 * * 1-5 openclaw run Trading_Sentinel --task check_signals

# Social media scheduler — 8 AM and 6 PM daily
0 8,18 * * * openclaw run Social_Poster --task post_scheduled

# Weekly pattern analysis — Sunday 11 PM
0 23 * * 0 openclaw run PatternAnalyzer --weekly

# Memory compression — Sunday midnight
0 0 * * 0 openclaw run MemoryCompressor

# Nightly backup — 2 AM daily
0 2 * * * cp ~/.openclaw/config/soul.md ~/.openclaw/memory/archive/soul_$(date +\%Y\%m\%d).md && cp ~/.openclaw/config/brain.md ~/.openclaw/memory/archive/brain_$(date +\%Y\%m\%d).md

# 51-Dynamics store check — 9 AM daily
0 9 * * * openclaw run Monitor_51Dynamics --task daily_digest

EOF
) | crontab -

echo "✅ Cron jobs installed"
crontab -l | grep openclaw | wc -l
echo "   jobs scheduled"
echo ""
echo "🚀 Schedule active. Empire runs automatically."
