# router_core — Prototype

**Status: prototype, not deployed.** This is Workstream 5's deliverable for
the OpenClaw Free LLM Platform program. It demonstrates the consolidation
pattern proposed in `OPENCLAW_PLATFORM_ARCHITECTURE.md` — one shared
routing library instead of `ugos-mac-mini`'s two independent, live
implementations (`adaptive_router.py`, `ai_router.py`) — but it is **not**
a drop-in replacement for either, and it has not been deployed to
`ugos-mac-mini` or wired into `oe-proxy`/`alusi-gateway`.

## Why a prototype, not a port

`adaptive_router.py` (657 lines, read in full from the live host) is
production-hardened: fail-closed gating on paid inference and tool use,
a circuit breaker with quarantine/retest semantics, and comments recording
real incidents (e.g. a Groq 403 that got it pulled from the candidate
pool). Rewriting that from a read-only SSH session, without the ability to
run it against real provider traffic, would risk silently dropping a
safety property that only shows up under real failure conditions. Instead,
this prototype:

- **Borrows the pattern, not the file.** `engine.py` reimplements the
  *shape* of `adaptive_router.py`'s health-tracking/scoring approach
  (`RouterState`, `score_candidate`, `rank_candidates`) as clean,
  independently-tested code — not a copy-paste, so it can be reviewed on
  its own merits before anyone considers pointing real traffic at it.
- **Borrows `ai_router.py`'s policy shape**, not its module — `policy.py`
  implements the same task-type → chain mapping concept
  (`model_policy.json`), independently loadable and testable.
- **Adds the two new layers** Workstream 3 recommended: a semantic-cache
  hook (`cache.py`, GPTCache-shaped interface, no-ops if `gptcache` isn't
  installed) and a context-compression hook (`compress.py`, LLMLingua-
  shaped interface, same no-op fallback).
- **All provider calls are mockable** — `tests/` exercises the full
  routing/caching/compression flow with fake providers, no network calls,
  no API keys required. This proves the *design* works; it does not prove
  parity with either live system's exact behavior under real failures.

## What this does NOT do

- Does not call Free-Way, Ollama, Anthropic, or OpenAI for real in its
  test suite.
- Does not replicate `adaptive_router.py`'s exact scoring weights,
  provider catalog, or circuit-breaker timing — those are real tuning
  decisions made against real traffic on the live host and shouldn't be
  guessed at from outside.
- Does not replicate `ai_router.py`'s exact `model_policy.json` (that file
  contains the live cost limits and task mappings — this prototype ships
  its own small example policy for testing).
- Is not registered with pm2, not given real credentials, not reachable
  from `oe-proxy` or `alusi-gateway`.

## Path to real use (per `OPENCLAW_PLATFORM_ARCHITECTURE.md`'s migration plan)

If this design is approved: port `adaptive_router.py`'s *actual* tuned
scoring engine and provider catalog into `engine.py` (replacing the
example one here), point it at the live `model_policy.json`, add real
GPTCache/LLMLingua dependencies, then follow the staged rollout (`oe-proxy`
first, verify, then `alusi-gateway`) — not a step this program executes
unattended.

## Running the tests

```bash
cd empire/router_core
python3 -m pytest tests/ -v
```
