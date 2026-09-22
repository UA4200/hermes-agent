# OpenClaw Free LLM Platform — Workstream 2: Root Cause Analysis

**Evidence class:** LIVE_VERIFIED — every claim below traces to a specific
file read or command run against `ugos-mac-mini` this session (see
`CURRENT_AI_ENVIRONMENT.md`), not inference from names or the program brief.

## Headline: the premise was wrong. Nothing "failed to become operational."

The brief asked to determine why Intelligent Routing / Freeway LLM / Free
Claude Code "never became operational." Direct investigation found **two
real, actively-used routing implementations handling real traffic**, plus
two genuinely dormant experiments. The actual problem is **duplication**,
not absence — which is exactly what this program's own constraints already
warn against ("Do NOT: Duplicate orchestration logic across products").

## The Two Real, Active Systems

### Path A — Interactive Claude Code CLI sessions
```
claude CLI (ANTHROPIC_BASE_URL=127.0.0.1:4100, set globally in .zshrc + ~/.claude/settings.json)
  → oe-proxy (oe_proxy.py, pm2, port 4100)
    → adaptive_router.py
      → call_freeway()   [requires FREEWAY_API_KEY]
      → call_ollama()
      → call_anthropic_direct()
      → call_openai_direct()
```
`adaptive_router.py` is the most sophisticated piece found in this review:
a `RouterState` class tracks per-provider success rate, latency, and health
over time; `rank_candidates()`/`score_candidate()` pick a route adaptively
rather than from a fixed chain. This is a real, working system — Free-Way
is one of its backends, not an orphaned dependency.

### Path B — Autonomous agent layer (Telegram/Discord "Alusi")
```
alusi-gateway (pm2, port 8788, FastAPI)
  → natural_response()
    → ai_router.py (6 fixed tiers: local → haiku → gpt-mini → sonnet → opus → gpt4o)
      → call_ollama() / call_haiku() / call_sonnet() / call_opus() / call_gpt()
```
Policy-driven (`model_policy.json`), 22 task types mapped to 11 named
chains, real governance fields (`no_hidden_bypass_routes`,
`daily_hard_limit_usd`). **179,725 real logged calls**, 43% routed to local
Ollama at $0 cost — this system works and is actively cost-optimizing
today.

**Root cause of the apparent "failure":** these two systems were built
independently (different sessions, different points in time — `oe_proxy.py`'s
own comment says "v2: Replaced hardcoded Groq-first chains with
adaptive_router," confirming at least one prior rewrite), never merged, and
nothing routes CLI-originated work through the bot's cost policy or vice
versa. Anyone auditing "the" routing system by looking at only one path
would reasonably conclude the other is missing or broken — that is most
likely how this program's brief was drafted.

## Two Genuinely Dormant Systems

| System | Status | Evidence |
|---|---|---|
| `model-cost-gateway` (port 4110) | Built, tested, **never wired into either real path** | `logs/ledger.jsonl` is almost entirely synthetic smoke-test rows (`agent_id: "tst"`, `project_id: "smoke"`); last entry 2026-09-16; neither `ai_router.py` nor `adaptive_router.py`/`oe_proxy.py` reference port 4110 anywhere |
| `native-router` (port 4010) | **Abandoned after one day of testing** | `logs/native_router/events.jsonl` has exactly 5 entries, all dated 2026-07-30 (the same day as the original Phase 0 screenshot session) and none since, despite running in pm2 for ~2 months since |

These are not "failures" in the sense of broken code — both start cleanly
and would work if called. They're **unadopted prototypes**, most likely
superseded by `adaptive_router.py`'s later, more capable design, and never
formally decommissioned.

## Real Defects Found (Distinct From the Duplication Issue)

1. **Silent Postgres logging failure in `ai_router.py`.** `_get_db()`
   connects to a `openclaw` role/database that was never provisioned
   (`psql: FATAL: role "openclaw" does not exist`). `_log_db()`'s blanket
   `except: pass` means this has never raised a visible error in the
   system's entire operating history. The JSONL fallback (179,725 rows) is
   the only real record of usage — any tool or dashboard built to query
   Postgres for cost data has been silently getting nothing.
2. **A live API key exposed in plaintext logs.** `native-router`'s error
   log captured a full request URL — including the Gemini API key as a
   query parameter — when a 429 response was logged. **This key should be
   rotated**; the value itself is not reproduced in this report or repo.
   Root cause: logging the raw exception message (which includes the full
   request URL) instead of sanitizing it before writing to a log file that
   isn't access-restricted beyond normal file permissions.
3. **pm2 restart-count false positives.** The July snapshot flagged 4
   processes as concerning based on restart count alone. Direct log
   inspection (this session) confirms all 4 are working exactly as
   designed: two are scheduled poll-and-exit jobs (`blco-email-monitor`,
   cadence `WEEKDAY_3X_WEEKLY`), two are approval-gated status reporters
   that intentionally run-report-exit (`open-empire-federation-staging`,
   `open-empire-lifecycle-staging`, both `"health": "green"`,
   `"approval_required": true`). Root cause of the false alarm: pm2's
   restart counter doesn't distinguish "crashed" from "exited
   successfully, scheduled to run again" — a monitoring/observability gap,
   not an application defect.
4. **Ollama MLX library failure (minor).** Every `ollama` invocation logs
   `Failed to load MLX dynamic library ... libmlxc.dylib`. Functions
   correctly without it (falls back to non-accelerated inference); real
   but low-severity — worth fixing if this Mac Mini is Apple Silicon (not
   yet confirmed either way this pass — `sw_vers` doesn't report chip
   architecture; would need `uname -m` or `sysctl -n machdep.cpu.brand_string`).

## What This Means for the Rest of This Program

- **Workstream 4 (Platform Architecture)** should design around
  *consolidating* Path A and Path B's routing logic into one shared
  library — `adaptive_router.py`'s design (adaptive, health-aware) is the
  stronger foundation; `ai_router.py`'s policy file (task-type → chain
  mapping, governance fields) is the more complete *policy* layer. The
  target architecture combines adaptive_router's mechanism with
  ai_router's policy.
- **Workstream 7 (Freeway Rebuild)** is retitled by evidence: Free-Way
  itself needs no rebuild — it's a healthy, actively-used dependency of
  `adaptive_router.py`. The real Workstream 7 work is deciding whether to
  formally retire `model-cost-gateway` and `native-router` (recommended:
  yes, after confirming nothing external depends on ports 4110/4010) or
  finish integrating them.
- **Workstream 9 (AI Orchestration Capability)** is well-justified by real
  evidence, not speculative: two independent, non-communicating routing
  systems is precisely the "duplicate orchestration logic across products"
  this program's own constraints forbid continuing.
- The two real defects (§ Postgres role, § leaked key) should be fixed
  regardless of what else this program decides, and are low-risk,
  high-value fixes to do early.

## Confidence and Limits

Every claim above traces to a file read or command executed live against
the Mac Mini this session — no benchmark or usage number was estimated or
assumed. Not yet verified: whether anything besides the `claude` CLI
environment variable points at `oe-proxy`/port 4100 (e.g., could n8n
workflows or another automation also call it — not checked this pass);
whether `economic_guard.py`, `groq_rotator.py`, `fcc_router.py` (also
present in the `router/` directory) are live dependencies of
`adaptive_router.py` or further dormant experiments — flagged for
Workstream 4's architecture review to resolve before finalizing the target
design.
