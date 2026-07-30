# 00_CURRENT_STATE_REPORT — Phase 0 Mac Mini Evidence
**Generated:** 2026-07-30  
**Source:** 5 terminal screenshots from `neoOC@ugos-mac-mini`  
**Evidence class:** LOCAL_VERIFIED (photos of live terminal)

---

## SYSTEM IDENTITY

| Field | Value |
|---|---|
| Hostname | ugos-mac-mini |
| SSH user | neoOC |
| OS | macOS 12.7.6 (Monterey) — Build 21H1320 |
| Python | 3.14.x (exact patch unclear from screenshot) |
| Node | v24.18.0 |

---

## OPENCLAW / HERMES CLI

| Item | Status | Detail |
|---|---|---|
| `openclaw` | ✅ INSTALLED | v2026.7.1 (2d2dddc4) at `/usr/local/bin/openclaw` |
| `hermes` CLI | ❌ NOT FOUND | "hermes not found" — `openclaw` IS the installed alias |
| openclaw.json | ⚠️ CONFLICTED | Multiple clobbered backups (see below) |

**openclaw.json conflict history** (all present in home/openclaw dir):
- `openclaw.json` — 4281 bytes (active)
- `openclaw.json.bak.1` through `.bak.4` — multiple generations
- `openclaw.json.clobbered.2026-05` — multiple versions
- `openclaw.json.last-good`
- `openclaw.json.pre-hardening`
- `openclaw.json.pre-update`
- `openclaw.json.pre_discord_fix.b`

→ **Config was clobbered at least 4 times in May 2026.** The `last-good` snapshot exists and is the recovery anchor.

---

## GIT REPO STATE

| Repo | Branch | Status |
|---|---|---|
| hermes-agent | `claude/summarize-weekly-calendar-b6rlm` | ✅ HEAD matches remote (`cd7c0ea8`) |
| open-empire-ros | — | ❌ NOT FOUND at `~/open-empire-ros` |

**hermes-agent recent commits visible on Mac Mini:**
- `cd7c0ea8` Fix X API credentials: use X_BEARER_TOKEN, X_API_KEY
- `0f8a1392` Update social agent: META optional, TikTok+X proceed immediately
- `05751979` Add OpenClaw multi-agent PMO system for 51-Dynamics
- `95b049ab` Add 51-Dynamics lead gen system: Apify configs, processing script

→ The Mac Mini is **on the correct branch and up to date** with remote.

---

## LOCAL CODEBASE (home directory — `~/`)

This is far larger than the GitHub repo. The home dir contains 100+ production Python scripts running locally:

### Active Alusi Agents
- `alusi_loop.py` — main agent loop
- `alusi_loop.py.bak_*` — backup copies
- `alusi_multi_agent_bus.py` — inter-agent messaging
- `alusi_telegram_control.py` — Telegram control plane
- `alusi_telegram_conversational.py` — conversational interface
- `alusi_discord_operator.py` — Discord integration
- `alusi_dream_engine.py` — (14KB — significant)
- `alusi_unified.py`
- `alusi_backlog_reporter.py` — (14KB, updated Jul 30)

### Revenue / Deal Engines
- `blco_deal_state.py`
- `blco_engine.py`
- `blco_followup_engine.py`
- `blco_message_engine.py`
- `blco_regenerate_drafts.py`
- `hybrid_deal_engine.py` — updated Jul 30
- `revenue_engine.py`
- `revenue_engine_ai_patch.py`
- `enrichment_engine.py`

### Infrastructure / Control
- `load_secrets.py` — 14KB (large — handles all secret loading)
- `secrets_manager.py`
- `controlled_task_executor.py`
- `task_executor.py`
- `signal_sourcer.py`
- `discord_alusi_live.py` — updated Jul 30
- `approved_email_dispatcher.py`
- `backlog_multi_agent_dispatcher.py`
- `inject_230.py` — 9.6KB
- `model_router.py`
- `native_router`
- `deliverability_policy.py` — updated Jul 30

### Key Directories Present
`agents/` `antfarm/` `api-wrappers/` `backups/` `bin/` `blco/` `brain/` `briefings/` `cache/` `canvas/` `cashclaw/` `claude/` `claude-code-skills/` `config/` `connectors/` `council/` `cron/` `dashboards/` `data/` `debug/` `devices/` `discord/` `empire/` `enrichment/` `etc/` `execution_engine/` `external-resources/` `final_health_check.py` `flows/` `gateway/` `grafana/` `hooks/` `identity/` `infrastructure/` `intelligence/` `llm_fabric/` `logs/` `memory/` `migration/` `mission-control/` `npm/` `observability/` `runtime/` `scripts/` `secrets/` `security/` `session-delivery-queue/` `shared/` `skills/` `staging/` `state/` `subagents/` `supabase/` `tasks/` `telegram/` `telemetry/` `tmp/` `tools/` `trading/` `vault/` `ventures/` `wiki/` `workspace/` `workspaces/`

