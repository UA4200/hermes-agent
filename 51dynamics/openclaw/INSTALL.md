# How to Activate on OpenClaw (Mac Mini)

## Step 1 — Add API keys to secrets/.env
```
APIFY_API_TOKEN=
INSTANTLY_API_KEY=
SHOPIFY_API_KEY=
META_ACCESS_TOKEN=
TIKTOK_API_KEY=
X_API_KEY=
CANVA_API_KEY=
SLACK_WEBHOOK=
```

## Step 2 — Copy this folder to your OpenClaw workspace
cp -r 51dynamics/openclaw ~/.openclaw/projects/51dynamics/

## Step 3 — Load SOUL.md as your agent's system prompt
In OpenClaw: /agent new --soul ~/.openclaw/projects/51dynamics/SOUL.md

## Step 4 — Trigger PMO Council
Tell Alusi: "Execute ALUSI_PMO_INSTRUCTION.md now"

## Step 5 — Monitor
Alusi will post daily digests and write to TEAM_LOG.md
Check: ~/.openclaw/projects/51dynamics/TEAM_LOG.md

## Optional — Pull Extra Skills
/skill install hesreallyhim/awesome-claude-code
/skill install travisvn/awesome-claude-skills
/skill install alirezarezvani/claude-skills
