# ADAI Empire — Tool Stack & OSS Alternatives
# Rule: Always prefer a free/self-hosted OSS alternative before paying for a SaaS tool.
# Every paid tool below has a working GitHub replacement Alusi should try first.

---

## OSS-FIRST POLICY

Before adding any paid SaaS tool to the empire stack, check this list.
If a working OSS alternative exists and can run on the Mac Mini (or a cheap VPS):
- Self-host it instead.
- Use the paid version ONLY if scale or reliability makes self-hosting impractical.
- All OSS alternatives listed here are actively maintained GitHub repos.

---

## B2B SOURCING

### Web Scraping / Crawling

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| Firecrawl (paid tier) | $16+/mo | **Firecrawl OSS** | `mendableai/firecrawl` | Exact same API, Docker self-host. Use paid only if credit volume exceeds what self-host can handle |
| Apify | $49/mo | **Crawlee** | `apify/crawlee` | Same team, open-source crawler framework. Write custom actors |
| ScrapingBee | $49/mo | **Playwright** | `microsoft/playwright` | Built-in headless browser, already installed in Alusi's env |
| Diffbot | $299/mo | **Trafilatura** | `adbar/trafilatura` | Python library for article + contact extraction |

### Web Search

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| Tavily (paid tier) | $20+/mo | **SearXNG** | `searxng/searxng` | Self-hosted privacy meta-search, aggregates Google/Bing/DDG. Docker in 5 min |
| Brave Search API (paid) | $3+/mo | **SearXNG** | `searxng/searxng` | Same — use free Brave tier (2k/mo) first, fall back to SearXNG |
| Google Custom Search | $5/1k | **SearXNG** | `searxng/searxng` | Free |

### Email Finding / Verification

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| Hunter.io | $34/mo | **theHarvester** | `laramies/theHarvester` | OSINT tool, finds emails from domain + public sources |
| Hunter.io | $34/mo | **EmailFinder** | `Josue87/EmailFinder` | Finds pattern emails by name + domain |
| Clearbit Enrich | $99+/mo | **Wappalyzer** | `wappalyzer/wappalyzer` | Tech stack detection (replaces Clearbit tech data) |
| ZoomInfo | $500+/mo | **Apollo free tier** | apollo.io | Use Apollo free before paying for ZoomInfo |

### CRM / Contact Storage

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| HubSpot CRM | $45+/mo | **Twenty** | `twentyhq/twenty` | Modern open-source CRM, Postgres-backed, active dev |
| Salesforce | $150+/mo | **Twenty** | `twentyhq/twenty` | Full CRM with pipelines and contacts |
| Airtable | $20+/mo | **NocoDB** | `nocodb/nocodb` | Airtable clone, connects to Postgres/MySQL/SQLite |
| Notion (paid) | $16+/mo | **AFFiNE** | `toeverything/AFFiNE` | Open-source Notion alternative |

---

## EMAIL OUTREACH / SEQUENCING

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| Instantly.ai | $37/mo | **Listmonk** | `listmonk/listmonk` | Self-hosted email campaigns, high deliverability |
| Instantly.ai | $37/mo | **Mautic** | `mautic/mautic` | Full marketing automation — sequences, scoring, CRM |
| Lemlist | $50/mo | **Mautic** | `mautic/mautic` | Same |
| Mailchimp | $13+/mo | **Listmonk** | `listmonk/listmonk` | Listmonk is simpler + faster for plain outreach |
| SendGrid | $20+/mo | **Postal** | `postalserver/postal` | Self-hosted email server with full analytics |
| Mailgun | $15+/mo | **Postal** | `postalserver/postal` | Same |

---

## SCHEDULING / CALENDAR

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| Calendly (paid) | $12+/mo | **Cal.com** | `calcom/cal.com` | Full Calendly replacement, self-hostable, free cloud tier |
| Acuity | $20/mo | **Cal.com** | `calcom/cal.com` | Same |

---

## AUTOMATION / WORKFLOWS

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| Zapier | $20+/mo | **n8n** | `n8n-io/n8n` | Most powerful OSS automation platform, MCP-native |
| Make (Integromat) | $9+/mo | **n8n** | `n8n-io/n8n` | Same |
| ActivePieces | freemium | **n8n** | `n8n-io/n8n` | n8n is more powerful |
| Retool | $10+/mo | **Appsmith** | `appsmithorg/appsmith` | Internal tool builder |

---

## ANALYTICS / TRACKING

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| Google Analytics | free (privacy) | **Plausible** | `plausible/analytics` | Privacy-first, self-hostable |
| Google Analytics | free (privacy) | **Umami** | `umami-software/umami` | Simpler alternative |
| Mixpanel | $25+/mo | **PostHog** | `PostHog/posthog` | Full product analytics, self-hostable |
| Hotjar | $32+/mo | **OpenReplay** | `openreplay/openreplay` | Session replay + heatmaps, self-hostable |

