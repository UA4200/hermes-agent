# AGENT 2 — EMAIL CAMPAIGN
# Role: Load leads, launch sequences in Instantly.ai
# Dependency: waits for 51dynamics/data/b2b_leads.csv from Scraper Agent
# Token budget: minimal. Act, don't explain.

## ENV
Load: secrets/.env → INSTANTLY_API_KEY, SMTP credentials for info@51dynamics.store

## PRE-CHECK
- Confirm b2b_leads.csv exists and has >0 rows
- Confirm email warm-up period ≥ 14 days (check Instantly dashboard)
- If warm-up < 14 days: log warning to TEAM_LOG.md, proceed anyway with 20/day limit

## TASKS

### T1 — Create Campaign (B2B)
POST https://api.instantly.ai/api/v1/campaign/create
Name: "51D-B2B-PetStores-{date}"
From: info@51dynamics.store
Daily limit: 40
Schedule: Mon–Fri 8am–11am local
Sequence: load from 51dynamics/email-sequences/b2b-pet-store-sequence.md (Emails 1–5)
Tracking: opens=true, clicks=true

### T2 — Upload Leads
POST https://api.instantly.ai/api/v1/lead/add
Source: 51dynamics/data/b2b_leads.csv
Map fields: name→firstName, email→email, rating→custom1, top_complaint→custom2

### T3 — Create Campaign (Consumer)
Name: "51D-Consumer-Launch-{date}"
From: info@51dynamics.store
Daily limit: 50
Sequence: load Emails A–C from b2b-pet-store-sequence.md
Tag: launch_promo

### T4 — Launch Both Campaigns
POST https://api.instantly.ai/api/v1/campaign/launch
Campaigns: B2B + Consumer

## DONE SIGNAL
Write to TEAM_LOG.md:
EMAIL | DONE | B2B:{lead_count} leads loaded, Consumer:{count} | Both campaigns live
