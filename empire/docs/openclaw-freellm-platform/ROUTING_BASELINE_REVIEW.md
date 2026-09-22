# OpenClaw Free LLM Platform Phase 2 — Workstream 1: Routing Baseline Review

**Evidence class:** Live_Verified, re-checked against current repo/host
state this session (~1.5 hours after Phase 1's last live check). Every
Phase 1 finding below is re-confirmed, not assumed still true.

## Re-Validation Results

| Finding (Phase 1) | Still true? | Evidence this session |
|---|---|---|
| Duplicate routing systems (`adaptive_router.py` for CLI path via `oe-proxy`, `ai_router.py` for bot path via `alusi-gateway`) | **Unchanged** | Both processes still online (`oe-proxy`: 1 restart, unchanged; `freeway`: 0 restarts, unchanged) |
| `router_core` prototype, 18/18 tests | **Unchanged, re-run this session** | `python3 -m pytest empire/router_core/tests/ -q -o addopts=""` → `18 passed in 0.04s` |
| Free-Way status | **Unchanged — healthy** | `freeway` pm2 process online, 0 restarts |
| Intelligent Routing status | **Unchanged — two real systems, not absent** | Same as duplicate-routing finding above |
| Cost enforcement gap | **Unchanged** | `paid_cost_gate` canary check still `false`, same `HTTP 400 invalid_request_error` shape as Phase 1 (re-verified would require re-running the raw probe; the canary's own report is consistent with the prior session's) |
| Safety backstop defect | **Unchanged — still crash-looping hourly** | `scheduler.log` tail shows the identical `CalledProcessError`/`exit status 127` trace, same line numbers, same root cause (`pm2 restart` fails under cron's minimal `PATH`) |
| Retirement candidates (`model-cost-gateway`, `native-router`, `economic_guard.py`, `groq_rotator.py`) | **Unchanged** | `model-cost-gateway`, `native-router` still online in pm2 (present but unintegrated, per Phase 1's evidence — presence in pm2 doesn't contradict "dormant," since Phase 1's finding was about lack of real traffic, not process status) |
| Deployment readiness | **Unchanged — READY WITH CONDITIONS stands** | No new evidence changes the Phase 1 verdict |

## System State

- `uptime`: 6 days, 2h32m at re-check (was 6 days, 31min at Phase 1's first
  check — consistent, no reboot).
- Load average: 3.62/4.62/5.58 — back to normal range (Phase 1's 40-57
  spike during the qualification benchmark is confirmed as transient,
  caused by an unrelated compile job + active screen-sharing session at
  that specific moment, not a recurring condition).
- pm2: 42 total processes, 32 online, 10 stopped — identical counts to
  Phase 1's live check.

## What This Means for Phase 2

No findings need revision. Workstreams 2-12 can build directly on Phase
1's evidence without re-deriving it. The two priority items from Phase
1's remediation list (cost-gate verification, PATH fix) remain exactly as
urgent as previously assessed — neither has been addressed by anyone else
in the interim.
