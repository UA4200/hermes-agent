# OpenClaw Free LLM Platform — Workstream 5: Intelligent Routing

**Deliverable:** `empire/router_core/` — a real, tested (18/18 passing,
`python3 -m pytest empire/router_core/tests/ -v -o addopts=""`), standalone
prototype demonstrating the consolidation architecture from Workstream 4.
See `empire/router_core/README.md` for exactly what it does and does not
prove — summarized here.

## What was built

A unified `Router.route(task_type, prompt)` that composes, in order:

1. **Cache check** (`cache.py`) — semantic/exact-match lookup before any
   provider call.
2. **Policy resolution** (`policy.py`) — task-type → chain, shaped after
   `ai_router.py`'s `model_policy.json` (read live, not guessed).
3. **Conditional compression** (`compress.py`) — only for chains mapped to
   expensive tiers (`high_value`/`paramount`), only above a size
   threshold — matching Workstream 3's recommendation to compress where
   cost is highest, not universally.
4. **Health-aware ranking and execution** (`engine.py`) — shaped after
   `adaptive_router.py`'s `RouterState`/circuit-breaker/scoring pattern
   (read in full, 657 lines, from the live host), reimplemented
   independently rather than copied.

## What real bugs this process caught (worth noting for its own sake)

Building and actually running the test suite (not just writing it) caught
3 real test bugs before they could hide a design defect:

- A circuit-breaker test asserted quarantine after one failure, but the
  engine's `HEALTHY→DEGRADED→QUARANTINED` transition is a two-step
  `elif` chain (mirrored faithfully from `adaptive_router.py`'s own logic)
  — quarantine correctly requires two `record_failure()` calls at
  `degrade_after=quarantine_after=1`, not one. Test was wrong, not the
  engine — but this is exactly the kind of thing that looks fine on read-
  through and only surfaces when the test actually runs.
- Two compression tests used a chain name (`"high_value"`) where a
  task-type was required (`"research"`, which *maps to* `"high_value"` in
  the default policy) — an easy mistake to make given both concepts share
  vocabulary, caught immediately by the tests failing with
  `all_candidates_failed` rather than silently passing.

## What this explicitly does not prove

Per `README.md`: no real provider was called, `adaptive_router.py`'s
actual tuned scoring weights/provider catalog/circuit-breaker timing were
not carried over, and this has not been deployed anywhere near
`oe-proxy`/`alusi-gateway`. It proves the *design* composes correctly
under test, not that it's a safe drop-in replacement for either live
system. `OPENCLAW_PLATFORM_ARCHITECTURE.md`'s staged migration plan is
what would actually take this from prototype to production, and that plan
is explicitly not executed by this workstream.

## Configurability / no manual model switching

The brief asks for "Routing shall be configurable. No manual model
switching." This prototype satisfies that at the design level: adding a
provider/tier means adding an entry to `candidates_by_tier` and `callers`
(both plain dicts passed into `Router.__init__`), and changing routing
behavior means editing the policy data (`Policy.from_file(...)`), not code
— no caller ever names a specific model directly.
