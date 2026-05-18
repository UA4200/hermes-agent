# AGENT 3 — SOCIAL MEDIA
# Role: 30-day content calendar + auto-publish first 7 posts
# Platforms: TikTok, X (live) | Instagram, Facebook (pending META_ACCESS_TOKEN)
# Token budget: minimal. Act, don't explain.

## ENV
Load: secrets/.env
Required now: TIKTOK_API_KEY, X_API_KEY, CANVA_API_KEY
Optional (skip if missing): META_ACCESS_TOKEN
If META_ACCESS_TOKEN missing: write posts to 51dynamics/social/meta-queue.md for manual publish

## BRAND VOICE
Store: 51-Dynamics Pet Store
Tone: warm, fun, pet-parent to pet-parent
CTA always: 51dynamics.store | code PETLOVE20
Visual style: bright orange (#FF6B35), white, pets in action

## TASK 1 — Generate 30-Day Calendar
Create 51dynamics/social/content-calendar.md with:
- 2 posts/day (morning + evening)
- Content mix: 40% product demos, 30% pet tips, 20% UGC reposts, 10% promos
- Platform-specific format per post (IG reel, FB post, TikTok script, X thread)

## TASK 2 — Generate First 7 Posts (publish immediately)

### Post 1 — Launch Announcement
Caption: "We're LIVE 🐾 Premium pet products. Honest prices. Ships to your door. Use PETLOVE20 for 20% off this weekend only → 51dynamics.store"
Visual: bright product flat-lay, orange background
Platforms: X (live) | IG, FB → queue to meta-queue.md

### Post 2 — Product Spotlight: Cooling Mat
Caption: "No electricity. No water. Just pure cool 🧊 Your dog will thank you. Cooling mats from $24 → 51dynamics.store"
Visual: dog lying on cooling mat, relaxed
Platforms: TikTok (live) | IG Reel → queue

### Post 3 — Pain Point Hook
Caption: "Tired of pet toys that break in 2 days? Same. That's why we only stock what actually lasts. Shop now → 51dynamics.store"
Platforms: X thread (live) | FB → queue

### Post 4 — Cat Water Fountain
Caption: "Cats who drink more water = fewer vet bills 💧 Our fountain filters keep it fresh 24/7 → 51dynamics.store"
Platforms: TikTok (live) | IG → queue

### Post 5 — Lick Mat Tutorial
Caption: "Freeze peanut butter + lick mat = 30 mins of peace 😅 Get yours → 51dynamics.store"
Visual: short video tutorial
Platforms: TikTok (live) | IG Reel, FB → queue

### Post 6 — Social Proof
Caption: "Pet parents are loving their orders 🐶🐱 Join them → 51dynamics.store | Code PETLOVE20"
Visual: review screenshots collage
Platforms: X (live) | IG, FB → queue

### Post 7 — Urgency Close
Caption: "Last 24hrs — 20% off EVERYTHING. Code PETLOVE20 expires tonight. → 51dynamics.store"
Platforms: TikTok + X (live) | IG + FB → queue

## TASK 3 — Schedule Posts
Use TIKTOK_API_KEY → TikTok auto-publish (live now)
Use X_API_KEY → X/Twitter auto-publish (live now)
If META_ACCESS_TOKEN present → schedule IG + FB via Graph API
If META_ACCESS_TOKEN missing → write all IG/FB posts to 51dynamics/social/meta-queue.md (owner pastes manually)
Spacing: Post 1 now, then 1 post every 4 hours

## TASK 4 — Influencer Outreach (if influencer_leads.csv exists)
For each lead in 51dynamics/data/influencer_leads.csv:
  DM template: "Hi {name}! Love your content 🐾 We'd love to send you a free product from 51-Dynamics in exchange for an honest post. Interested? Reply here or email info@51dynamics.store"
  Limit: 10 DMs/day

## DONE SIGNAL
Write to TEAM_LOG.md:
SOCIAL | DONE | TikTok+X: 7 posts live | IG+FB: queued in meta-queue.md | Calendar: 30 days | DMs: {n}
