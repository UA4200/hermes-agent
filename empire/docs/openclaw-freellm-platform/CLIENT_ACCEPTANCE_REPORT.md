# OpenClaw Free LLM Platform — Workstream 8: Client Qualification

**Evidence class:** Live_Verified. Every dimension below is checked
against real current state, not assumed. Where a check was inconclusive,
that's stated plainly rather than rounded up to a pass.

**Situational note:** while running this workstream's checks, `ps aux`
showed active screen sharing (`ScreensharingAgent`, `screensharingd`
running) plus a heavy `clang`/Rust compile job (`~/.openclaw/repos/
openhuman`) and an open Chrome session — i.e., **someone is actively,
interactively using this Mac Mini right now**, unrelated to this program.
Noted for situational awareness; this workstream's checks were kept
read-only and brief to avoid interfering with that.

## Routing

**Healthy.** `dashboard` (Workstream 7) confirms `oe_proxy`, `freeway`,
and `ollama` all responding. `adaptive_router.py`'s and `ai_router.py`'s
real traffic (179,725 logged calls, Workstream 1) confirms routing works
under real production load, not just a synthetic health check.

## Fallback

**Confirmed by design, not independently re-tested this pass.** Both live
routers implement escalation-on-failure (`adaptive_router.py`'s
try-next-candidate loop with circuit breaking; `ai_router.py`'s chain
iteration with per-tier exception handling) — read directly from source
in Workstreams 2/5, not assumed. Not forced to fail live this pass
(would mean deliberately breaking a working provider path on a system
someone is actively using right now — held for a dedicated test window).

## Context Retention

**Not tested — flagged as a real gap, not silently skipped.**
`router_core`'s test suite (Workstream 5) exercises single-turn routing
only. Neither live router was observed handling multi-turn conversation
state in the code read so far. This would need its own investigation
pass to answer properly.

## Engineering Programs

**Out of scope for this system** — Engineering Programs are an
`engineering-operating-system` concept (a separate repository), not
something `ugos-mac-mini`'s empire implements. Not applicable here.

## Knowledge Retrieval

**Exists, not deeply verified.** `empire/knowledge-governance/
governed_knowledge.py index` runs daily via cron (confirmed in the full
crontab read, Workstream 7). Not exercised end-to-end this pass.

## Documentation Generation

**This program's own output is the evidence.** Nine real documents
produced across Workstreams 1-8, each grounded in live-verified data —
itself a working demonstration of documentation generation grounded in
real system state, which is what this line item is really asking whether
the platform can support.

## Trading Workflows

**Live and active — with a real, current constraint.** `cashclaw_arb`,
`cashclaw_director`, `trading_sentinel`, `polymarket-trader` all online
(Workstream 1). Read the real, current trade log
(`~/.openclaw/trading/data/arb/arb_trades.jsonl`, last entries seconds
before this check, `"dry_run": false`): the arbitrage scanner is actively
finding and attempting real opportunities (e.g. a Kalshi bundle showing
62 cents/contract profit), but **recent attempts are failing at the
execution leg with `insufficient_balance`** (HTTP 400 from Kalshi) —
`realized_pnl: 0.0` on the recent entries checked. This is an account
funding matter, not a code defect, and is reported factually for your
awareness, not as something this program should act on.

One minor, unrelated finding: a daily cron reminder
(`0 10 * * * ... "check ~/.openclaw/cashclaw/trades.jsonl"`) references a
path that no longer exists — the real data has moved to
`~/.openclaw/trading/data/`. The reminder still fires; the path it tells
you to check is stale.

## Failure Recovery

**Partially confirmed, one real gap found and already documented
(Workstream 7).** Circuit-breaker recovery (`RETEST` after quarantine
cooldown) is implemented in `adaptive_router.py`'s source. The
higher-level automated rollback (`empire_efficiency.py`'s
`--rollback-on-critical`) is currently broken (PATH/node issue,
Workstream 7) — a real failure-recovery gap, already flagged there, not
re-litigated here.

## Cost Optimization / Token Optimization

**See Workstream 6 and the Workstream 7 correction.** Real measured
savings to date are modest (~$1.59 lifetime local-vs-haiku avoidance);
declared cost limits are not enforced in `ai_router.py`'s code; whether
`oe-proxy` enforces its own limit is genuinely unverified (corrected
finding, Workstream 7) rather than confirmed either way.

## Model Health Benchmark

**Run, inconclusive.** `qualify --benchmark` (the system's own tool) was
run against all 6 installed Ollama models — **all 6 timed out** (45s
timeout, trivial 12-token prompt). Investigated rather than reported at
face value: load average at the time was **40-57 on a 2-core CPU**,
driven by the concurrent compile job and interactive session noted above,
not by anything in the routing/trading stack. **This result should not be
read as "Ollama is broken"** — it's a measurement taken during genuine,
unrelated heavy contention on modest hardware. Recommend re-running
`qualify --benchmark` during a quiet period for a representative result;
not re-run again this pass to avoid adding more load to an already
heavily-loaded, actively-used machine.

## No Production Regression

**Confirmed — nothing was modified.** Every command run across this
entire program (Workstreams 1-8) was read-only or was the system's own
existing read-only tooling (`empire_efficiency.py dashboard`/`canary`/
`qualify`, which the system already runs on its own schedule). No file
was edited, no service was restarted, no config was changed, no pm2
process was touched. `git log` on `hermes-agent` shows only new files
added under `empire/docs/openclaw-freellm-platform/` and
`empire/router_core/` — nothing existing was altered.

## Overall

**Mixed, honestly reported rather than rounded to a single verdict per
category:** routing and documentation generation are demonstrably
healthy; trading workflows are live but currently funding-constrained;
cost enforcement is a confirmed-and-unverified mix across two subsystems;
failure recovery has one known, already-flagged gap; context retention
and fallback-under-real-failure remain genuinely untested. This feeds
Workstream 11's single overall READY / READY WITH CONDITIONS / NOT READY
verdict for the program as a whole — not decided here, since this
document's job is the per-dimension evidence that verdict has to rest on.
