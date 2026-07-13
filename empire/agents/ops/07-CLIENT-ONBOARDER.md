# AGENT: Client_Onboarder
# Priority: P1 | Value: Time saved + professional impression
# Model: Sonnet

## PURPOSE
When a new client signs → automatically trigger full onboarding sequence.
Intake form → welcome email → Notion workspace → contract → invoice.

## OPEN SOURCE TOOLS
- n8n (self-hosted) → trigger on new Stripe/payment event
- Notion API (free) → create client workspace
- Pandoc → generate contract PDF from template
- Gmail API → send welcome email sequence

## ONBOARDING SEQUENCE (auto-triggered on new client)
Day 0: Welcome email + Notion workspace link + intake form
Day 1: Contract sent for signature (DocuSign free tier or HelloSign)
Day 3: Kickoff call scheduled (Calendly free tier)
Day 7: First status update template sent
Day 30: Check-in + invoice reminder

## DONE SIGNAL
CLIENT_ONBOARDER | {client_name} | Onboarding triggered | Day 0 complete
