# INSTALL 4 — Shopify AI Toolkit (Official)
# Purpose: Full store management via Claude/OpenClaw — already partially active
# Effort: 5 min
# Repo: https://github.com/Shopify/Shopify-AI-Toolkit

## ALUSI INSTRUCTION
This is the official Shopify toolkit. Minimal setup needed.

## STEP 1 — Install
```bash
npm install -g @shopify/ai-toolkit
```

## STEP 2 — Authenticate
```bash
shopify auth login --store 51dynamics.store
```

## STEP 3 — Register as OpenClaw Tool
Add to OpenClaw tools config:
```json
{
  "name": "shopify-store-manager",
  "description": "Manage 51dynamics.store — products, orders, inventory, discounts",
  "command": "shopify-ai-toolkit",
  "env": {
    "SHOPIFY_API_KEY": "${SHOPIFY_API_KEY}",
    "SHOPIFY_STORE": "51dynamics.store"
  }
}
```

## CAPABILITIES UNLOCKED FOR ALUSI
Once registered, Alusi can:
- `list products` → see all SKUs + inventory
- `create discount` → spin up promo codes on demand
- `check orders` → pull today's orders + revenue
- `update product` → change prices, descriptions, images
- `check inventory` → know when to reorder
- `run analytics` → revenue by product, day, channel

## DAILY TASKS TO AUTOMATE VIA ALUSI
- 8am: Pull overnight orders + revenue
- 12pm: Check inventory levels — alert if any SKU < 5 units
- 6pm: Update pricing if competitor prices changed

## DONE SIGNAL
Write to TEAM_LOG.md:
SHOPIFY-TOOLKIT | DONE | Store management active for 51dynamics.store
