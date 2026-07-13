# UGC CONTENT CALENDAR — 51-Dynamics Pet Store
# 7 posts/week. Platform: TikTok (primary) + X (repurposed) + IG/FB (queued pending META_ACCESS_TOKEN)
# Model: Haiku (scheduling) → Sonnet (script/caption) → SadTalker + Coqui (video production)

---

## WEEK 1 CONTENT PLAN (Starting July 14, 2026)

### POST 1 — Monday (Store Launch)
**Platform:** TikTok + X  
**Format:** Text/graphic post  
**Hook:** "We just launched 51-Dynamics and your pets are going to love what we built 🐾"  
**Caption:**
```
51-Dynamics is LIVE.

Premium pet products. Fast shipping. Real care.

Use code PETLOVE20 for 20% off your first order 👇
51dynamics.store

#PetStore #PetLovers #DogMom #CatMom #NewStore #Pets #PetProducts
```
**CTA:** Shop link in bio → 51dynamics.store

---

### POST 2 — Tuesday (Product Spotlight: Best-Selling Bed)
**Platform:** TikTok + X  
**Format:** Product video/image  
**Hook:** "POV: Your dog finally has the bed they deserve 🛏️"  
**Caption:**
```
The orthopedic pet bed that has thousands of 5-star reviews.

Your dog spends 12-14 hours/day sleeping.
They deserve this.

Shop: 51dynamics.store
Code: PETLOVE20 (20% off, limited time)

#DogBed #OrthopedicBed #DogMom #PetComfort #51Dynamics
```

---

### POST 3 — Wednesday (Educational: Pet Health Tip)
**Platform:** TikTok + X  
**Format:** Text carousel or talking-head video  
**Hook:** "3 signs your pet needs a vet that most owners miss 👀"  
**Caption:**
```
Most pet owners miss these early warning signs:

1. Drinking more water than usual
2. Sudden change in energy level
3. Eating less for 2+ days in a row

If you see these — vet visit, not "wait and see."

We built 51-Dynamics because your pet's health matters.
Shop: 51dynamics.store

#PetHealth #DogHealth #CatHealth #PetCare #VetTips
```
**Note:** Education builds trust → drives store credibility

---

### POST 4 — Thursday (Customer/Pet UGC Repost)
**Platform:** TikTok + X  
**Format:** Repost user photo or "tag us for a feature"  
**Hook:** "Tag us in your pet photos for a chance to be featured 🐶🐱"  
**Caption:**
```
We want to see your pets! 🐾

Tag @51Dynamics or use #51Dynamics in your pet photos.

Best post each week gets featured + a discount code.

Shop our store: 51dynamics.store

#PetPhoto #ShowMeYourPet #DogOfInstagram #CatsOfTikTok #51Dynamics
```

---

### POST 5 — Friday (Discount Reminder)
**Platform:** TikTok + X  
**Format:** Graphic or short video  
**Hook:** "Code PETLOVE20 expires soon — here's what pet owners are buying"  
**Caption:**
```
Top 3 things pet parents are grabbing at 51-Dynamics:

1. 🛏️ Orthopedic dog beds (dogs sleep 14hrs/day — they deserve it)
2. 🎾 Interactive puzzle toys (bye bye boredom)
3. 💊 Omega-3 supplements (coat + joint support)

20% off with PETLOVE20 👇
51dynamics.store

#PetProducts #PetDeals #DogMom #CatMom #51Dynamics
```

---

### POST 6 — Saturday (Behind the Scenes / Brand Story)
**Platform:** TikTok + X  
**Format:** Story-style text or short video  
**Hook:** "Why we built a pet store from scratch (honest story)"  
**Caption:**
```
51-Dynamics started because we couldn't find pet products that were:

✓ Actually high quality
✓ Reasonably priced
✓ Shipped fast

So we built the store we wished existed.

Every product is hand-selected. Every order matters.

Visit us: 51dynamics.store

#BrandStory #PetStore #PetCommunity #SmallBusiness #51Dynamics
```

---

### POST 7 — Sunday (Engagement/Poll)
**Platform:** TikTok + X  
**Format:** Poll post or question  
**Hook:** "Dog parent or cat parent? (Important debate)"  
**Caption:**
```
Settle it once and for all:

🐶 Dog parent
🐱 Cat parent

Comment below — we're building our next product drop around YOUR vote.

Shop: 51dynamics.store
Code: PETLOVE20 (20% off)

#DogsVsCats #PetDebate #DogMom #CatMom #51Dynamics #PetLovers
```

---

## POSTING SCHEDULE

| Day | Time (CDT) | Platform | Status |
|-----|-----------|----------|--------|
| Mon | 7:00 PM | TikTok + X | Queued |
| Tue | 6:00 PM | TikTok + X | Queued |
| Wed | 12:00 PM | TikTok + X | Queued |
| Thu | 8:00 PM | TikTok + X | Queued |
| Fri | 5:00 PM | TikTok + X | Queued |
| Sat | 10:00 AM | TikTok + X | Queued |
| Sun | 3:00 PM | TikTok + X | Queued |
| IG/FB | All | Meta | Pending META_ACCESS_TOKEN |

---

## VIDEO PRODUCTION PIPELINE (When SadTalker + Coqui are installed)

```
Script (Sonnet) 
  → Voice (Coqui TTS — clone Nathan's voice from 30s sample)
  → Lip sync (SadTalker — avatar video)
  → Caption overlay (FFmpeg auto-captions)
  → Upload (TikTok API + X API)
  → Queue (meta-queue.md for IG/FB)
```

**Mac Mini command (after install):**
```bash
# Generate voice
tts --text "POV: Your dog finally has the bed they deserve" \
    --model_name tts_models/en/vctk/vits \
    --speaker_idx p225 \
    --out_path /tmp/post1_audio.wav

# Generate video with SadTalker
cd ~/openclaw-projects/SadTalker
python inference.py \
    --driven_audio /tmp/post1_audio.wav \
    --source_image ~/hermes-agent/assets/avatar.jpg \
    --result_dir ~/hermes-agent/ugc-output/
```

---

## METRICS TO TRACK (weekly)

| Metric | Week 1 Target | Month 1 Target |
|--------|--------------|----------------|
| TikTok followers | 50 | 500 |
| TikTok views/post | 200 | 2,000 |
| X impressions | 500 | 5,000 |
| Store clicks from social | 25 | 250 |
| Conversions from social | 1 | 10 |