---

## AI / LLM INFRASTRUCTURE

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| OpenAI API | usage | **Ollama** | `ollama/ollama` | Run LLMs locally (Llama 3, Mistral, Phi-3) — use for low-stakes tasks |
| Claude API | usage | **Ollama** | `ollama/ollama` | Ollama for cheap/fast tasks; Claude for high-stakes reasoning |
| LangChain | freemium | **LlamaIndex** | `run-llama/llama_index` | OSS RAG framework |
| Pinecone | $70+/mo | **Qdrant** | `qdrant/qdrant` | Self-hosted vector DB — Docker in 2 min |
| Pinecone | $70+/mo | **Chroma** | `chroma-core/chroma` | Simpler vector DB for smaller scale |
| Weaviate | $25+/mo | **Qdrant** | `qdrant/qdrant` | Same |

---

## CONTENT / MEDIA

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| Canva (paid) | $13/mo | **Penpot** | `penpot/penpot` | OSS design tool, Figma/Canva alternative |
| Adobe | $55+/mo | **Penpot** | `penpot/penpot` | Same |
| Descript | $24/mo | **Whisper** | `openai/whisper` | OSS transcription (same quality as paid tools) |
| ElevenLabs | $22/mo | **Coqui TTS** | `coqui-ai/TTS` | OSS text-to-speech, voice cloning |
| Synthesia | $67/mo | **SadTalker** | `OpenTalker/SadTalker` | OSS talking head video generation |

---

## E-COMMERCE / SHOPIFY SUPPLEMENTS

| Paid Tool | Cost | OSS Replacement | GitHub | Notes |
|-----------|------|----------------|--------|-------|
| Klaviyo | $45+/mo | **Listmonk** | `listmonk/listmonk` | Email automation for Shopify stores |
| Gorgias | $10+/mo | **Chatwoot** | `chatwoot/chatwoot` | OSS customer support platform |
| Tidio | $29/mo | **Chatwoot** | `chatwoot/chatwoot` | Live chat + chatbot |
| ReCharge | % of GMV | **Medusa.js** | `medusajs/medusa` | OSS commerce infrastructure with subscriptions |

---

## CURRENT EMPIRE STACK — PAID VS FREE

| Tool | Current Status | Monthly Cost | Action |
|------|---------------|-------------|--------|
| Tavily | MCP connected, free tier | $0 | Keep — upgrade only if search volume exceeds free limits |
| Brave Search | MCP connected, free tier (2k/mo) | $0 | Keep — use SearXNG if volume exceeds 2k |
| Firecrawl | Being set up | $0 (500 free) | Self-host `mendableai/firecrawl` via Docker when credits run out |
| Apollo.io | Free tier | $0 | Keep free; upgrade to $49/mo only when sending 40+ emails/day consistently |
| AgentMail | Free tier | $0 | Keep |
| Notion | Connected | $0–$16 | Consider NocoDB if paid tier needed |
| Calendly | Free tier | $0 | Use Cal.com self-host if paid features needed |
| Shopify | Active | ~$39/mo | Required — no OSS equivalent at scale |
| Stripe | Active | % of revenue | Required — standard payment infra |
| Twilio | Usage-based | $0.0079/SMS | Required — no OSS equivalent for SMS delivery |
| Instantly.ai | NOT YET | $37/mo | Use Listmonk first before paying |
| Hunter.io | NOT YET | $34/mo | Use theHarvester first |
| Apollo paid | NOT YET | $49/mo | Delay until 40 emails/day volume proven |

---

## ALUSI'S OSS-FIRST RULES

1. **Before recommending any paid tool** — check this file first for a free/OSS alternative.
2. **For scraping** — try Firecrawl free credits → self-host `mendableai/firecrawl` → only then consider paid.
3. **For search** — use Brave (2k free) + Tavily (free tier) first → SearXNG self-host if volume is high.
4. **For email sequences** — use Listmonk or n8n before Instantly.ai or Lemlist.
5. **For CRM** — use Notion (already connected) or Twenty (OSS) before HubSpot.
6. **For email finding** — use theHarvester (free, OSINT) before Hunter.io.
7. **For vector storage** — use Qdrant or Chroma (self-hosted) before Pinecone.
8. **For local AI tasks** — use Ollama (local) before calling Claude/OpenAI API to save costs.
9. **Always Docker-first** — if a tool has a Docker image, spin it up before signing up for SaaS.
10. **Report savings** — when an OSS tool replaces a paid one, log the monthly saving to Cost Guard.
