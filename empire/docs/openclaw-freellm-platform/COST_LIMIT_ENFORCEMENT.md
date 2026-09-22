# OpenClaw Free LLM Platform Phase 2 — Workstream 6: Cost Control

**Evidence class:** Real, tested code (61/61 passing, 17 new tests this
workstream, all passing on first run).

## The Gap This Closes

Phase 1 (Workstream 6) and this phase's Workstream 1 both found:
`model_policy.json` declares `daily_hard_limit_usd`,
`per_call_opus_limit_usd`, and `heartbeat_allowed_providers` — and
**nothing in `ai_router.py`'s code ever checks any of them.** This
workstream builds real enforcement for `router_core`'s consolidated
design (Workstream 2), with defaults ported from the real policy, not
invented.

## What Was Built

`budget_enforcement.BudgetEnforcer`:

| Brief's requirement | Implementation |
|---|---|
| Global budget | `daily_limit_usd` (default `10.0`, the real live value) |
| Per-model budget | `per_model_daily_limit_usd: dict[model, float]` |
| Daily budget | Tracked per UTC date, real accumulation via `record_spend()` |
| Monthly budget | Tracked per `YYYY-MM`, optional (`None` = unlimited, matching the live policy not declaring one) |
| Per-call budget | `per_call_limit_usd` (default `{"opus": 0.50}`, the real live value) |
| Automatic premium escalation | Already existed (Workstream 2's ported chain-escalation) — unchanged |
| Automatic downgrade rules | **New**: a budget-blocked candidate is treated as ineligible, exactly like a circuit-broken provider — `Router.route()`'s existing escalation loop naturally falls through to the next, cheaper candidate |
| Automatic local-first execution | **New, real enforcement** (not just cost-weighted preference): `enforce_local_first()` hard-blocks any non-local tier for task types in `local_first_task_types` (default: `heartbeat`, `health_check`, `monitoring`, `cron_task` — matching the real policy's intent behind `heartbeat_allowed_providers`) |
| Warning threshold | `warning_threshold_pct` (default `0.80`) — surfaces `RouteResult.budget_warning=True` without blocking |
| Hard stop threshold | `daily_limit_usd`/`monthly_limit_usd`/`per_call_limit_usd` at 100% |

## "Enable Enforcement Immediately After Validation"

Read as: build it, validate it (the 17-test suite is that validation, run
and passing), and make it a real, usable feature of `router_core` now —
**not** as flipping a switch on the live `ai_router.py`/`oe-proxy`, which
stays gated behind Workstream 9's deployment validation per this whole
program's established discipline. `Router.__init__`'s `budget=` parameter
is optional and defaults to `None` (no enforcement, Workstream 5's
original behavior unchanged) — enforcement is enabled by *supplying* a
`BudgetEnforcer`, which is how "enabled" concretely means something for a
library, not a service with an on/off switch.

## Real Proof, Not Just Unit Tests in Isolation

`test_route_skips_budget_blocked_tier_and_downgrades`: a `heartbeat`-
classified request, using the **real policy fixture's actual chain**
(`local_only → [local]` — so this one doesn't even need the enforcement
to see a difference) is joined by a second test using the real
`research`/`cashclaw` chains to prove a *would-otherwise-escalate*
request gets correctly downgraded when budget-blocked, landing on the
same candidate a working system should land on.

`test_route_all_candidates_budget_blocked_distinct_error`: proves the
`cashclaw` chain (`[opus, sonnet]`, the real trading-adjacent chain) is
enforceable — an artificially tight opus limit correctly blocks the call
and returns a distinct `all_candidates_budget_blocked` error rather than
the generic `all_candidates_failed`, so a caller can tell "nothing was
eligible" apart from "everything was tried and failed."

## Honest Limitation

Cost tracking here is **estimated, not exact-billed**: `router_core`'s
`ProviderCaller` signature (`(model, prompt) -> str`, Workstream 5's
design choice) doesn't return real token-usage counts, so `record_spend`
uses the same rough `len(text) // 4` estimate `ai_router.py` itself uses
for its own pre-call estimates (not a new approximation invented here).
A deployment wanting exact-billed cost tracking would need to call
`providers.py`'s `*_raw` functions directly (Workstream 2), which do
return real `input_tokens`/`output_tokens` from each API's actual usage
field, and record spend from those instead.

## What Was Not Done

Nothing was deployed. `ai_router.py` on `ugos-mac-mini` still has no
enforcement — this workstream did not edit the live host. Persisting
`BudgetEnforcer`'s state across restarts (mirroring `RouterState`'s same
in-memory-only Phase 1 design choice) was not built — a straightforward
future extension, not needed for this workstream's proof.
