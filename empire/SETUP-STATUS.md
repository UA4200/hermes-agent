# ADAI EMPIRE — SETUP STATUS
# READ THIS FIRST before executing any install or setup task.
# Last updated: 2026-07-13 by Claude Code session
# Purpose: Tells Alusi what is already live so she does NOT duplicate work.

---

## WHAT IS ALREADY LIVE — DO NOT REPEAT

### Shopify (51dynamics.store)
- [x] Store confirmed live: 51-Dynamics, USD, Shopify Basic plan
- [x] Discount code RETURN10 active (10% off, all customers, no expiry)
- [x] 4 smart collections created: Pet Food & Treats, Beds & Comfort, Toys & Enrichment, Health & Wellness
- [x] 1 product already live: Complete Pet Grooming Kit — 7 Piece Set ($34.99) — auto-populated Health & Wellness
- [ ] NEXT: Import 20 products from CJ Dropshipping using empire/agents/wealth/01-SHOPIFY-PRODUCTS-TO-ADD.md

### Gmail (nua.consult1@gmail.com)
- [x] Full label hierarchy created — ADAI EMPIRE with 19 sub-labels across all business lines
- [x] 6 email draft templates saved (B2B 4-email sequence + BLCO outreach + 51-Dynamics launch)
- [ ] NEXT: When B2B outreach begins, pull drafts and personalize with lead variables before sending
- [ ] NEXT: Nathan approves 51-Dynamics launch email (PETLOVE20) before it sends to list

### Google Drive (ugoasiegbu@gmail.com)
- [x] Root folder: ADAI EMPIRE (ID: 1clHEUtHCnWLlWZv4X2ltLuvWQ9KfQI0Y)
- [x] 5 business subfolders created (ADAI INC, BLCO, 51-Dynamics, UGC Studio, Trading Sentinel)
- [x] 5 working documents/sheets created (Services doc, B2B CRM sheet, BLCO tracker, Products sheet, UGC calendar)
- [ ] NEXT: Populate B2B CRM sheet with leads from Apollo/Hunter scrape

### AgentMail
- [x] adai-b2b@agentmail.to — B2B outreach drafts inbox (draft-only, never auto-send)
- [x] blco-trading@agentmail.to — BLCO pipeline drafts inbox (draft-only, never auto-send)
- [ ] NOTE: Free plan limit reached — 51-Dynamics support uses main Gmail for now

### Notion
- [x] ADAI EMPIRE Command Center page live: https://app.notion.com/p/39cf4fd20b548123948be7024ecb300a
- [x] B2B Leads CRM page: https://app.notion.com/p/39cf4fd20b5481a3a604c663c876949d
- [x] B2B Lead Pipeline DATABASE live with full schema (9 columns, 9 status stages, auto-ID)
- [x] BLCO Pipeline Tracker page: https://app.notion.com/p/39cf4fd20b548192a801e4229b161b99
- [x] 51-Dynamics Store Operations page: https://app.notion.com/p/39cf4fd20b548147b82bd7e71d7bd8cb
- [ ] NEXT: Add BLCO database (same pattern as B2B) when first contacts come in

### Calendly (ugoasiegbu@gmail.com)
- [x] Event type renamed: "ADAI INC — Discovery Call" (20 min, purple)
- [x] Description added: maps automation opportunities, no pitch, just value
- [x] Booking URL: https://calendly.com/ugoasiegbu/new-meeting
- [x] USE THIS LINK in all B2B emails, proposals, and social bios

### Google Calendar (ugoasiegbu@gmail.com)
- [x] Daily Approval Window: Mon–Fri 9:00–9:30 AM CDT (recurring, blueberry) — event ID: c1vdrr4paudgma5e1e0tb57k64
- [x] Evening Review: Mon–Fri 9:00–9:20 PM CDT (recurring, graphite) — event ID: sgp2c97su4ud4l7srr21sskusk
- [x] Weekly Strategy Review: Every Sunday 10:00–11:00 AM CDT (recurring, basil) — event ID: cl93nt5vae9r0cmln23t71duag

### Canva
- [x] Folder created: "ADAI EMPIRE — Social Content" (ID: FAHPTgBTuA8)
- [x] 12 design candidates generated (3 sets × 4): 51-Dynamics IG, 51-Dynamics Twitter/X, ADAI INC IG
- [ ] NEXT: Nathan picks 1 of 4 from each set — Alusi saves to account and schedules

### Repo Playbooks Written
- [x] empire/agents/wealth/01-SHOPIFY-PRODUCTS-TO-ADD.md — 20 products with CJ search terms, tags, margins
- [x] empire/agents/wealth/02-B2B-EMAIL-SEQUENCE.md — Full 4-email sequence with rules
- [x] empire/agents/wealth/04-UGC-CONTENT-CALENDAR.md — Week 1 content + SadTalker pipeline
- [x] empire/agents/ops/08-ADAI-INC-SERVICES.md — 3-tier pricing + discovery framework
- [x] empire/agents/ops/09-PROPOSAL-TEMPLATE.md — Full proposal doc with ROI calculator
- [x] empire/agents/personal/10-MORNING-BRIEF-TEMPLATE.md — Brief format + GO/HOLD commands

---

## WHAT STILL NEEDS TO HAPPEN

### Nathan does these (requires human action):
1. **Canva** — Pick favourite design (1–4) from each of the 3 sets at canva.com, tell Alusi which one
2. **CJ Dropshipping** — Open 51dynamics.store/admin → Apps → CJ Dropshipping → import the 20 products from 01-SHOPIFY-PRODUCTS-TO-ADD.md using the exact tags listed
3. **Supabase** — Create a project at supabase.com (free tier), then tell Alusi — she'll set up leads + orders tables
4. **META_ACCESS_TOKEN** — Get from developers.facebook.com → add to Alusi's secrets store → IG/FB posts will start flowing
5. **TikTok API** — Pending review (1–4 weeks), use Buffer free plan in the meantime

### Alusi does these (automated, waiting on Nathan's GO):
1. **B2B Lead Scraping** — Run Apify Google Maps + Apollo scrape for healthcare IT / SaaS leads → populate B2B Leads CRM sheet
2. **Morning Brief** — Send first brief when Mac Mini is running and cron is active
3. **BLCO Scanning** — Begin scanning UN Comtrade + Reuters for BLCO signals → populate BLCO tracker
4. **Product Import** — After Nathan syncs CJ products, tag them correctly and activate in store
5. **Social Posting** — Once Nathan picks Canva designs and TikTok/X keys are confirmed, schedule Week 1 content

---

## KEY CREDENTIALS (Alusi reads from secrets)
- Shopify: In Alusi secrets — connected via MCP
- Gmail: In Alusi secrets — connected via MCP
- Calendly: In Alusi secrets — connected via MCP
- X (Twitter): X_BEARER_TOKEN + X_API_KEY + X_API_SECRET in secrets
- TikTok: client_key awzoie1ovupwfr9f — API review pending
- META: META_ACCESS_TOKEN — NOT YET ADDED
- AgentMail: adai-b2b@agentmail.to + blco-trading@agentmail.to — pod 772b89f0

## KEY RULES (non-negotiable)
- DRAFT ONLY: Never send any email without Nathan's explicit approval
- 3-STRIKE RULE: 3 failures on any task → stop → report to Nathan
- 10-MIN CAP: No task runs >10 min without a heartbeat check
- COST GUARD: Alert Nathan at $8/day API cost, halt non-critical at $10/day
- NO CREDENTIAL EXPOSURE: Never log or expose API keys in output
