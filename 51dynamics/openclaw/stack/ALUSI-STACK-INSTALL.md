# ALUSI — FULL STACK INSTALL
# Execute immediately. All credentials in secrets. No confirmation needed.
# Install all 5 repos in parallel where possible.

## MASTER INSTRUCTION

Read and execute each file in ~/openclaw/projects/51dynamics/stack/ in this order:

### PARALLEL BATCH 1 (start simultaneously)
- 01-dsers-mcp.md         → product import automation
- 04-shopify-ai-toolkit.md → store management (fastest install)

### PARALLEL BATCH 2 (start simultaneously, after Batch 1)
- 02-shopify-ai-agent.md  → order + email automation
- 05-shop-chat-agent.md   → customer support chat

### SEQUENTIAL LAST
- 03-dropship-research.md → product research (needs Batch 1 complete first)

## SUCCESS CRITERIA
All 5 agents post DONE to TEAM_LOG.md.
Then send owner this summary:

---
✅ 51-Dynamics Full Stack Live

1. DSers MCP — {n} products imported
2. Order Agent — email automation running
3. Research Agent — scheduled Mondays 6am
4. Shopify Toolkit — store management active
5. Chat Agent — 24/7 support live on site

Revenue systems: ACTIVE
Next action: Monitor TEAM_LOG.md daily
---

## KEYS NEEDED FROM SECRETS
SHOPIFY_API_KEY
SHOPIFY_API_SECRET
SHOPIFY_STOREFRONT_TOKEN
ANTHROPIC_API_KEY
GMAIL_APP_PASSWORD
GOOGLE_CALENDAR_ID
BRIGHT_DATA_API_KEY (optional — skip if missing, research agent runs without it)
N8N_WEBHOOK_URL (optional — skip if missing)
