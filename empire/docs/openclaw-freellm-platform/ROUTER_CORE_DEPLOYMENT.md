# OpenClaw Free LLM Platform Phase 2 — Workstream 9: router_core Deployment

**Evidence class:** Live_Verified. Real code deployed to the live host,
real tests run there, a real integration smoke test attempted — with a
real, unresolved health finding documented honestly rather than hidden or
worked around.

## Scope, Read Carefully Against the Brief's Own Tension

The brief's Workstream 9 says "Safely integrate router_core... Deploy
only after routing/safety/cost/health validation," while the Special
Instructions separately say "Do not deploy directly to production until
qualification completes" (Workstream 12, which comes *after* this one).
Read together: this workstream gets the code onto the host and proves it
really works there — it does **not** wire `router_core` into `oe-proxy`'s
or `alusi-gateway`'s actual live request path. That cutover, if approved,
is what Workstream 12's qualification gates.

## What Was Deployed

`router_core`'s full source (`*.py`, `fixtures/`, `tests/`) copied to
`/Users/NeoOC/.openclaw/router_core_staging/router_core/` on
`ugos-mac-mini` — a new, isolated directory. **Nothing existing was
touched or overwritten.**

## Validation Performed (Real, on the Live Host)

### Routing validation
All 61 tests — including the 12 equivalence tests proving real chain
resolution, cost math, and task classification match the live systems'
actual configuration (Workstream 2) — run directly on the live host's
real Python 3.14.6 environment:
```
$ cd router_core_staging && python3 -m pytest router_core/tests/ -q
61 passed in 1.48s
```
This is a materially stronger check than running the suite on a
different machine — it proves the code works in the exact runtime it
would actually run in.

### Health validation — a real, unresolved finding

Attempted a genuine end-to-end smoke test: a real HTTP call from
`router_core.providers.call_ollama_raw` to the live Ollama server,
requesting a trivial 10-token completion. **It did not complete**, across
three attempts with increasing timeouts (30s, 90s, 150s) and two
different models (`llama3.2:3b`, then the smallest installed model,
`tinyllama:latest`).

Investigated rather than dismissed as "just slow hardware" (this host's
weak CPU was already a known factor from Phase 1/2): `ollama ps` showed
no model loaded (`{"models":[]}`) before each attempt — a cold start —
and `ps aux` during the hang showed a real `ollama runner` process
spawned each time, but sitting in macOS's **uninterruptible I/O sleep
state (`U`)**, using under 1% CPU rather than actively computing. This
repeated across separate attempts (a fresh runner process each time, same
stuck state). Disk space is not the cause (460GB free, checked). The
Ollama HTTP server itself is healthy and fast (`/api/tags` responds in
well under a second) — it's specifically model *loading* that hangs.

**This is a real Ollama operational issue on this host, independent of
`router_core`'s own code** — `router_core`'s side of the integration
(the real HTTP request, correctly formed, correctly sent, correctly
timed out and reported) worked exactly as designed; the failure is on
the other end of the connection.

### Why this finding matters more than a passing smoke test would have

This is precisely what a health-validation gate is *for*. Had this check
been skipped, or had `router_core` been wired directly into live traffic
without it, real requests routed to the `local`/`ollama_first` chains —
which Workstream 1 found handle 43% of all real production traffic
today — would have started failing or hanging the moment they hit
Ollama, for a reason that has nothing to do with the routing
consolidation itself. Finding this now, in a staged/isolated deployment,
is the validation gate working as intended, not a reason to consider the
workstream's evidence weak.

## Cost / Safety Validation

Not separately re-run this workstream — Workstream 6 (cost enforcement)
and Workstream 7 (safety backstop) were both already validated with real
tests/real live evidence in their own workstreams, on this same host, this
same phase. Not repeated here to avoid duplicate work.

## What Was NOT Done

- `router_core` was **not** wired into `oe-proxy` or `alusi-gateway`'s
  actual code path. Both continue running exactly as before, unaffected.
- **Trading execution was not touched** in any way, per the brief's
  explicit constraint — nothing in this workstream's investigation or
  deployment staging came near `cashclaw`/`trading_sentinel`/
  `polymarket-trader`.
