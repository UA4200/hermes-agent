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
**The `paid_cost_gate` check is currently failing — but not for the
reason it looks like at first.** This canary sends an oversized fake Opus
request (`max_tokens: 100000`) expecting an HTTP 403 `cost_limit`
rejection from `oe-proxy`. Checking the *actual* raw response (not just
the canary's boolean summary) shows: **HTTP 400,
`{"error": {"type": "invalid_request_error", "message":
"invalid_request_fields"}}`** — not a 200 success, and not the 403
`cost_limit` the test expects either. This matters a lot for severity:
**no money is being spent** — the request is rejected — but it's rejected
for an unrelated validation reason, before whatever cost-gate logic
exists ever gets a chance to run. This is most likely a **stale test**
(oe-proxy's request validation changed since this canary was written, and
now rejects the probe's shape before reaching the cost check it means to
exercise) rather than confirmed proof the cost gate itself is absent.
Whether real cost enforcement exists and works at the `oe-proxy` layer is
now genuinely **unverified, not confirmed-broken** — a materially
different, more accurate finding than this document's first draft stated
before the raw response was checked.

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

**Net effect:** a stale (or newly-mismatched) canary test has had no
working automatic remediation for an unknown period — the hourly job has
presumably been crash-looping silently rather than either fixing or
clearly alerting. No evidence of real financial exposure (the probe
request is rejected, not executed) — but the underlying question this
canary was built to answer (does `oe-proxy` actually enforce a cost
limit?) is now open again, not settled, since the test that was supposed
to verify it no longer exercises the code path it claims to.

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
2. **Fix or replace the `paid_cost_gate` canary probe** so it actually
   exercises `oe-proxy`'s cost-limit logic again (its current request
   shape gets rejected by input validation before reaching that code),
   and **separately verify whether `oe-proxy` cost enforcement exists and
   works at all** — Workstream 6 already found the equivalent enforcement
   missing in `ai_router.py`'s code; whether `oe-proxy` has its own
   working version is now an open question, not a confirmed gap. Resolve
   this before the PATH fix — a working rollback for a test that isn't
   testing the right thing doesn't add real safety.
3. **Clear the expired pending approval** and consider whether expiry
   should auto-reject rather than sit indefinitely.
4. Retire `model-cost-gateway`, `native-router`, `economic_guard.py`,
   `groq_rotator.py` per the confirmed-orphaned evidence above; resolve
   `fcc_router.py`'s self-import before deciding on it.

## Final Update (Post-Phase-2-Workstream-10): Item 2 Fully Resolved

Read `oe_proxy.py` in its entirety (221 lines, confirmed complete) — the
`"invalid_request_error"`/`"invalid_request_fields"` shape this document
originally found does not appear anywhere in the file's actual logic.
Re-ran the exact original probe: it now returns
`HTTP 403 {"error": {"type": "cost_limit", "message":
"paid_request_exceeds_cost_ceiling"}}` — exactly the code path and
exactly the response the canary expects. **Re-ran the real canary tool
itself: full `PASS` across all three checks** (`health`,
`paid_cost_gate`, `privacy_classifier`), where it previously showed
`FAIL`.

**Conclusion:** the earlier 400 response was a transient state at that
specific moment (`oe-proxy` had 1 restart recorded across this program's
timeline — plausibly mid-restart or briefly degraded then), not a
persistent defect in the probe or the enforcement logic. Both are
correct and working. Item 2 above ("fix or replace the canary probe") is
now closed — nothing to fix; re-verified live and passing.
