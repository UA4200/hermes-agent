# OpenClaw Free LLM Platform Phase 2 — Workstream 10: Prioritized Remediation

**Evidence class:** Live_Verified throughout. Maps to Phase 1's
`FINAL_PRODUCT_REPORT.md`'s 5 prioritized conditions, addressed in the
order that document specified.

## Item 1 (highest priority): Does `oe-proxy` Actually Enforce a Cost Limit?

**Resolved — yes, confirmed real, by reading the actual code.** Found in
`oe_proxy.py`:
```python
if paid_required:
    req_hash = IA.request_sha256(...)
    max_cost = IA.estimated_max_cost(...)
    if max_cost > 0.05:
        return self._send({"error": {"type": "cost_limit",
            "message": "paid_request_exceeds_cost_ceiling"}}, 403)
```
A real, hard $0.05-per-request ceiling exists, gated behind
`paid_required = bool(tools) or force_paid` (where `force_paid` triggers
on any model name containing "opus"). This directly resolves Phase 2
Workstream 7's open question — that workstream correctly found the
canary's specific probe gets rejected earlier (HTTP 400
`invalid_request_error`) rather than reaching this check, but the
enforcement mechanism itself is real and present, not absent.

**One residual detail, honestly left unresolved:** why the canary's exact
probe shape triggers the earlier 400 rather than reaching this 403 path
was not fully traced — a read-only investigation into the remaining code
(past line 160 of `oe_proxy.py`) was blocked by this session's own
"Secret-Store Writes" permission gate before it could be completed
(discussed below). This doesn't change the core finding — the cost gate
is real — but the canary's own probe likely still needs updating to
actually exercise it, consistent with Workstream 7's original conclusion.

## Item 2: Implement Missing Enforcement in `ai_router.py`

**Designed, tested twice, staged — blocked from final production
deployment by this session's own "Production Deploy" permission gate.**

A minimal, purely additive patch was written (backed by `router_core`'s
already-tested design from Workstream 6): `_daily_spend` accumulator,
`_budget_block_reason()` checking `heartbeat_allowed_providers`,
`per_call_opus_limit_usd`, and `daily_hard_limit_usd` — all read from
the live policy file itself, fail-open if a field is absent. Integrated
into `generate_text()`'s existing chain loop: a blocked tier is skipped
exactly like a failed one, so escalation naturally downgrades.

**Verified, not assumed, before attempting deployment:**
1. Syntax-checked (`py_compile`) — clean.
2. Diffed against the original — purely additive (43 new lines, 1 line
   changed to add a spend-recording call), nothing removed or altered.
3. **Pure-logic tests on the live host**, real policy file, no network:
   all 6 cases correct (heartbeat/haiku blocked, heartbeat/local allowed,
   opus over/under the $0.50 ceiling, daily accumulation correctly
   blocking at the $10 boundary).
4. **Real end-to-end test on the live host**: `generate_text("...",
   task_type="heartbeat")` correctly allowed the `local` tier through
   enforcement, then correctly and gracefully handled a real Ollama
   timeout (Workstream 9's already-documented, unrelated issue) with a
   clean structured failure — no crash, no leaked exception, `cost_usd`
   stayed `0`. This proves the patch's control flow is sound even under
   a real infrastructure failure, not just in the happy path.
5. A timestamped backup of the live file was taken
   (`ai_router.py.backup_before_ws10_20260922_092414`) before any
   deployment attempt.

**Deployment itself was denied** by a distinct permission classifier
("Production Deploy") separate from the "Remote Shell Writes" gate
granted earlier this session — correctly recognizing that replacing the
live routing file real trading-adjacent bot traffic depends on is a
materially higher-risk action than a crontab edit. **Verified the live
file is unchanged** (`ls -la` shows the original Aug 2 timestamp and
byte-identical size to the backup) — the blocked `scp` did not partially
write anything. The original file, the patched file, and a clean diff
between them are committed alongside this report
(`prepared-fixes/ai_router_original.py`,
`prepared-fixes/ai_router_patched.py`,
`prepared-fixes/ai_router_ws10.diff`) for review and for whenever you
authorize the final deployment step — either by asking this session to
retry with permission granted, or by copying
`prepared-fixes/ai_router_patched.py` to
`~/.openclaw/ai_router.py` on `ugos-mac-mini` yourself (a live backup
already exists there at
`ai_router.py.backup_before_ws10_20260922_092414` for instant rollback).

## Item 3: PATH/node Bug — Done

Completed and demonstrated in Workstream 7/7b — not repeated here.

## Item 4: API Key Rotation — Explicitly Out of Scope

This phase's own Special Instructions: *"Ignore API key exposure. Assume
API keys will be rotated after migration."* Not attempted, per direct
instruction, not because it isn't real — Workstream 2 (Phase 1) still
stands as the record of that finding.

## Item 5: Postgres Role Fix or Dead-Code Removal

**Root cause fully re-confirmed and diagnosed precisely — the actual fix
was blocked before execution by this session's own "Secret-Store Writes"
gate.**

Found the exact missing piece: `~/.openclaw/secrets/.env` already has a
`CLAWDB_USER=openclaw`, `CLAWDB_DB=openclaw`, and a `CLAWDB_PASSWORD`
set — someone already provisioned the *credential*, the Postgres *role*
was simply never created to match it. Confirmed via `pg_roles` that the
connecting user (`NeoOC`) has real superuser/`CREATEROLE`/`CREATEDB`
privileges, so the fix is a straightforward `CREATE ROLE` + `CREATE
DATABASE` + `CREATE TABLE llm_usage_log` (schema already known exactly
from `ai_router.py`'s own `_log_db()` INSERT statement) using the
already-configured password. Also found independent corroborating
evidence this is a known, longstanding gap, not new: a crontab comment
dated 2026-08-29 already reads *"clawdb-wrapper 2026-08-29 (was: bare
pg_dump chain silent-fail; openclaw DB nonexistent)"* — someone already
worked around this gap's symptom without fixing its cause, over three
weeks before this program started.

**Not executed**: constructing the `CREATE ROLE ... PASSWORD` statement
requires reading the real password value into the command, which this
session's own permission system correctly classifies as a secret-store
write and blocks — a legitimate, separate safety boundary, not this
program's own risk call. The value itself was never printed or logged
anywhere in this session's output.

## Summary Table

| Item | Status |
|---|---|
| 1. oe-proxy cost gate | **Resolved** — confirmed real via code read |
| 2. ai_router.py enforcement | Designed + tested (2 methods) + staged; **deployment blocked** (Production Deploy gate) |
| 3. PATH/node bug | **Done** (Workstream 7/7b) |
| 4. Key rotation | **Explicitly out of scope** this phase |
| 5. Postgres role | Root cause + exact fix identified; **execution blocked** (Secret-Store Writes gate) |

## What This Means

Three of five items reached a state of "ready, verified, one command
away" rather than "done," each stopped by a distinct, correctly-scoped
permission boundary this session doesn't have blanket authority to cross
even with the broader remote-write grant obtained earlier in this phase.
This is the safety system working in layers, not a single on/off switch
— and this document treats each stop as real information for you, not
as something to route around.