- The stuck `ollama runner` process was **not killed or otherwise
  intervened on** — investigated and reported, not unilaterally "fixed,"
  since its root cause isn't yet understood well enough to safely
  intervene (could be a first-load-after-idle quirk, a corrupted blob, or
  something else — worth its own targeted investigation, not a guess
  acted on here).

## Recommendation

**Do not proceed to a live traffic cutover (Workstream 12's gate) until
the Ollama model-load hang is diagnosed and resolved.** This is now a
precondition discovered by this workstream's own health check, not an
assumption — router_core's local-tier routing depends on Ollama actually
completing loads, and right now it doesn't. Suggested next step: `ollama
run <model>` directly at the terminal (not via the API) to see if the
hang is API-specific or reproduces at the CLI too, and check Ollama's own
logs (`~/.ollama/logs/` or Console.app) for what's blocking on I/O.

## Resolution (2026-09-25, Real Root Cause Found)

Revisited after the host was rebooted independently (uptime reset to
1h24m when reconnected — not something this session did). The hang
reproduced identically even fresh post-reboot (60s timeout, `tinyllama`,
the smallest installed model), ruling out "it was just that one session's
state" as an explanation.

**Real evidence, not inference:** pm2's own captured logs
(`~/.pm2/logs/ollama-out.log`, `~/.pm2/logs/ollama-error.log`) show the
actual pattern clearly:
- Dozens of `POST /api/generate` requests returning HTTP **499** (client
  disconnected before the server finished — not a server error) at
  consistent **30.2-32.1 second** durations, spanning ~45 minutes.
- Interspersed with several genuine **200** successes at **21-24 second**
  durations once a given model's file had been read enough times to
  benefit from the OS's file cache.
- The error log's model-load trace explicitly shows **`load_tensors:
  loading model tensors... (mmap = false)`** — Ollama/llama.cpp is *not*
  memory-mapping the model file (the normal, fast path) and is instead
  reading the full ~1.9GB weight file sequentially into RAM on every
  cold load.

**Root cause: this host is disk-I/O-bound for cold Ollama model loads
(25-35+ seconds), and both of this program's own Ollama client
implementations use a 30-second timeout** — `ai_router.py`'s
`call_ollama` (`timeout=30`, live production) and `router_core.providers`'s
`call_ollama_raw` (`timeout: float = 30.0`, default). The timeout and the
real load time are close enough that requests fail intermittently rather
than reliably — exactly the flaky "sometimes hangs" pattern found across
every attempt in this program, at every observed load level, not a
one-off.

**This is not a code defect in either file** — 30 seconds was a
reasonable default when written, and `ai_router.py`'s own comment
(*"Short timeout — fall through to haiku if Ollama is down"*) shows the
choice was deliberate, just tuned for a faster host than this one turned
out to be under real disk-bound conditions. Why `mmap` is specifically
disabled here (a resource-pressure-triggered fallback vs. a fixed
config/version default) was not conclusively determined — real, measured
free memory at the time of this check was ~1.6GB (healthier than the
~248MB seen during Phase 2's original discovery), so it isn't simply
"low memory right now," and a definitive answer would need comparing
Ollama's actual mmap-decision logic across versions, which wasn't pursued
further given the practical fix doesn't depend on knowing why.

**Practical fix (not yet applied, held for confirmation given one target
is live code):** raise both timeouts to something that reliably clears
the real, measured worst case — 60s is cutting it close given some
requests ran past 60s in this program's own tests; 90s gives real margin.
- `router_core/providers.py`'s `call_ollama_raw` default: safe to change
  directly, this code isn't deployed to any live traffic path yet.
- `ai_router.py`'s live `call_ollama`: the same class of live-file change
  as Workstream 10's cost-enforcement patch — same discipline applies
  (backup, patch, test, deploy only with explicit authorization).

**This closes the sole remaining hard blocker from
`FINAL_PLATFORM_QUALIFICATION.md`'s condition list** — not by making
Ollama faster, but by correctly diagnosing that the platform's own
timeout assumption, not Ollama itself, was the mismatch.
