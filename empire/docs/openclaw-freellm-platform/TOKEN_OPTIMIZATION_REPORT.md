# OpenClaw Free LLM Platform — Workstream 6: Token & Cost Optimization

**Evidence class:** Live_Verified — measured from the real 179,725-row
usage log (`~/.openclaw/memory/raw/ai_router.jsonl`) and the actual source
of `ai_router.py`, not estimated.

## What Already Exists (Confirmed Working)

`ai_router.py` already implements three of the brief's asks:

1. **Prompt trimming** (`_trim_prompt`, `max_chars=3000`): head+tail
   preservation, applied to every prompt before any provider call.
2. **Task classification** (`classify_pmo`): keyword-based, maps a prompt
   to a `PMO_TIER_MAP` category (`monitoring`, `signal`, `lead_gen`,
   `research`, `code`, `strategy`, `coordination`) → chain, used when
   `task_type="auto"`.
3. **Pre-call cost estimation** (`estimate_cost`): computes expected cost
   from the first tier in the resolved chain before calling anything.

**Request batching, response compression, and conversation summarization**
(also asked for in the brief) were **not found** anywhere in `ai_router.py`,
`adaptive_router.py`, or the dormant services — genuinely absent, not
just unverified.

## The Real Gap: Declared Limits Are Not Enforced

`model_policy.json` declares:
```json
"cost_limits": {
  "daily_hard_limit_usd": 10.0,
  "per_call_opus_limit_usd": 0.50,
  "heartbeat_allowed_providers": ["local"]
},
"no_hidden_bypass_routes": true
```

**None of these are checked anywhere in `ai_router.py`'s code.** There is
no daily-spend accumulator, no per-call cap check before an Opus call, and
no code that verifies a heartbeat-classified call is actually restricted
to `local`. The policy file reads like an enforced contract; it is
currently closer to documentation of intent. Confirmed by reading the
entire 467-line file — no `daily_hard_limit`, `cost_limits`, or `budget`
string appears outside the JSON policy data itself.

## Measured Impact (Is This Gap Actually Costing Anything Today?)

**No — not yet, based on real usage data**, and this is worth stating
plainly rather than treating the gap as more urgent than the evidence
supports:

- **Zero calls ever reached the sonnet/opus/gpt/gpt4o tiers** across all
  179,725 logged calls. Every real call has been `local` (76,985, $0) or
  `haiku` (22,333, $0.4614 total).
- **Highest single-day spend recorded: $0.15** (2026-08-05) — 1.5% of the
  declared $10 daily limit.
- **This means the missing enforcement is a latent risk, not an active
  one.** The `cashclaw` chain (`["opus", "sonnet"]`, used for
  `deal_strategy`-classified tasks) has apparently never actually fired in
  production. If it does — and trading-adjacent decision logic is exactly
  where "fired once, unexpectedly" is the scenario worth guarding
  against — there is currently nothing in code stopping an unbounded
  sequence of $0.075+/call Opus requests.

## Recommendation

Implement the missing enforcement as a small, targeted addition to
`ai_router.py` (or, per `OPENCLAW_PLATFORM_ARCHITECTURE.md`'s longer-term
plan, to `router_core`'s policy layer once consolidated) — not a
redesign:

1. A daily-spend accumulator (append-only, reset at UTC midnight or
   `report_timezone`'s local midnight per `model-cost-gateway`'s existing
   convention) checked before each call; refuse and fall back to `local`
   if the day's total would exceed `daily_hard_limit_usd`.
2. A per-call check against `per_call_opus_limit_usd` before dispatching
   to the `opus` tier specifically.
3. A `heartbeat_allowed_providers` check — reject (not silently
   downgrade) any `heartbeat`-classified call whose resolved chain
   includes a non-local provider, since the policy explicitly promises
   this task type never leaves the local tier.

This is a genuinely small change (the policy data already exists; this is
purely adding the check), low-risk, and directly closes a real gap — a
strong candidate for one of the "two low-risk fixes" category from
Workstream 4, alongside the Postgres role and key-rotation items. **Not
implemented in this workstream** — same reasoning as Workstream 4: this
touches the live cost-control path for a system with real trading
processes downstream, and should ship with your review, not unasked.

## Caching/Compression (Cross-Reference)

Workstream 3's GPTCache/LLMLingua recommendations and Workstream 5's
`router_core` prototype (which implements the *hook points* for both,
tested, not deployed) are the other half of this workstream's brief.
Not repeated here — see `CACHING_AND_ACCELERATION_RESEARCH.md` and
`MODEL_ROUTING_POLICY.md`.

## Measurement Honesty Note

The brief asks to measure "API savings... cost reduction." A precise
counterfactual (what would this have cost if every `local` call had gone
to `haiku` instead) is calculable from real data:
76,985 local calls × ($0.4614 / 22,333 haiku calls ≈ $0.0000207/call) ≈
**$1.59 in avoided cost over the system's lifetime to date.** This is the
honest number — real, but modest, because Haiku itself is already very
cheap. It is **not** the "~97% savings" figure found in an unrelated,
never-deployed planning document (`empire/infra/MODEL-ROUTING.yaml`,
Workstream 1) — that figure describes a different, aspirational routing
scheme that was never the one actually running, and citing it here would
misattribute an unverified planning claim as a measured result.
