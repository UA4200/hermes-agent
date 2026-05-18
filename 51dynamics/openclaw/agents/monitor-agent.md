# AGENT 4 — MONITOR
# Role: Daily KPI digest → Alusi via WhatsApp/Slack
# Schedule: runs every 24hrs at 8am
# Token budget: ultra-minimal. Numbers only in reports.

## ENV
Load: secrets/.env → SHOPIFY_API_KEY, INSTANTLY_API_KEY, APIFY_API_TOKEN, SLACK_WEBHOOK or WHATSAPP_TOKEN

## DAILY PULL (parallel requests)

### Shopify
GET /admin/api/2024-01/orders.json?status=any&created_at_min={yesterday}
Extract: orders_count, total_revenue, top_product, abandoned_carts

### Instantly.ai
GET /api/v1/campaign/analytics
Extract: emails_sent, open_rate, reply_count, meetings_booked

### Apify
GET /v2/acts/runs?status=SUCCEEDED
Extract: last_scrape_date, leads_generated

## DAILY DIGEST FORMAT (send to Alusi)
Keep under 100 words. Numbers only. No fluff.

---
📊 51-Dynamics Daily — {date}

🛒 Orders: {n} | Revenue: ${x}
📦 Top product: {name}
🛒 Abandoned carts: {n}

📧 Emails sent: {n} | Opens: {x}% | Replies: {n}
🤝 B2B replies: {n}

🔍 New leads scraped: {n}

⚠️ Alerts: {any_blockers or "None"}
---

## WEEKLY SIGNAL (every Monday)
Add revenue vs target chart to 51dynamics/data/weekly-report.md

## DONE SIGNAL
Write to TEAM_LOG.md:
MONITOR | ACTIVE | Digest sent {date} {time}
