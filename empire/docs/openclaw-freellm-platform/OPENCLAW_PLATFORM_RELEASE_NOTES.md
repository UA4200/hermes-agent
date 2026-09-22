# OpenClaw Free LLM Platform — Release Notes

## v0.1.0-prototype (2026-09-22)

First release. Prototype status throughout — see `OPENCLAW_FREE_LLM_
PLATFORM.md` for what that means concretely.

### Added

- `router_core`: unified routing library (policy resolution, health-aware
  provider scoring/circuit-breaking, cache/compression hook points).
  18/18 tests passing, zero required dependencies.
- `install_check.py`: real installer/health-check script.
- 15 documents across Workstreams 1-10 covering live-verified current
  state, root cause analysis, ecosystem research, target architecture,
  the routing prototype, cost analysis, a Free-Way health assessment,
  client qualification, and the AI Orchestration capability design.

### Fixed

Nothing — this release proposes fixes, it doesn't apply them. Two
specific fixes are documented and held for approval:
`empire_efficiency.py`'s PATH/node rollback bug (Workstream 7) and the
missing enforcement of `model_policy.json`'s declared cost limits
(Workstream 6).

### Known Issues (On the Real, Live System — Not This Prototype)

- `ai_router.py`'s declared cost limits (`daily_hard_limit_usd`,
  `per_call_opus_limit_usd`) are not enforced in code (Workstream 6).
- Whether `oe-proxy` enforces its own cost limit is unverified — its
  canary test is stale and doesn't reach the code path it's meant to
  check (Workstream 7, corrected finding).
- `empire_efficiency.py`'s automated rollback crashes on a PATH/node
  issue (Workstream 7).
- A live Gemini API key was found exposed in a plaintext log
  (`native-router`'s error log) — flagged for rotation, value not
  reproduced anywhere in this program's output (Workstream 2).
- A daily cron reminder references a trading-data path that no longer
  exists (Workstream 8).

### Known Limitations (This Prototype)

- Not deployed. Not wired into `oe-proxy` or `alusi-gateway`.
- No real GPTCache/LLMLingua integration (hook points only).
- No persistence for `RouterState` (in-memory only).
- No token-budget trimming ported from `ai_router.py`'s `_trim_prompt`.
- Circuit-breaker/scoring weights are illustrative, not tuned against
  real traffic.

### Explicitly Not Broken (Verified, Not Assumed)

- Free-Way: healthy, 5+ days uptime, 0 restarts (Workstream 2/7).
- `oe_proxy`/`freeway`/`ollama` health endpoints: all responding
  (Workstream 8, live check).
- `adaptive_router.py`/`ai_router.py`: both real, both handling real
  production traffic (179,725 logged calls) (Workstream 1).
- 4 pm2 processes the earlier screenshot-derived report flagged as
  crash-looping are confirmed working as designed (Workstream 1/2).

## Next Release (Not Scheduled, Not Committed To)

Would require: your review/approval of Workstream 4's staged migration
plan, the two low-risk fixes (Postgres role or dead-code removal, key
rotation), and the `paid_cost_gate`/PATH fixes from Workstream 7 — none
of which this program executed unasked.
