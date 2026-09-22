# OpenClaw Free LLM Platform — Workstream 1: Current AI Environment

**Evidence class:** LIVE_VERIFIED — gathered via direct SSH to `NeoOC@ugos-mac-mini`
(`100.125.170.39`, Tailscale) during this session, not from screenshots or
assumption. Supersedes the 2026-07-30 screenshot-derived snapshot in
`00_CURRENT_STATE_REPORT.md`/`01_PM2_PROCESS_MAP.md`, which is now ~8 weeks
stale — kept as historical record, not current truth.

**Date:** 2026-09-22. **Uptime at time of inspection:** 6 days, load avg 4.5-5.5.

---

## 1. System Identity

| Field | Value |
|---|---|
| Hostname | Ugos-Mac-mini.lan (Tailscale name: `ugos-mac-mini`) |
| SSH | `NeoOC@100.125.170.39` (Tailscale IP — the MagicDNS-resolved IP, `100.104.183.39`, does NOT work from this session; use the direct IP) |
| OS | macOS 12.7.6 (Monterey), Build 21H1320 — unchanged since Phase 0 |
| Disk | 931GB total, 14GB used, 469GB available (3%) |
| Python | 3.14.6 (Homebrew, `/usr/local/Cellar/python@3.14/3.14.6`) |

**Access note:** `pm2`, `psql`, `openclaw` are not on the default non-interactive
SSH PATH — must run via `zsh -lc "..."` (login shell) to pick up the full PATH
these tools were installed under.

## 2. The Actual "Intelligent Routing" System — `ai_router.py`

This is the real answer to "does intelligent routing exist and work": **yes**,
and it is more mature than either this program's brief or the July snapshot
assumed.

