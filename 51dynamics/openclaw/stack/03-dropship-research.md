# INSTALL 3 — Dropship Product Research Agent
# Purpose: AI scrapes wholesale markets → recommends next winning pet products
# Effort: 20 min
# Repo: https://github.com/nadinev6/dropship

## ALUSI INSTRUCTION
Run all steps sequentially. No confirmation needed.

## STEP 1 — Clone + Install
```bash
cd ~/openclaw-projects
git clone https://github.com/nadinev6/dropship.git
cd dropship
npm install
```

## STEP 2 — Configure
Create .env:
```env
BRIGHT_DATA_API_KEY=${BRIGHT_DATA_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
N8N_WEBHOOK_URL=${N8N_WEBHOOK_URL}
NICHE=pet supplies
TARGET_MARGIN_MIN=0.60
PRICE_RANGE_MIN=5
PRICE_RANGE_MAX=20
OUTPUT_PATH=~/openclaw-projects/51dynamics-research/
```

## STEP 3 — Set Pet-Specific Search Targets
Edit config/niches.json:
```json
{
  "niche": "pet supplies",
  "keywords": [
    "dog accessories trending 2026",
    "cat products viral tiktok",
    "pet cooling products summer",
    "dog anxiety products",
    "eco friendly pet supplies",
    "smart pet gadgets",
    "pet dental care products"
  ],
  "sources": ["aliexpress", "cjdropshipping", "alibaba"],
  "min_orders": 500,
  "min_rating": 4.5,
  "max_cost": 15
}
```

## STEP 4 — Run Weekly Research
```bash
npm run research -- --niche "pet supplies" --output winners.json
```

## STEP 5 — Auto-Import Winners to Shopify
Connect output to DSers MCP:
If winners.json contains products with margin > 60%:
  → Pass to dsers-mcp-product for auto-import
  → Notify Alusi with product list

## SCHEDULE
Run every Monday 6am → output to TEAM_LOG.md

## DONE SIGNAL
Write to TEAM_LOG.md:
DROPSHIP-RESEARCH | DONE | {n} winning products found this week | Top pick: {product_name}