---

## SECRETS / ENV FILES

| File | Location | Modified | Risk |
|---|---|---|---|
| `.env` | `~/.openclaw/` or `~/` | Jul 30 05:36 | ⚠️ Exists — confirm location |
| `secrets.env` | `~/secrets.env` | present | ⚠️ Exists |
| `secrets/` | `~/secrets/` dir | present | Review contents |
| `load_secrets.py` | `~/load_secrets.py` | May 16 | Central secret loader |

**ACTION REQUIRED:** Confirm `.env` and `secrets.env` are NOT committed to any repo.  
These files hold values; only variable names should ever appear in git history.

---

## PM2 STATUS

Not captured cleanly. The `#` comment in the Phase 0 script caused `zsh: command not found: #`.  
**Next action:** Run `pm2 list` directly (no comment prefix) to see what processes are managed.

---

## PORT LISTENERS

Not captured — same `zsh: command not found: #` issue cut off the lsof output before results printed.  
**Next action:** Run `lsof -iTCP -sTCP:LISTEN -nP 2>/dev/null | head -30` directly.

---

## CRITICAL GAPS

| # | Gap | Severity | Action |
|---|---|---|---|
| G1 | `open-empire-ros` NOT FOUND at `~/open-empire-ros` | 🔴 P0 | Find repo: `find ~ -maxdepth 4 -name "empire-ros" -o -name "open-empire-ros" 2>/dev/null` |
| G2 | `openclaw.json` clobbered 4+ times | 🔴 P0 | Diff `openclaw.json` vs `openclaw.json.last-good` before any config changes |
| G3 | `hermes` CLI not found (only `openclaw`) | 🟡 P1 | hermes-agent setup.sh creates this symlink — run `setup-hermes.sh` to install |
| G4 | pm2 process list unknown | 🟡 P1 | Run `pm2 list` to understand what's currently live |
| G5 | Port listeners unknown | 🟡 P1 | Run `lsof -iTCP -sTCP:LISTEN -nP 2>/dev/null | head -30` |
| G6 | Home dir has 100+ production scripts not in GitHub | 🟠 P1 | Map what is local-only vs what should be in repo |

---

## PHASE 0 VERDICT

**OpenClaw is live and current.** The Mac Mini is operational with `openclaw v2026.7.1` installed and the correct branch checked out.

**The home directory is a full production empire** — not just the hermes-agent repo. Hundreds of Python files, engines, bots, and agents exist locally that have no GitHub counterpart yet. This is the "Mega Block" artifact referenced in the directive.

**Immediate safe actions authorized:**
```bash
# Fix the comment-causes-error issue — run these without # prefix:
pm2 list
lsof -iTCP -sTCP:LISTEN -nP 2>/dev/null | head -30

# Find open-empire-ros:
find ~ -maxdepth 4 -type d \( -name "open-empire-ros" -o -name "empire-ros" \) 2>/dev/null

# Check openclaw.json config conflict:
diff ~/openclaw.json ~/openclaw.json.last-good 2>/dev/null | head -50

# Verify hermes symlink setup:
cd ~/hermes-agent && bash setup-hermes.sh
```

**NOT authorized yet:** CRON-SETUP.sh, MEMORY-SETUP.sh, any `openclaw run` tasks, or sending any communications. Held pending Phase 8 gates.

---

## WORKSTREAM MAPPING (from Directive)

| WP | Component | Evidence State | Action |
|---|---|---|---|
| WP-01 | hermes-agent branch | GITHUB_VERIFIED ✅ | Merge when P1 resolved |
| WP-07 | open-empire-ros integration | MISSING ❌ | Find repo (G1 above) |
| WP-09 | openclaw config | CONFLICTED ⚠️ | Diff last-good vs active |
| WP-10 | Local production scripts | LOCAL_VERIFIED | Map to GitHub |
| WP-15 | Secrets handling | DOCUMENTED_ONLY | Confirm .env not committed |
| WP-16 | Cron / memory infra | GITHUB_VERIFIED | Held pending Phase 8 |

---

*Next report: `01_PM2_PROCESS_MAP.md` after running `pm2 list` directly.*
