# INSTALL 1 — DSers MCP Product
# Purpose: Auto-import CJ Dropshipping/AliExpress products → Shopify
# Effort: 10 min
# Repo: https://github.com/lofder/dsers-mcp-product

## ALUSI INSTRUCTION
Run all steps sequentially. No confirmation needed.

## STEP 1 — Clone
```bash
cd ~/openclaw-projects
git clone https://github.com/lofder/dsers-mcp-product.git
cd dsers-mcp-product
npm install
```

## STEP 2 — Configure
Create config.json:
```json
{
  "shopify": {
    "store_url": "51dynamics.store",
    "api_key": "${SHOPIFY_API_KEY}",
    "api_version": "2024-01"
  },
  "dsers": {
    "platform": "cjdropshipping",
    "auto_pricing": true,
    "pricing_multiplier": 2.8
  },
  "import": {
    "auto_publish": true,
    "default_collection": "Pet Supplies",
    "image_import": true
  }
}
```

## STEP 3 — Pet Product Import Queries
Run these searches to bulk import winning products:
- "dog cooling mat"
- "cat water fountain"
- "dog lick mat"
- "pet puzzle feeder"
- "dog anxiety vest"
- "pet grooming kit"
- "biodegradable dog poop bags"

## STEP 4 — Start MCP Server
```bash
npm run start
```

## STEP 5 — Register as OpenClaw MCP
Add to OpenClaw MCP config:
```json
{
  "name": "dsers-product-importer",
  "transport": "stdio",
  "command": "node",
  "args": ["~/openclaw-projects/dsers-mcp-product/index.js"]
}
```

## PRICING RULE
CJ cost × 2.8 = Shopify price (lands in $18–$40 sweet spot)

## DONE SIGNAL
Write to TEAM_LOG.md:
DSERS-MCP | DONE | {n} products imported to Shopify
