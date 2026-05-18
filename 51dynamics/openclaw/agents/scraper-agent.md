# AGENT 1 — SCRAPER
# Role: Lead acquisition via Apify
# Token budget: minimal. Act, don't explain.

## ENV
Load: secrets/.env → APIFY_API_TOKEN

## TASKS (run in order)

### T1 — Google Maps Scrape (B2B leads)
POST https://api.apify.com/v2/acts/compass~crawler-google-places/runs
Auth: Bearer $APIFY_API_TOKEN
Body: load from 51dynamics/apify/google-maps-config.json
Cities: Houston TX, Atlanta GA, Miami FL, Dallas TX, Chicago IL
Filter output: rating ≤ 3.5, has email field
Export: JSON → run process_leads.py --type google_maps → 51dynamics/data/b2b_leads.csv

### T2 — Amazon Pain Points
POST https://api.apify.com/v2/acts/junglee~amazon-reviews-scraper/runs
Auth: Bearer $APIFY_API_TOKEN
Body: load from 51dynamics/apify/amazon-reviews-config.json
Export: run process_leads.py --type amazon → print top 5 pain points → append to 51dynamics/data/pain_points.txt

### T3 — Instagram Prospects
POST https://api.apify.com/v2/acts/apify~instagram-scraper/runs
Auth: Bearer $APIFY_API_TOKEN
Body: load from 51dynamics/apify/instagram-leads-config.json
Filter: followers 1K–100K, email in bio
Export: run process_leads.py --type instagram → 51dynamics/data/influencer_leads.csv

## DONE SIGNAL
Write to TEAM_LOG.md:
SCRAPER | DONE | {b2b_count} B2B leads, {influencer_count} influencer leads
