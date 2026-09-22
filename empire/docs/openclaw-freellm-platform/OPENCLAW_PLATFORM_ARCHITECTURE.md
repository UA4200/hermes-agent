# OpenClaw Free LLM Platform — Workstream 4: Platform Architecture

**Status:** Proposal, not executed. This workstream produces a target
design and a staged migration plan. Nothing in this document has been
applied to `ugos-mac-mini` — it's a live production system with real
trading (`cashclaw_arb`, `trading_sentinel`, `polymarket-trader`) and
revenue automation running on it today; consolidating its two working
routing paths is real surgery and should happen in stages with
verification at each step, not as a single sweeping change. Where a fix
is low-risk enough to execute directly, it's called out explicitly as
such and held for your go-ahead rather than applied unasked.

## Why Not the Brief's Reference Architecture, Literally

The brief's reference stack (`Claude Code → LiteLLM Gateway → Intelligent
Router → Capability Router → Task Classification → Local Models → Optional
Premium Models → Fallback Layer → EOS Runtime`) assumes LiteLLM as the
gateway layer. Workstream 3 confirmed: **this system has never used
LiteLLM** — `adaptive_router.py` and `ai_router.py` are both bespoke
Python, and that appears to be a deliberate choice (no LiteLLM config,
install, or reference found anywhere on the host), not an oversight.
Introducing LiteLLM now would mean *three* routing implementations instead
of consolidating two down to one. The architecture below keeps the proven
bespoke-Python approach and focuses on merging what already exists, per
this program's own constraint: "Do NOT: Duplicate orchestration logic
across products."

## Target Architecture

```
                    ┌─────────────────────────────┐
                    │      router_core (NEW)        │
                    │  unified library, importable   │
                    │  by any caller on this host     │
                    ├─────────────────────────────┤
                    │ Engine:  adaptive_router.py's  │
                    │   RouterState (health/success-  │
                    │   rate tracking) + score/rank   │
                    │ Policy:  ai_router.py's         │
                    │   model_policy.json (task-type   │
                    │   → chain mapping, governance     │
                    │   fields, cost limits)            │
                    │ Cache:   GPTCache (semantic,      │
                    │   fronts local_only task types)   │
                    │ Compress: LLMLingua (fronts       │
                    │   high_value/paramount tier        │
                    │   calls only — where cost is       │
                    │   highest)                          │
                    │ Backends: Ollama (KV cache          │
                    │   q8_0), Free-Way (BYOK free-tier), │
                    │   Anthropic direct, OpenAI direct   │
                    └───────────┬─────────────┬──────┘
                                │             │
                    ┌───────────▼──┐   ┌──────▼────────────┐
                    │ oe-proxy      │   │ alusi-gateway      │
                    │ (CLI path,    │   │ (bot path, port    │
                    │  port 4100)   │   │  8788)              │
                    └───────────────┘   └────────────────────┘
```

**What changes:** both entry points call the *same* `router_core` library
instead of each having their own routing engine. **What doesn't change:**
the two entry points themselves (`oe-proxy`, `alusi-gateway`) — their
request/response shapes, ports, and callers are untouched, so this is an
internal consolidation, not a caller-facing breaking change.

## Decisions on Existing Components

| Component | Decision | Basis |
|---|---|---|
| `adaptive_router.py` | **Promote** — becomes `router_core`'s engine | More sophisticated (health/success-rate scoring) than `ai_router.py`'s fixed chains |
| `ai_router.py`'s `model_policy.json` | **Promote** — becomes `router_core`'s policy file | More complete governance (task-type mapping, cost limits, `no_hidden_bypass_routes`) than `adaptive_router.py` currently has |
| `ai_router.py` (the module itself) | **Retire** after `alusi-gateway` is migrated to call `router_core` | Its logic gets absorbed into the policy above; the module becomes a thin compatibility shim during migration, then deleted |
| Free-Way | **Keep, unchanged** | Real, healthy, actively used by `adaptive_router.py`'s `call_freeway()` |
| Ollama | **Keep**, add `OLLAMA_KV_CACHE_TYPE=q8_0` | Low-risk, free memory/context win (Workstream 3) |
| `model-cost-gateway` | **Retire** | Never wired into either real path; ledger is synthetic-only (Workstream 2) |
| `native-router` | **Retire** | 5 test events total, abandoned since 2026-07-30 (Workstream 2) |
| `economic_guard.py`, `groq_rotator.py`, `fcc_router.py` | **Audit individually before retiring** | Confirmed not imported by `adaptive_router.py`/`oe_proxy.py` (Workstream 2/3), but not yet checked for use elsewhere (e.g. a cron job calling them directly) — do not delete until confirmed orphaned |
| `hermes-agent`'s `AIAgent`/`prompt_caching.py`/`context_compressor.py` | **Do not migrate onto it this pass** — flagged as a future option, not this program's scope | Real potential benefit (Workstream 3) but migrating the live agent onto a different execution model is a much larger, higher-risk change than consolidating two routers that already share the same call shape. Worth its own future program, not bundled into this one. |

## Two Low-Risk Fixes, Held for Your Go-Ahead

These were found in Workstream 2, are narrow, reversible, and don't touch
the routing consolidation above — but I'm not executing them without
confirmation, since they touch a live production host:

1. **Create the missing `openclaw` Postgres role/database** so
   `ai_router.py`'s existing (already-written, already-called) `_log_db()`
   path starts working instead of silently no-op'ing. Alternative: since
   the JSONL fallback has worked fine for 179,725 calls, an equally valid
   fix is to **delete the dead Postgres code path** instead of provisioning
   a database for it — simpler, one less service to maintain. Your call.
2. **Rotate the Gemini API key** found exposed in `native-router`'s
   plaintext error log (Workstream 2). This is independent of everything
   else in this program and shouldn't wait for it.

## Migration Stages (once approved)

1. Build `router_core` as a new module, unit-tested standalone, **not yet
   called by anything live**.
2. Point `oe-proxy` at `router_core` (lower-traffic, interactive path —
   easier to verify a mistake quickly). Run both old and new in parallel
   behind a feature flag if `oe_proxy.py`'s structure allows it; otherwise
   a clean cutover with immediate rollback (`git revert` + `pm2 restart`)
   ready.
3. Verify for a defined period (propose: 48 hours) before touching the
   bot path.
4. Point `alusi-gateway` at `router_core`, same verify-before-proceed
   discipline. **This path touches `cashclaw`/trading-adjacent task types
   via the `cashclaw` chain — verify those specific chains behave
   identically before and after**, given real money is downstream.
5. Retire `ai_router.py`, `model-cost-gateway`, `native-router` only after
   step 4 is confirmed stable.

## Capability-First / No Vendor Lock-In Check

- Local-first preserved: `local_only`/`ollama_first`/`cheap` chains still
  route to Ollama before any paid provider, unchanged from today's policy.
- No new paid-only dependency introduced: GPTCache and LLMLingua are both
  MIT/permissive, self-hosted, no API keys required.
- Free-Way (multi-provider BYOK) remains the free-tier path — not
  replaced by a single-vendor alternative.
