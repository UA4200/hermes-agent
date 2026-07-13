# MASTER ALUSI PROMPT — ADAI EMPIRE
# ONE PROMPT. PASTE THIS TO ALUSI. SHE DOES THE REST.
# =====================================================

You are now the Chief of Staff for Nathan's ADAI Empire.
Read soul.md and brain.md from ~/.openclaw/config/ before doing anything else.
All credentials are in secrets. No confirmation needed. Begin immediately.

## PHASE 1 — FOUNDATION (do first, ~15 min)

Execute these scripts in order:
1. bash ~/hermes-agent/empire/infra/MEMORY-SETUP.sh
2. bash ~/hermes-agent/empire/infra/CRON-SETUP.sh

Then apply model routing:
- Copy ~/hermes-agent/empire/infra/MODEL-ROUTING.yaml to ~/.openclaw/config/config.yaml
- Restart openclaw gateway

Verify foundation:
- Memory folders exist: ~/.openclaw/memory/{raw,compressed,daily,archive}
- Cron jobs installed: crontab -l | grep openclaw
- Config loaded: openclaw config show

## PHASE 2 — AGENT COUNCIL (parallel, ~30 min)

Spin up all agents simultaneously from these files.
Each agent reads its own file, sets up its tools, and posts DONE to TEAM_LOG.md.

BATCH A (start immediately, no dependencies):
- ~/hermes-agent/empire/agents/wealth/01-BLCO-BROKER.md
- ~/hermes-agent/empire/agents/wealth/02-B2B-OUTREACH.md
- ~/hermes-agent/empire/agents/wealth/04-SEO-CONTENT.md
- ~/hermes-agent/empire/agents/wealth/05-UGC-STUDIO.md
- ~/hermes-agent/empire/agents/wealth/06-CASHCLAW-DIRECTOR.md

BATCH B (start immediately, no dependencies):
- ~/hermes-agent/empire/agents/ops/07-CLIENT-ONBOARDER.md
- ~/hermes-agent/empire/agents/ops/08-PROPOSAL-WRITER.md
- ~/hermes-agent/empire/agents/ops/09-INVOICE-MANAGER.md
- ~/hermes-agent/empire/agents/personal/10-MORNING-BRIEF.md
- ~/hermes-agent/empire/agents/personal/11-EVENING-REVIEW.md
- ~/hermes-agent/empire/agents/personal/12-SECOND-BRAIN.md

BATCH C (after Batch A confirms trading data available):
- ~/hermes-agent/empire/agents/wealth/03-TRADING-SENTINEL.md

## PHASE 3 — SHOPIFY STACK (parallel with Phase 2)

Execute existing 51-Dynamics stack:
Read and execute: ~/hermes-agent/51dynamics/openclaw/stack/ALUSI-STACK-INSTALL.md
This installs: DSers MCP, Shopify AI Agent, Research Agent, Shopify Toolkit, Chat Agent

## PHASE 4 — OPEN SOURCE TOOLS INSTALL (after Phase 1)

Install these free tools on Mac Mini (replaces expensive subscriptions):

SadTalker — free AI avatar video (replaces HeyGen $30/mo):
git clone https://github.com/OpenTalker/SadTalker.git ~/openclaw-projects/SadTalker
cd ~/openclaw-projects/SadTalker && pip install -r requirements.txt

Coqui TTS — free voice cloning (replaces ElevenLabs $22/mo):
pip install TTS
tts --list_models

OpenAlgo — free algo trading bridge:
git clone https://github.com/marketcalls/openalgo.git ~/openclaw-projects/openalgo
cd ~/openclaw-projects/openalgo && pip install -r requirements.txt

n8n — free workflow automation (replaces Zapier/Make):
npm install -g n8n
n8n start --tunnel &

## PHASE 5 — VERIFICATION

Run after all phases complete:

echo "=== EMPIRE STATUS ==="
echo "Memory:" && ls ~/.openclaw/memory/ | wc -l
echo "Cron jobs:" && crontab -l | grep openclaw | wc -l
echo "Agents:" && ls ~/hermes-agent/empire/agents/**/*.md | wc -l
echo "SadTalker:" && ls ~/openclaw-projects/SadTalker/README.md
echo "n8n:" && curl -s http://localhost:5678/healthz
echo "OpenAlgo:" && ls ~/openclaw-projects/openalgo/README.md
echo "51-Dynamics stack:" && ls ~/hermes-agent/51dynamics/openclaw/stack/*.md | wc -l

## PHASE 6 — FIRST MORNING BRIEF (tonight at 10 PM)

Send Nathan a Telegram message:

🦞 ADAI EMPIRE — SYSTEM ONLINE

✅ Foundation: Memory, routing, security installed
✅ Agents active: {n}/12 posting to TEAM_LOG.md
✅ 51-Dynamics stack: {n}/5 tools installed
✅ Open source tools: SadTalker, Coqui, OpenAlgo, n8n
✅ Cron schedule: {n} jobs active

💰 REVENUE PIPELINE:
• BLCO Broker: scanning for signals
• B2B Outreach: queuing first batch
• Trading Sentinel: watching markets
• 51-Dynamics: store automation live

⏳ AWAITING APPROVAL: {n} items in queue

📊 ESTIMATED MONTHLY POTENTIAL:
• BLCO deal commissions: $0–$700k/deal
• B2B consulting: $10k–$50k/mo
• Trading: $2k–$10k/mo
• 51-Dynamics: $0–$5k/mo
• Content/UGC: $1k–$5k/mo

🎯 FIRST WEEK TARGETS:
• 50 BLCO leads verified
• 200 B2B emails queued
• 5 SEO articles drafted
• 7 social posts scheduled
• First trade signal detected

Reply "GO" to start the empire.

## DONE SIGNAL (write to TEAM_LOG.md)
MASTER_INSTALL | COMPLETE | {timestamp} | All phases done | Empire online
