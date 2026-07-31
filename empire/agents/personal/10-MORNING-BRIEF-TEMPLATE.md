# MORNING BRIEF — ADAI EMPIRE
# Delivered: 7:00 AM CDT daily via Telegram
# Agent: Morning_Brief (Haiku for data pull → Sonnet for summary)
# Nathan replies "GO" to approve the day's work

---

## BRIEF FORMAT

```
🦞 ADAI EMPIRE — MORNING BRIEF
{DAY}, {DATE} | {TIME} CDT

━━━━━━━━━━━━━━━━━━━━━━━━
💰 REVENUE UPDATE
━━━━━━━━━━━━━━━━━━━━━━━━

51-Dynamics (Shopify):
  Orders yesterday: {N} | Revenue: ${X}
  Total orders: {N} | Total revenue: ${X}
  Top product: {PRODUCT}

B2B Pipeline (ADAI INC):
  New leads added: {N}
  Emails sent yesterday: {N}
  Replies received: {N}
  Hot leads (call booked): {N}
  Active proposals: {N} (${X} total value)

BLCO Pipeline:
  Contacts in verification: {N}
  Replies received: {N}
  Stage: {STATUS}

Trading Sentinel:
  Signals detected: {N}
  Paper P&L yesterday: ${X}
  Alerts: {ALERTS}

━━━━━━━━━━━━━━━━━━━━━━━━
📬 APPROVALS NEEDED
━━━━━━━━━━━━━━━━━━━━━━━━

{N} items waiting in queue:

{LIST_OF_DRAFTS_AWAITING_APPROVAL}

━━━━━━━━━━━━━━━━━━━━━━━━
📅 TODAY'S SCHEDULE
━━━━━━━━━━━━━━━━━━━━━━━━

{CALENDAR_EVENTS_TODAY}

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 TOP 3 PRIORITIES
━━━━━━━━━━━━━━━━━━━━━━━━

1. {HIGHEST_VALUE_ACTION}
2. {SECOND_PRIORITY}
3. {THIRD_PRIORITY}

━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AGENT UPDATES
━━━━━━━━━━━━━━━━━━━━━━━━

{AGENT_STATUS_SUMMARY_FROM_TEAM_LOG}

━━━━━━━━━━━━━━━━━━━━━━━━
💡 INSIGHT OF THE DAY
━━━━━━━━━━━━━━━━━━━━━━━━

{ONE_ACTIONABLE_INSIGHT_FROM_DATA}

Reply "GO" to release today's queued work.
Reply "HOLD" to pause all outbound.
Reply "SKIP {ITEM}" to skip a specific approval.
```

---

## DATA SOURCES (Haiku pulls these at 6:50 AM before brief compiles)

| Source | What to pull | Tool |
|--------|-------------|------|
| Shopify | Orders, revenue, top product | Shopify MCP |
| Gmail | Unread replies in B2B/BLCO labels | Gmail MCP |
| TEAM_LOG.md | Agent completions overnight | Read file |
| Google Calendar | Today's events | Calendar MCP |
| Approval queue | ~/.openclaw/memory/approval-queue.json | Read file |
| Trading | Paper P&L from OpenAlgo | OpenAlgo API |

---

## BRIEF COMPILATION LOGIC

```python
# Pseudocode — Alusi / Haiku executes this at 6:50 AM
data = {
    "shopify": fetch_shopify_yesterday(),
    "gmail_replies": count_replies("ADAI EMPIRE/B2B Leads/Replied"),
    "approvals": read_json("~/.openclaw/memory/approval-queue.json"),
    "calendar": get_calendar_events(today),
    "team_log": read_recent_entries("TEAM_LOG.md", hours=24),
    "trading_pnl": fetch_openalgo_pnl(yesterday),
}
brief = sonnet.generate(BRIEF_FORMAT, data)
telegram.send(NATHAN_CHAT_ID, brief)
```

---

## RESPONSE HANDLING

| Nathan replies | Action |
|---------------|--------|
| "GO" | Release all queued approvals in queue |
| "HOLD" | Pause all outbound, keep building |
| "SKIP email to {NAME}" | Skip that specific draft |
| "SEND {NAME}" | Send that specific draft NOW |
| "MORE INFO {ITEM}" | Pull deeper data on that item |

---

## ESCALATION RULES

If Nathan doesn't reply by 10 AM:
- Hold all outbound actions
- Send reminder: "⚠️ Morning brief awaiting GO. Reply when ready."

If Nathan doesn't reply by 2 PM:
- Final reminder: "⚠️ Empire paused. {N} items waiting. Reply GO or HOLD."

DONE SIGNAL: MORNING_BRIEF | {date} | DELIVERED | {N} items in queue
