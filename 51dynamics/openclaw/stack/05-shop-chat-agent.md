# INSTALL 5 — Shop Chat Agent (Customer Support)
# Purpose: 24/7 autonomous customer support on 51dynamics.store
# Effort: 15 min
# Repo: https://github.com/Shopify/shop-chat-agent

## ALUSI INSTRUCTION
Run all steps sequentially. No confirmation needed.

## STEP 1 — Clone + Install
```bash
cd ~/openclaw-projects
git clone https://github.com/Shopify/shop-chat-agent.git
cd shop-chat-agent
npm install
```

## STEP 2 — Configure for 51-Dynamics
Create .env:
```env
SHOPIFY_STORE_URL=51dynamics.store
SHOPIFY_STOREFRONT_TOKEN=${SHOPIFY_STOREFRONT_TOKEN}
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
AI_MODEL=claude-haiku-4-5-20251001
STORE_NAME=51-Dynamics Pet Store
SUPPORT_EMAIL=info@51dynamics.store
```

## STEP 3 — Train on Pet Store Context
Create context/store-info.md:
```
Store: 51-Dynamics Pet Store
URL: 51dynamics.store
Niche: Premium pet accessories — dogs and cats
Shipping: 5–10 business days (dropship from CJ)
Returns: 30-day return policy
Discount: PETLOVE20 for 20% off (new customers)
RETURN10 for 10% off (returning customers)
Top products: cooling mats, water fountains, lick mats,
             grooming kits, puzzle feeders, anxiety vests
Questions to escalate to human: refunds over $50, damaged goods
```

## STEP 4 — Deploy to Shopify
```bash
npm run deploy -- --store 51dynamics.store
```

## STEP 5 — Add Chat Widget to Shopify
Shopify Admin → Online Store → Themes → Customize
→ Add Section → App Embeds → Shop Chat Agent → Enable

## CHAT AGENT HANDLES AUTOMATICALLY
- "Where is my order?" → pulls tracking from Shopify
- "What's your return policy?" → answers from context
- "Do you have X product?" → searches store catalog
- "Can I get a discount?" → offers RETURN10 code
- Product recommendations → suggests based on pet type

## DONE SIGNAL
Write to TEAM_LOG.md:
CHAT-AGENT | DONE | 24/7 support live on 51dynamics.store
