---
name: b2b-sourcing
description: "Lead sourcing agent for ADAI INC — discovers, enriches, scores, and drafts outreach for B2B prospects using Tavily, WebSearch, Apollo, ZipRecruiter, Notion, AgentMail, and Twilio."
version: 1.0.0
author: ADAI Empire / Nathan Asiegbu
license: MIT
metadata:
  hermes:
    tags: [B2B, Lead Generation, Outreach, Apollo, Tavily, Notion, AgentMail, Sales]
    related_skills: [google-workspace, notion]
---

# B2B Lead Sourcing — ADAI INC

This skill tells Alusi how to discover, qualify, enrich, and draft outreach for B2B leads across ADAI INC's three validated ICPs: **dental practices**, **small law firms**, and **real estate agencies**.

---

## Tool Stack Map

### AVAILABLE NOW (use these)

| Tool | MCP Prefix | Sourcing Use |
|------|-----------|--------------|
| **WebSearch** | Built-in `WebSearch` | Discover businesses, verify websites, find decision-makers |
| **Tavily** | `mcp__Tavily__*` | Deep research, crawl directory pages, extract contact info |
| **Apollo.io** | `mcp__Apollo_io__*` | Search existing contact DB, enrich companies, match people |
| **ZipRecruiter** | `mcp__e48d58b6-*` | Find companies actively hiring → growth signal = good ICP match |
| **Indeed** | `mcp__Indeed__*` | Same as ZipRecruiter — hiring activity signals growth/investment |
| **Notion** | `mcp__Notion__*` | Store leads in CRM database, track pipeline status |
| **AgentMail** | `mcp__AgentMail__*` | Create personalized outreach drafts (DRAFT ONLY — no send without Nathan's GO) |
| **Gmail** | `mcp__Gmail__*` | Send approved outreach, track replies, apply pipeline labels |
| **Google Calendar** | `mcp__Google_Calendar__*` | Book discovery calls once lead replies |
| **Twilio** | `mcp__Twilio__*` | SMS follow-up for dental/real estate (high open rates) |
| **Canva** | `mcp__Canva__*` | Generate case study one-pagers and outreach assets per niche |
| **Google Drive** | `mcp__Google_Drive__*` | Store lead lists, case study PDFs, niche research files |

### Apollo.io Free Plan Limits

| Endpoint | Available? | Notes |
|---------|-----------|-------|
| `contacts_search` | ✅ Yes | Search existing DB by name/company/title |
| `organizations_enrich` | ✅ Yes | Enrich a company by domain |
| `people_match` | ✅ Yes | Match person by name + company |
| `mixed_people_api_search` | ❌ Blocked | Requires paid plan ($49+/mo) |
| `mixed_companies_search` | ✅ Yes | Company-level search works |

**Workaround for free plan:** Use `mixed_companies_search` to find the company, then `people_match` to find the decision-maker, then `organizations_enrich` to fill in missing fields.

---

### NOT IN STACK — ADD THESE

These tools would significantly boost sourcing throughput. Nathan must add them.

#### 1. Brave Search MCP ← HIGH PRIORITY (FREE TIER)
- **What it does:** Privacy-respecting web search with 2,000 free queries/month; better for business lookups than standard web search
- **Setup:** Get API key at https://api.search.brave.com → add to Alusi's secrets as `BRAVE_API_KEY`
- **Install:** In an interactive Claude Code session: `claude mcp add brave-search npx @modelcontextprotocol/server-brave-search`
- **Cost:** Free up to 2k queries/mo; $3/mo for 20k queries

#### 2. Firecrawl MCP ← HIGH PRIORITY (FREE TIER)
- **What it does:** Scrapes and crawls websites/directories — Yelp dental pages, Avvo attorney listings, Zillow agent profiles — extracts structured contact data
- **Setup:** Sign up at https://firecrawl.dev → `FIRECRAWL_API_KEY` to Alusi's secrets
- **Install:** `claude mcp add firecrawl npx firecrawl-mcp`
- **Cost:** 500 free credits; $16/mo for 3,000 credits — enough for 300 pages/mo

#### 3. Hunter.io (via API, no MCP needed)
- **What it does:** Finds and verifies professional email addresses by name + domain; critical for deliverability
- **Setup:** https://hunter.io → API key → `HUNTER_API_KEY` to Alusi's secrets
- **Script:** `source_leads.py` already uses this if key is present
- **Cost:** 25 searches/mo free; $34/mo for 500 searches

#### 4. Apollo.io Paid Plan ← MEDIUM PRIORITY
- **What it does:** Unlocks `mixed_people_api_search` — bulk prospect database with 265M+ contacts
- **Cost:** $49/mo (Basic) unlocks people search; worth it once you're sending 40 emails/day
- **Upgrade at:** https://app.apollo.io/settings/billing

#### 5. Instantly.ai ← FOR SEQUENCING (when ready to scale)
- **What it does:** Email sequencing, warmup, inbox rotation — handles the 40/day cadence automatically
- **Cost:** $37/mo (Growth)
- **Integration:** Export qualified leads from Notion → import into Instantly sequence

#### 6. Apify ← OPTIONAL POWER-UP
- **What it does:** Scalable web scraping — dental directories, state bar pages, MLS broker lists
- **Cost:** Pay-per-use ($5 starting credit free) or $49/mo
- **MCP:** `apify-mcp-server` (check Apify marketplace for Claude integration)

---

## Target ICPs

### ICP 1 — Independent Dental Practices
- Staff size: 4–15 (NOT part of a DSO/chain)
- Decision-maker: Practice owner / Office manager
- Pain: 160+ hrs/mo on insurance pre-auth, scheduling, no-show management
- Hook: "Reclaim 15–20 hrs/week of admin within 30 days"
- Retainer: $800–$2,000/mo
- Best channels: Google Maps scrape, Yelp, dental association directories (ADA, state chapters)
- ICD-10 intel: Use `mcp__ICD-10_Codes__*` to understand dental billing codes (D0100–D9999) — useful for establishing credibility in outreach

### ICP 2 — Small Law Firms (2–10 Attorneys)
- Practice areas: PI, family law, immigration, criminal defense (highest volume intake)
- Decision-maker: Managing partner, office admin
- Stack hint: Uses Clio, MyCase, or Lawmatics (these integrate with our automation)
- Pain: Every admin hour = $200–500 in lost billable work
- Hook: "120–180 billable hours per attorney per year back on the table"
- Retainer: $1,000–$2,500/mo
- Best channels: Avvo, FindLaw, state bar directories, LinkedIn

### ICP 3 — Real Estate Agencies
- Agent count: 3–25 agents
- Decision-maker: Agency owner, team lead, broker of record
- Pain: 200+ leads/week, 67% conversion loss from slow response
- Hook: "60-second AI response, 24/7 — one agency booked 14 clients + $47k in 90 days"
- Retainer: $800–$3,500/mo
- Best channels: Zillow agent directory, NAR/local MLS directories, LinkedIn

---

## Sourcing Workflow

### Phase 1: DISCOVER (find company names + websites)

**Using WebSearch (always available):**
```
Query patterns:
- Dental: "independent dental practice [CITY] [STATE] -DSO -group -dental center"
- Law: "small law firm [CITY] personal injury OR family law 2-10 attorneys site:avvo.com OR site:findlaw.com"
- Real estate: "real estate team [CITY] Zillow top agent 2025 OR 2026"
```

**Using Tavily (when connected):**
```
Use tavily_search for quick hits:
  query: "dental practice owner [city] contact email"
  search_depth: "advanced"

Use tavily_crawl for directories:
  url: "https://www.yelp.com/search?find_desc=dental&find_loc=[city]"
  limit: 20

Use tavily_extract for specific pages:
  urls: ["https://www.avvo.com/find-a-lawyer/[state]/[city]/family-law"]
```

**Using ZipRecruiter/Indeed (growth signal detection):**
```python
# Find companies actively hiring front desk / office manager / intake coordinator
# These are companies FEELING the admin pain RIGHT NOW
search_jobs(
  query="dental front desk coordinator",
  location="Chicago, IL",
  radius=25
)
# Extract company names → treat as warm ICP hits (they're actively staffing up admin)
```

**Using Apollo mixed_companies_search (when connected):**
```
Search by industry + size + location:
  q_organization_industry_tag_ids: [dental, legal services, real estate]
  organization_locations: [Chicago, IL]
  organization_num_employees_ranges: ["1,20"]
```

---

### Phase 2: ENRICH (get decision-maker contact info)

**Step 1 — Verify the company domain**
Use WebSearch: `"[company name]" [city] dental/law/real estate site:linkedin.com OR official website`

**Step 2 — Find the decision-maker**
Use `apollo_people_match`:
```
name: "Dr. John Smith" (or "John Smith")
organization_name: "[practice name]"
domain: "[company website domain]"
```

**Step 3 — Get/verify email**
Priority order:
1. Apollo `people_match` result (if email returned)
2. Hunter.io API (if HUNTER_API_KEY set): `GET https://api.hunter.io/v2/email-finder?domain={domain}&first_name={first}&last_name={last}`
3. Common pattern guessing: `firstname@domain.com`, `dr.lastname@domain.com` — verify with Hunter
4. Tavily extract: crawl their Contact/About page for email

**Step 4 — Enrich company info**
Use `apollo_organizations_enrich`:
```
domain: "theirwebsite.com"
```
Returns: employee count, tech stack, revenue estimate, social profiles

---

### Phase 3: QUALIFY (score 1–5)

| Signal | Points |
|--------|--------|
| Staff 4–15 (dental) / 2–10 atty (law) / 3–25 agents (RE) | +2 |
| Active job posting for admin role | +2 |
| No automation tools visible in their tech stack | +1 |
| Practice owner is the decision-maker (not a VP/manager) | +1 |
| Independent (not part of chain/DSO/franchise) | +1 |
| Phone number + email both found | +1 |
| LinkedIn has recent activity (last 30 days) | +1 |

**Score 6–8:** HOT — create AgentMail draft immediately
**Score 4–5:** WARM — add to Notion, draft when batch is ready
**Score 1–3:** COLD — skip or save for future niche test

---

### Phase 4: STORE (Notion CRM)

Create/update a Notion database with these properties:

| Property | Type | Values |
|----------|------|--------|
| Name | Title | Contact full name |
| Company | Text | Practice/firm/agency name |
| Niche | Select | Dental / Law / Real Estate |
| Email | Email | Verified email |
| Phone | Phone | Direct line if available |
| Website | URL | Company website |
| Score | Number | 1–8 qualification score |
| Status | Select | Discovered / Qualified / Drafted / Sent / Replied / Booked / Closed |
| City | Text | City, State |
| Growth Signal | Text | Job posting, new location, etc. |
| Notes | Text | ICP-specific intel |
| Draft ID | Text | AgentMail draft ID once created |
| Created | Date | Auto |

Use `notion-create-pages` to add leads, `notion-update-page` to advance status.

---

### Phase 5: DRAFT (AgentMail outreach)

Use `mcp__AgentMail__create_draft` with inbox `adai-b2b@agentmail.to`:

Personalization rules:
- Always reference a specific pain point from their ENRICH data
- Use city/location in the opening if you have it
- For dental: mention insurance if tech stack shows no clearinghouse
- For law: name the practice area if known (PI firms vs family law have different hooks)
- For RE: reference their lead volume estimate if available from ZipRecruiter/Apollo

**DRAFT ONLY — Never send without Nathan's explicit GO.**

After creating the draft, update the Notion lead's `Draft ID` and set `Status = Drafted`.

---

### Phase 6: FOLLOW-UP (Day 3, 7, 14)

Gmail labels to track pipeline:
- `B2B Leads/Cold` — awaiting Nathan's send approval
- `B2B Leads/Sent` — approved and sent
- `B2B Leads/Replied` — response received → move to HOT
- `B2B Leads/Booked` — discovery call scheduled via Calendly

For high-score leads (7–8): use Twilio SMS as supplementary channel on Day 5 if no email reply.

---

## Shorthand Setup

```bash
BSRC="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/b2b-sourcing/scripts/source_leads.py"
```

### Commands

```bash
# Discover + qualify 10 leads for a niche in a city
$BSRC discover --niche dental --city "Chicago, IL" --count 10

# Discover + enrich + score (requires HUNTER_API_KEY for email verification)
$BSRC enrich --niche law --city "Chicago, IL" --count 5

# Full pipeline: discover → enrich → score → create Notion records
$BSRC pipeline --niche real-estate --city "Chicago, IL" --count 10 --output notion

# Export leads from Notion to CSV for Instantly import
$BSRC export --niche dental --status qualified --format csv
```

---

## Daily Sourcing Target

| Niche | Daily Goal | Weekly Goal |
|-------|-----------|-------------|
| Dental | 5 qualified | 25 |
| Law | 5 qualified | 25 |
| Real estate | 5 qualified | 25 |
| **Total** | **15/day** | **75/week** |

At 40 emails/day capacity (Instantly limit), hit 75 new qualified leads/week to keep pipeline full.

---

## Rules

1. **DRAFT ONLY** — Never send any outreach without Nathan's explicit "GO."
2. **3-STRIKE RULE** — If a sourcing tool fails 3 times, stop and report to Nathan.
3. **VERIFY FIRST** — Always verify the decision-maker's name and email before drafting.
4. **NO DSO/CHAIN** — For dental, skip multi-location chains; they have internal IT.
5. **SCORE BEFORE DRAFT** — Minimum score of 4 before creating a draft. Don't waste quota on cold 1s.
6. **TWILIO LAST** — SMS only as Day 5 follow-up, never as first touch.
