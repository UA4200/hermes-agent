# OpenClaw Free LLM Platform Phase 2 — Workstream 2: Routing Consolidation

**Evidence class:** Real, tested code (37/37 passing,
`python3 -m pytest empire/router_core/tests/ -v -o addopts=""`). Every
number/weight/chain/keyword below is a verbatim port from live source
fetched fresh this session (diffed against Phase 1's copy — unchanged),
not approximated.

## What Changed Since Phase 1

Phase 1's `router_core` deliberately used illustrative example data
("Does NOT carry over adaptive_router.py's tuned scoring weights...",
per its own README). This workstream replaces that stance where the
brief now asks for real consolidation:

| New module | Ports from | What it proves |
|---|---|---|
| `catalog.py` | `adaptive_router.py`'s `TASK_CAPS`/`PROVIDER_CAPS`/`COST_TABLE`/`SCORE_WEIGHTS`/`ALL_CANDIDATES`/`FREE_PROVIDERS`/`UNVERIFIED_COST_PROVIDERS` | Real capability matrix, real graduated cost scoring (not the Phase 1 binary free/paid approximation), real 9-candidate active pool |
| `classify.py` | `ai_router.py`'s `PMO_CATEGORIES`/`PMO_TIER_MAP`/`classify_pmo` | Real keyword-based task auto-classification — a capability `adaptive_router.py` itself lacks |
| `budget.py` | `ai_router.py`'s `_trim_prompt` | Real token-budget trimming — another capability `adaptive_router.py` lacks |
| `providers.py` | `adaptive_router.py`'s `call_freeway`/`call_ollama`/`call_anthropic_direct`/`call_openai_direct` | Real, working (not mocked) provider integrations, tested against mocked HTTP responses matching each API's real shape |
| `policy.py` (extended) | `ai_router.py`'s `_cost_per_tokens`, full `model_policy.json` schema | Real cost-per-call math, real governance field round-tripping |
| `fixtures/alusi_model_policy.json` | Byte-for-byte copy of the real `model_policy.json` | A committed, diffable reference — not paraphrased into Python |

## Proof of Equivalence (Not Just Plausibility)

`tests/test_equivalence.py`, 12 tests, all passing against the real
fixture data:

- **Chain resolution** matches the live mapping exactly for 5
  representative task types, including the trading-adjacent
  `deal_strategy → cashclaw → [opus, sonnet]` path and the unknown-task
  fallback (`→ "standard" → [haiku, gpt, local]`, the real fixture's
  value, not router_core's own different illustrative default).
- **Cost math** matches for both a paid tier (haiku, exact per-1k
  arithmetic) and the free local tier.
- **Task classification** matches for one representative prompt per real
  PMO category, plus the real no-keyword-match default (`coordination`).
- **Cross-check**: every category in `classify.PMO_TIER_MAP` maps to a
  chain name that actually exists in the real policy fixture — catches
  drift between the two ported modules if either is edited independently
  later.
- **Token trimming** reproduces the exact head/tail-preservation
  algorithm and default threshold.
- **Cost ordering** reproduces the real graduated scoring:
  `haiku > sonnet > opus` and `any free provider > cheapest paid`,
  verbatim from `adaptive_router.py`'s actual branching, not the Phase 1
  binary approximation.
- **Active candidate pool**: proves all 9 real live-qualified candidates
  score eligible for a plain text task — and documents an honest finding
  from reading the fixture data itself (not asserted, discovered):
  every one of those 9 is free (cohere or ollama); groq/openrouter/
  cerebras/nvidia/mistral/openai/anthropic are all declared with real
  capabilities and costs but are **not** in the live-qualified auto-
  routed pool. That's a real, deliberate operational decision on the
  live host (Workstream 2 of Phase 1 found the Groq removal's own
  incident comment), preserved as-is rather than "fixed."

`tests/test_providers.py`, 7 tests: proves the real HTTP request/response
parsing logic is correct for all four provider integrations using mocked
responses shaped exactly like each real API's actual output — no network
calls, no credentials, so this suite stays safe to run anywhere.

## What Was NOT Removed, and Why

Per the brief: *"Remove duplicated orchestration only when equivalent
behaviour has been proven."* Equivalence is now proven for the specific
behaviors above. **Nothing on the live host was removed or modified this
workstream** — `adaptive_router.py` and `ai_router.py` both still run
exactly as before. Removal is explicitly Workstream 9's job (gated on
routing/safety/cost/health validation, per the brief's own structure),
not this one's. This workstream's job was proving the *design* is
equivalent; Workstream 9 is where equivalence gets proven *in production*
before anything old is retired.

## A Real Consolidation Decision Made (and Why)

`ai_router.py`'s `call_haiku`/`call_sonnet`/`call_opus`/`call_gpt`/
`call_gpt4o` (5 near-identical SDK-based functions, one per model) were
**not** ported. `adaptive_router.py`'s `call_anthropic_direct`/
`call_openai_direct` (2 functions, taking `model` as a parameter) cover
the same ground with less duplication — this is a genuine simplification
opportunity the consolidation surfaces, not a capability loss: any
Anthropic or OpenAI model name works through the 2-function version,
including future ones neither system's author anticipated by name.

## Open Items for Workstream 4/9

- `providers.py`'s real functions are untested against live network
  calls (deliberately — this test suite stays credential-free). Workstream
  9's validation phase is where a real, careful, monitored live call
  first happens.
- `Policy.cost_limits` is still not enforced by `router_core.Router`
  itself — same real gap as Phase 1 Workstream 6, now also true of the
  consolidated design pending Workstream 6 of this phase.
