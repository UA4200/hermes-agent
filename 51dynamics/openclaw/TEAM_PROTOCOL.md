# TEAM PROTOCOL — 51-Dynamics PMO Council

## Rules
- No agent messages another agent directly — all coordination via TEAM_LOG.md
- Each agent completes its task then writes one line to TEAM_LOG.md: AGENT_NAME | STATUS | METRIC
- Sub-agents have no memory — every prompt is self-contained
- Prefer action over confirmation — credentials are in secrets/.env

## Shared Glossary
- LEAD: pet store owner with email, rating ≤ 3.5, from Google Maps scrape
- PROSPECT: Instagram pet influencer with >1K followers and public email
- SEQUENCE: 5-email B2B drip or 3-email consumer drip
- SKU: any product listed on 51dynamics.store

## Escalation Path
Agent → TEAM_LOG.md → Alusi reviews → PMO decision

## Credentials Location
All API keys: secrets/.env
Keys needed: APIFY_API_TOKEN, INSTANTLY_API_KEY, SHOPIFY_API_KEY, X_BEARER_TOKEN, X_API_KEY, X_API_SECRET, META_ACCESS_TOKEN, TIKTOK_API_KEY, CANVA_API_KEY
