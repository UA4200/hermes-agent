# 51-Dynamics Lead Generation Playbook
## Apify + Email Campaign System

---

## Overview

Three parallel lead streams feeding one email campaign engine.

```
Stream 1: Google Maps → B2B pet store owners (wholesale leads)
Stream 2: Amazon Reviews → Pain point mining (email copy fuel)
Stream 3: Instagram → Micro-influencer outreach (free PR)
         ↓
   process_leads.py
         ↓
    leads.csv
         ↓
  Instantly.ai / Apollo.io
         ↓
  Email sequences fire automatically
```

---

## Step-by-Step Setup

### Step 1 — Apify Account
1. Go to apify.com → Create free account
2. Free tier = $5 credits/month (enough for ~500 leads)
3. Paid = $49/mo for unlimited

### Step 2 — Run Google Maps Scraper
1. Apify Console → Search "Google Maps Scraper" (by Compass)
2. Paste config from `apify/google-maps-config.json`
3. Run one city at a time (e.g. "pet store, Houston, TX")
4. Export results as JSON
5. Run: `python scripts/process_leads.py --input results.json --type google_maps --output leads.csv`

### Step 3 — Run Amazon Reviews Scraper
1. Apify Console → Search "Amazon Reviews Scraper" (by Junglee)
2. Paste config from `apify/amazon-reviews-config.json`
3. Export results as JSON
4. Run: `python scripts/process_leads.py --input reviews.json --type amazon`
5. Note the top pain points printed to terminal → use in email subject lines

### Step 4 — Load Leads into Email Tool
**Recommended: Instantly.ai**
1. Sign up at instantly.ai ($37/mo)
2. Connect info@51dynamics.store as sending account
3. Warm up email for 14 days before blasting (auto setting in Instantly)
4. Import leads.csv
5. Load sequence from `email-sequences/b2b-pet-store-sequence.md`
6. Set daily limit to 40 emails/day
7. Launch

### Step 5 — Track Results
| Metric | Target |
|---|---|
| Open rate | >40% |
| Reply rate | >5% |
| Conversion to call | >2% |
| Deals closed | 1 per 100 leads |

---

## Revenue Model from B2B Leads

One pet store owner placing monthly wholesale orders:
- 20 products × $15 avg margin = $300/order
- 2 orders/month = $600/month per client
- 10 clients = $6,000/month recurring

Cost to acquire: ~$86/mo (Apify + Instantly)
**ROI: 70x at 10 clients**

---

## Files in This Folder

| File | Purpose |
|---|---|
| `apify/google-maps-config.json` | Scrape low-rated pet stores |
| `apify/amazon-reviews-config.json` | Extract competitor pain points |
| `apify/instagram-leads-config.json` | Find micro-influencer emails |
| `scripts/process_leads.py` | Clean + filter scraped data |
| `email-sequences/b2b-pet-store-sequence.md` | 5-email B2B sequence + 3-email consumer sequence |
