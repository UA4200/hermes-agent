# INSTALL 2 — Shopify AI Agent
# Purpose: Auto order processing + customer emails + follow-up scheduling
# Effort: 15 min
# Repo: https://github.com/jarif87/shopify-ai-agent

## ALUSI INSTRUCTION
Run all steps sequentially. No confirmation needed.

## STEP 1 — Clone + Install
```bash
cd ~/openclaw-projects
git clone https://github.com/jarif87/shopify-ai-agent.git
cd shopify-ai-agent
pip install -r requirements.txt
```

## STEP 2 — Environment Config
Create .env from secrets:
```env
SHOPIFY_STORE_URL=51dynamics.store
SHOPIFY_API_KEY=${SHOPIFY_API_KEY}
SHOPIFY_API_SECRET=${SHOPIFY_API_SECRET}
GMAIL_ADDRESS=info@51dynamics.store
GMAIL_APP_PASSWORD=${GMAIL_APP_PASSWORD}
GOOGLE_CALENDAR_ID=${GOOGLE_CALENDAR_ID}
AI_API_KEY=${ANTHROPIC_API_KEY}
AI_MODEL=claude-sonnet-4-6
```

## STEP 3 — Customize Email Templates
Edit templates/order_confirmation.txt:
```
Subject: Your 51-Dynamics order is confirmed! 🐾

Hi {customer_name},

Thank you for your order! Your pet supplies are being prepared.

Order: #{order_number}
Items: {items}
Estimated delivery: {delivery_date}

Track your order: {tracking_url}

Questions? Reply to this email or visit 51dynamics.store

— 51-Dynamics Team
```

Edit templates/followup.txt:
```
Subject: How is {first_product} working for {pet_name}? 🐶

Hi {customer_name},

It's been 7 days since your order arrived. We'd love to know how
your pet is enjoying their new {first_product}!

Leave a quick review → {review_url}
Shop again → 51dynamics.store | Code RETURN10 for 10% off

— 51-Dynamics Team
```

## STEP 4 — Run as Background Service
```bash
nohup python main.py &
```

## STEP 5 — Schedule via OpenClaw
Tell Alusi: "Check shopify-ai-agent status every hour and restart if down"

## AUTOMATIONS ACTIVE AFTER INSTALL
- New order → confirmation email within 2 min
- Order shipped → tracking email auto-sent
- 7 days post-delivery → review request email
- Customer reply → AI responds using Claude

## DONE SIGNAL
Write to TEAM_LOG.md:
SHOPIFY-AGENT | DONE | Order automation live, email templates configured