- **Location:** `~/.openclaw/ai_router.py` (467 lines, last modified 2026-08-02).
- **Design:** a 6-tier escalation router — `local (Ollama) → haiku → gpt-mini →
  sonnet → opus → gpt4o` — calling each provider's native SDK directly
  (`anthropic`, `openai`, raw `requests` to Ollama's `/api/generate`), not
  through any intermediary gateway.
- **Policy-driven:** `~/.openclaw/config/model_policy.json` defines 6 cost
  tiers (with real per-token pricing), 11 named escalation chains (e.g.
  `local_only`, `cashclaw` = `[opus, sonnet]`, `ollama_first` = `[local, haiku]`),
  and a 22-entry task-type → chain mapping (`heartbeat` → `local_only`,
  `deal_strategy` → `cashclaw`, `trade_execution` → `ollama_first`, etc.).
  Includes explicit governance fields: `"external_send_requires_approval":
  true`, `"no_hidden_bypass_routes": true`, `daily_hard_limit_usd: 10.0`,
  `per_call_opus_limit_usd: 0.50`.
- **This is what the live production agent actually calls.** Traced the real
  call path: pm2's `alusi-gateway` (uvicorn, port 8788) → `alusi_gateway.py`'s
  `natural_response()` → `from ai_router import generate_text` → tier
  escalation per policy above. Not inferred — read directly from source.
- **Real usage volume (JSONL log, `~/.openclaw/memory/raw/ai_router.jsonl`):
  179,725 logged calls total.** Tier breakdown on a full scan: `local`
  (Ollama) 76,981 calls (43%, $0 cost), `haiku` 22,329 calls (12%, $0.46
  total), remainder in an older pre-tier log schema mixed into the same file
  (see §5). **This is real, substantial production traffic, actively cost-
  optimized — not an unused or abandoned system.**

## 3. Other Routing/Gateway Services Running (Parallel, Mostly Unintegrated)

pm2 currently shows **41 managed processes** (35 online, 6 stopped — see §4).
Beyond `ai_router.py`, four *additional* LLM-routing-adjacent services run
independently:

| Service | pm2 name | What it is | Actually wired into production traffic? |
|---|---|---|---|
| Free-Way | `freeway` | Real open-source project (`github.com/GoDiao/Free-Way`, MIT), installed May 2026. OpenAI/Anthropic-compatible local gateway (port 8787) for 9 free-tier providers (NVIDIA, OpenRouter, Gemini, Moonshot, DeepSeek, Cerebras, Mistral, Cohere, Groq) via BYOK. Bundles a `free-claude-code`-style proxy on port 8083 (`fcc-8083`). | **Partially.** `.freeway/usage.json` shows real (if modest) call counts across several providers — something is calling it — but nothing in `ai_router.py` or `alusi_gateway.py` references it. It's being used from somewhere else not yet traced. |
| model-cost-gateway | (part of the 41) | A well-engineered cost-enforcement overlay (port 4110): budget caps, circuit breakers, cache targets, a redacted audit ledger, daily Chicago-timezone audit reports, tested (`smoke.py`, `collect_baseline.py`, `restore.sh`/`rollback.sh`). | **No.** `logs/ledger.jsonl` contains almost entirely synthetic smoke-test rows (`agent_id: "tst"`, `project_id: "smoke"`, 4-byte prompts). Last entry 2026-09-16. No reference to it found in `ai_router.py` or `alusi_gateway.py`. Built and tested in isolation, never integrated. |
| native-router | `native-router` | A `server.py` under `~/.openclaw/native_router/`, own venv. | **Not yet traced** — running, 0 restarts, but its actual call path wasn't inspected this pass. |
| Ollama | `ollama` | Local model server. 6 models pulled ~4 months ago: `qwen2.5:3b`, `qwen2.5:1.5b`, `gemma2:2b`, `phi3:mini`, `llama3.2:3b`, `tinyllama`. | **Yes, directly** — this is what `ai_router.py`'s `local` tier calls. Logs an MLX dynamic library load failure on every invocation (`libmlxc.dylib` not found) — functions correctly, just without Apple Silicon acceleration. Real, minor, fixable issue. |

**This is the central finding of this workstream:** the system does not lack
intelligent routing — it has **at least four semi-independent
implementations of it**, of which only one (`ai_router.py`) is confirmed
wired into real production traffic. This is fragmentation, not absence.
Workstream 2 develops this into a formal root-cause analysis.

## 4. Full pm2 Process Inventory (Live, 2026-09-22)

42 processes total: 32 online, 10 stopped (`pm2 jlist`, machine-read, not
eyeballed off the table render). Selected groups (full list available via
`pm2 list` on the host):

**Trading / revenue (all online):** `cashclaw_arb`, `cashclaw_director`,
`trading_sentinel`, `polymarket-trader`, `arb-exporter`, `blco-enricher`,
`alpaca-demo`.

**Core orchestration (all online):** `alusi-gateway`, `alusi-orchestrator`,
`alusi-discord-adapter`, `alusi-controlled-worker`, `exec-gateway`, `executor`,
`heartbeat`, `mission-control`, `nexus-dashboard`, `nexus-telemetry`,
`kg-api`, `openclaw-dashboard`, `open-empire-control-plane`,
`open-empire-mission-ui`, `open-empire-nexus`, `oe-proxy`, `n8n`,
`cost-dashboard`, `hyrve-monitor-v2`.

**Routing/LLM layer (all online):** `ai_router` is not itself pm2-managed
(it's a library imported by `alusi-gateway`, not a standalone process);
`freeway`, `native-router`, `model-cost-gateway`, `claude-proxy`, `ollama`,
`fcc-8083`.

**Stopped (10, confirmed via `pm2 jlist`):** `alusi-telegram-adapter`,
`blco-email-monitor` (by design — see §5), `dynamics51` (by design — see
§5), `ecosystem.email-dispatcher`, `grafana`, `pnl-audit`, `skill-sync`,
`open-empire-federation-staging`, `open-empire-lifecycle-staging`,
`telegram-approvals`. Two are confirmed by-design (§5); the rest are open
items for Workstream 2 (§8) — not yet individually verified as broken vs.
intentionally idle.

**The one crash-loop flagged in the July report (`open-empire-missi...`,
113 restarts) is no longer in the process list** — either fixed, removed, or
renamed to `open-empire-mission-ui` (now online, 0 restarts).

## 5. "High Restart Count" ≠ "Broken" — Verified by Reading Logs, Not Assuming

The July report flagged high pm2 restart counts as a risk signal. Direct log
inspection this pass shows most are **working as designed**, not failing:

- **`blco-email-monitor`** (419 restarts, currently stopped): a scheduled
  IMAP poller with cadence `WEEKDAY_3X_WEEKLY` that exits cleanly after each
  check and gets restarted by pm2 on schedule — not a crash loop. Logs show
  consistent `"status": "OK"`, 424 zero-cost monitor runs, 0 detected
  replies (nothing to act on, not a failure).
- **`dynamics51`** (57 restarts, currently stopped): deliberately gated in
  `"active_draft_mode"` with `"approval_required": true`, `"external_actions_enabled":
  false` — waiting on a human approval of the first lead batch, not crashing.
  One historical error log shows a `KeyboardInterrupt` during Python startup
  (from a manual interruption, not an ongoing pattern).

This is a real methodological point worth carrying into every later
workstream: **pm2 restart count alone is not evidence of failure** for
processes designed to run-and-exit on a schedule or pause pending approval.
Each of the remaining stopped/high-restart processes not covered above
(`open-empire-federation-staging` 41 restarts, `open-empire-lifecycle-staging`
39 restarts) should be checked the same way — by reading logs — before
Workstream 2 treats them as defects.

## 6. Secrets / Config

- `.env`, `secrets.env`, `secrets/` all still present per Phase 0; not
  re-audited for content this pass (out of scope for read-only discovery —
  only key *names*, never values, were read: Free-Way's `.env` exposes 9
  provider key slots, `ai_router.py` reads `ANTHROPIC_API_KEY`,
  `OPENAI_API_KEY`, and Postgres credentials via env vars).
- **Real, concrete bug found:** `ai_router.py`'s Postgres cost-logging
  (`llm_usage_log` table) has been **silently failing since inception** —
  `psql -U openclaw -d openclaw` returns `FATAL: role "openclaw" does not
  exist`. The role/database was never provisioned. `_log_db()`'s broad
  `except: pass` means this has never raised a visible error; the code
  correctly falls back to the JSONL log (§2's 179,725-row file is the real
  data of record), but every dashboard or query expecting Postgres data has
  been silently getting nothing for the system's entire operating life.
- A stray, harmless directory-creation bug was found in `~/`: literal
  directories named `agents,/`, `tools,/`, `policies,/`, `memory,/`,
  `workflow,/`, `logs,/`, `}/` exist — the signature of a failed shell
  brace-expansion (`mkdir -p {agents,tools,...}` run somewhere that didn't
  expand braces). Cosmetic clutter, not a functional issue; safe to clean up
  in a later workstream, not touched here.

## 7. What This Corrects From the Program Brief

- **"Freeway LLM" is real** — it's the pm2 process name for the Free-Way
  project — and it is **not broken**; it has been running 5+ days with zero
  restarts. The brief's framing ("determine why it never became
  operational") does not match live evidence.
- **The actual routing gap is fragmentation and non-integration**, not
  absence of routing. `ai_router.py` handles real production traffic well
  (43% local, near-zero cost); three other routing-adjacent services exist
  in parallel, mostly unused.
- **A real, previously-undiagnosed bug exists**: Postgres cost-logging has
  been silently broken since the system's inception (missing DB role).

## 8. Open Items Carried to Workstream 2

1. Trace what actually calls Free-Way (something does — `usage.json` shows
   real traffic — but neither `ai_router.py` nor `alusi_gateway.py` do it).
2. Read `native-router/server.py` to determine its actual role.
3. Confirm whether `open-empire-federation-staging` /
   `open-empire-lifecycle-staging` (39-41 restarts, stopped) are
   by-design-staged or genuinely broken, the same way §5 resolved the other
   two.
4. Fix (or formally decide not to fix) the missing `openclaw` Postgres role.
