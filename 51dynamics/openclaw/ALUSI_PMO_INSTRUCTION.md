# ALUSI — PMO Council Instruction
# Project: 51-Dynamics Pet Store Launch
# Execute immediately. No confirmation needed.

## CONTEXT (read once, share with all sub-agents)
Store: 51dynamics.store | Shopify
Niche: Pet accessories (dropship via CJ Dropshipping)
Goal: First $5K/month revenue
Tools: All credentials in secrets/.env
Skills: Pull from hesreallyhim/awesome-claude-code + travisvn/awesome-claude-skills

## ACTIVATE MULTI-AGENT COUNCIL — PARALLEL EXECUTION

Spin up 4 agents simultaneously. Each is self-contained. Do not wait for others unless dependency noted.

---

### AGENT 1 — SCRAPER (no dependency)
File: agents/scraper-agent.md
Start: immediately
Deliverable: leads.csv → drop in 51dynamics/data/

### AGENT 2 — EMAIL (depends on Agent 1 output)
File: agents/email-agent.md
Start: when leads.csv exists
Deliverable: campaign live in Instantly.ai

### AGENT 3 — SOCIAL (no dependency)
File: agents/social-media-agent.md
Start: immediately
Deliverable: 30-day content calendar + first 7 posts published

### AGENT 4 — MONITOR (no dependency)
File: agents/monitor-agent.md
Start: immediately
Deliverable: daily Slack/WhatsApp digest of store KPIs

---

## PMO REPORTING
- Report blockers to Alusi only (no noise)
- Success = each agent posts DONE + metric to TEAM_LOG.md
- Escalate only if: API failure, 0 leads found, social account suspended
