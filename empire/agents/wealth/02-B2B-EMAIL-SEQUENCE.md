# ADAI INC — B2B Cold Email Sequence (4 Emails)
# Purpose: Convert healthcare IT / SaaS / ops leads into discovery calls
# Model: Haiku (personalization lookup) → Sonnet (write/edit)
# Rules: DRAFT ONLY — never send without Nathan's approval

---

## EMAIL 1 — Cold Outreach (Day 0)

**Subject:** Cut your {COMPANY} AI implementation time by 60%

Hi {FIRST_NAME},

I noticed {COMPANY} is scaling fast in {INDUSTRY} — congrats on the recent {GROWTH_SIGNAL}.

Most {ROLE}s I talk to are dealing with the same bottleneck: their team is spending 15–20 hours/week on tasks that AI can handle in minutes. We've helped companies like yours automate {PAIN_POINT} and redeploy that time into revenue-generating work.

ADAI INC builds custom AI automation systems. No fluff — we map your exact workflow, identify the 3 highest-ROI automation opportunities, and deliver a working system within 30 days.

Would a 20-minute call this week make sense? I'll share the exact framework we used to help {SIMILAR_COMPANY} reduce manual work by 70%.

Nathan | ADAI INC  
Founder, AI Automation Agency  
calendly.com/ugoasiegbu

P.S. If timing's off, I'm happy to send the case study first — just say the word.

---
VARIABLES: {FIRST_NAME} {COMPANY} {INDUSTRY} {ROLE} {GROWTH_SIGNAL} {PAIN_POINT} {SIMILAR_COMPANY}

---

## EMAIL 2 — Follow-Up (Day 3, no reply)

**Subject:** Re: Cut your {COMPANY} AI implementation time by 60%

Hi {FIRST_NAME},

Just bumping this up — wanted to make sure it didn't get buried.

Quick question: what's the ONE process at {COMPANY} that eats the most of your team's time right now?

I ask because in the last 6 months, the answer to that question has almost always pointed directly to the automation we build first — and it tends to deliver results within the first 30 days.

Still happy to do a 20-minute call. No pitch, just a mapping session.

Nathan | ADAI INC  
calendly.com/ugoasiegbu

---
VARIABLES: {FIRST_NAME} {COMPANY}
SEND: Day 3 after Email 1, no reply

---

## EMAIL 3 — Case Study (Day 7, no reply)

**Subject:** What happened when {SIMILAR_COMPANY} automated their {PAIN_POINT}

Hi {FIRST_NAME},

I wanted to share a quick example that might be relevant to {COMPANY}.

A {INDUSTRY} company similar to yours was spending ~18 hours/week manually {PAIN_POINT}. Their team was good at it — but it wasn't the best use of their time.

We built a custom AI system in 3 weeks that:
- Cut 18 hours down to under 2 hours/week
- Reduced errors by 94%
- Freed their team to focus on {HIGH_VALUE_ACTIVITY}

They hit ROI in week 5.

I think we could do something similar for {COMPANY}. Would 20 minutes this week work?

Nathan | ADAI INC  
calendly.com/ugoasiegbu

---
VARIABLES: {FIRST_NAME} {COMPANY} {INDUSTRY} {PAIN_POINT} {HIGH_VALUE_ACTIVITY} {SIMILAR_COMPANY}
SEND: Day 7 after Email 1, no reply

---

## EMAIL 4 — Break-Up (Day 14, no reply)

**Subject:** Closing the loop — {FIRST_NAME}

Hi {FIRST_NAME},

I've reached out a few times — I don't want to keep showing up in your inbox if the timing isn't right.

I'll close this out on my end. If AI automation ever becomes a priority at {COMPANY}, I'm one message away.

One last thing: if there's a specific reason this wasn't a fit, I'd genuinely appreciate knowing — it helps me improve who I reach out to.

Either way, best of luck with {COMPANY} this year.

Nathan | ADAI INC

---
VARIABLES: {FIRST_NAME} {COMPANY}
SEND: Day 14 after Email 1, no reply
ACTION: Move to ADAI EMPIRE/B2B Leads/Closed after sending

---

## SEQUENCING RULES

| Email | Day | Trigger | Gmail Label |
|-------|-----|---------|-------------|
| #1 Cold | 0 | Lead qualified | B2B Leads/Cold |
| #2 Follow-up | +3 | No reply to #1 | B2B Leads/Cold |
| #3 Case Study | +7 | No reply to #1 | B2B Leads/Cold |
| #4 Break-up | +14 | No reply to #1 | B2B Leads/Cold |
| — | Any | Reply received | B2B Leads/Replied → Hot |

## PERSONALIZATION DATA (Haiku pulls before Sonnet writes)
- {GROWTH_SIGNAL}: recent funding, new hire surge, product launch, award
- {PAIN_POINT}: manual reporting, lead qualification, invoice processing, data entry
- {HIGH_VALUE_ACTIVITY}: sales, client delivery, product development
- {SIMILAR_COMPANY}: anonymize or use "a healthcare IT firm we worked with"

## VOLUME TARGET
- 40 emails/day, weekdays only
- Apollo.io for healthcare IT / SaaS 10–500 employees
- Hunter.io for email verification before send
- Instantly.ai ($37/mo) for sequencing OR n8n self-hosted
