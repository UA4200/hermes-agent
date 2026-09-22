# OpenClaw Free LLM Platform — Workstream 7: Freeway LLM Assessment

**Evidence class:** Live_Verified — run against the real host this
session, including read-only invocations of the system's own existing
efficiency/governance tooling (`empire_efficiency.py`), not new tooling
built for this program.

## Reframed Per Workstream 2/4

Free-Way itself needs no rebuild — Workstream 2 already established it as
healthy, real, and actively used (via `adaptive_router.py`'s
`call_freeway()`). This workstream is the "repair where appropriate,
replace only what is broken, retain working configuration" assessment the
brief actually asks for, applied to the real state found.

## A Real, Already-Built Assessment System Exists — Used, Not Reinvented

`~/.openclaw/empire/efficiency/empire_efficiency.py` (105 lines,
explicitly documented as *"Read-mostly efficiency controls... Never
mutates protected services"*) already implements exactly this kind of
health/qualification/maintenance assessment, scheduled via cron:

- `canary` (hourly, `--rollback-on-critical`): checks oe-proxy health,
  a **cost-limit enforcement gate**, and a privacy classifier.
- `qualify --benchmark` (weekly): pings every installed Ollama model with
  a real prompt, records latency/success.
- `maintenance` (hourly): classifies every pm2 service as
  `protected_no_touch` / `review_retirement_or_enablement` / `observe` —
  `automatic_mutations: False`, always.
- `dashboard`: aggregates health across oe-proxy (4100), Free-Way (8082 —
  **confirms the real port**, correcting an earlier assumption of 8787
  from Free-Way's own README default), and Ollama (11434).

Rather than build new assessment tooling, this workstream ran the
existing one and read its real output.

## Real Results From Running It This Session

**`dashboard`:** all three core services healthy (`oe_proxy`, `freeway`,
`ollama` all `true`). One stale item: a `PENDING` paid-inference approval
request (`max_cost_usd: $0.0000896`) that expired 2026-09-16 and was never
cleaned up or auto-rejected — trivial in dollar terms, but indicates the
approval-expiry path isn't actually enforced either (same class of gap as
Workstream 6's cost-limit finding).

**`canary` (run without `--rollback-on-critical`, matching a safe manual
check):**
```json
{"checks": {"health": true, "paid_cost_gate": false, "privacy_classifier": true}, "status": "FAIL"}
```
**The `paid_cost_gate` check is currently failing.** This canary
deliberately sends an oversized fake Opus request expecting an HTTP 403
`cost_limit` rejection from `oe-proxy`. It isn't happening. This
independently confirms, from a completely different angle than Workstream
6's static-code-reading finding, that this system's cost enforcement is
not actually working at the `oe-proxy` layer either — not just
`ai_router.py`'s.

**The automated remediation for this is itself broken.** The hourly cron
entry (`17 * * * * ... canary --rollback-on-critical`) should attempt
`rollback_proxy()` on this exact failure. Its own log
(`reports/scheduler.log`) shows it has been crashing:
```
env: node: No such file or directory
subprocess.CalledProcessError: Command '[.../pm2', 'restart', 'oe-proxy']' returned non-zero exit status 127
```
`pm2` is a Node shebang script; cron's minimal environment doesn't have
`node` on `PATH`, so the rollback's `pm2 restart` step fails before it can
complete. **This is the identical bug class already found and partially
fixed elsewhere in this same crontab today** (a `pm2 save` entry carries
the comment *"PATH fixed 2026-09-22, OP-002 finding: env node not
found"*) — but the fix was not applied to `empire_efficiency.py`'s
rollback path. No trace of what "OP-002" is beyond that comment was found
on this host; noted as evidence someone/something is actively working the
same class of issue today, not investigated further here to avoid
duplicating that work blind.

**Net effect:** the failing cost-gate has had no working automatic
remediation for an unknown period — the hourly job has presumably been
crash-looping silently rather than either fixing or clearly alerting on
the underlying problem.

## Dormant Components — Retirement Confirmed Safe

Workstream 4 flagged `economic_guard.py`, `groq_rotator.py`,
`fcc_router.py` for individual audit before retiring alongside
`model-cost-gateway` and `native-router`. This session confirmed:

- **No cron job** (full crontab read, 40+ entries) references any of
  these five components.
- **No launchd job** is loaded referencing them —
  `com.openempire.model-cost-gateway.cost-audit.plist` exists on disk but
  is **not loaded** (`launchctl list` shows nothing matching), confirming
  it was built but never activated.
- **No other script** in `~/.openclaw` imports `economic_guard` or
  `groq_rotator` (repo-wide grep, this session).

**Retirement is now confirmed safe for `model-cost-gateway` and
`native-router`.** `economic_guard.py`, `groq_rotator.py` are confirmed
unreferenced by anything scheduled or imported, but `fcc_router.py`
self-references (`from fcc_router import route_inference` inside its own
file) — worth a one-line check of whether that's a `__main__` guard or an
actual external caller before retiring; not resolved this pass.

## What Changed, Documented (Per the Brief's "Document Every Modification")

**Nothing was modified this workstream.** All commands run were read-only
per the tool's own design (`dashboard`, `canary` without the rollback
flag, crontab/launchctl reads, grep). The `canary` run did write a fresh
`reports/canary-latest.json` (the tool's normal, expected behavior on any
invocation) — that's a report artifact, not a configuration change.

## Recommendation

1. **Fix the `PATH`/`node` issue in `empire_efficiency.py`'s
   `rollback_proxy()`**, mirroring the fix already applied to the
   `pm2 save` cron entry today — same root cause, same fix shape. Small,
   isolated, high-value. Held for your go-ahead per this program's
   running policy on live-host changes.
2. **Investigate why `paid_cost_gate` is failing** — this is now
   confirmed from two independent angles (Workstream 6's code read,
   Workstream 7's live canary) and should be prioritized over the PATH
   fix, since a working rollback for a gate that doesn't work yet only
   restores a non-working state.
3. **Clear the expired pending approval** and consider whether expiry
   should auto-reject rather than sit indefinitely.
4. Retire `model-cost-gateway`, `native-router`, `economic_guard.py`,
   `groq_rotator.py` per the confirmed-orphaned evidence above; resolve
   `fcc_router.py`'s self-import before deciding on it.
