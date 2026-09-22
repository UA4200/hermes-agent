# OpenClaw Free LLM Platform — Workstream 10: Product Guide

**v0.1.0-prototype.** Combined administrator/user guide — audience for
this internal tool is the same person for both roles, so one document
covers both rather than artificially splitting them.

## What This Product Is, Honestly

A tested, dependency-free Python routing library (`router_core`,
Workstream 5) that demonstrates how `ugos-mac-mini`'s two real, live,
independently-built routing systems (`adaptive_router.py`, `ai_router.py`
— Workstream 2) could be consolidated into one. **It is not yet deployed
anywhere.** This guide documents what exists today and what using it for
real would require — it does not describe a shipped product, because
there isn't one yet.

## For Users (Someone Calling the Router)

```python
from router_core import Router
from router_core.policy import Policy
from router_core.engine import Candidate

policy = Policy.default()
candidates = {"local": Candidate("ollama", "llama3.2:3b", is_free=True,
                                   capabilities=frozenset({"text"}))}
callers = {"local": lambda model, prompt: my_ollama_client.generate(model, prompt)}

router = Router(policy, candidates, callers)
result = router.route("heartbeat", "ping")
print(result.text, result.provider, result.success)
```

See `AI_ORCHESTRATION_CONFIGURATION.md` for the full policy/candidate/
caller schema.

## For Administrators

- **Install/verify:** `AI_ORCHESTRATION_INSTALLER.md` — real, runnable,
  18/18 tests passing as of this session.
- **Health check:** `python3 empire/router_core/install_check.py` — the
  same script used for install verification doubles as an ongoing health
  check (re-running it re-validates import + test suite).
- **Configuration:** `AI_ORCHESTRATION_CONFIGURATION.md`.
- **Diagnostics for the *real, currently-running* system** (not this
  prototype): use the live host's own existing tooling,
  `empire_efficiency.py dashboard`/`canary`/`qualify` (Workstream 7) —
  don't build new diagnostics when working ones already exist and are
  already scheduled.

## Upgrade Tool / Migration Guide

**Do not exist, and building them now would be premature.** An upgrade
tool upgrades something already deployed; a migration guide migrates
users off something already in use. Neither applies to a prototype that
has never been deployed. Once `OPENCLAW_PLATFORM_ARCHITECTURE.md`'s
staged rollout (approved, then executed) puts `router_core` in front of
real traffic on `oe-proxy` or `alusi-gateway`, *that* is the point where
an upgrade tool and migration guide become real, needed artifacts — not
before.

## Troubleshooting Guide

| Symptom | Cause | Fix |
|---|---|---|
| `install_check.py` reports `[FAIL] router_core failed to import` | Python < 3.10, or run from wrong directory | Check `sys.version`; run from a location where `empire/` is importable |
| `Router.route()` always returns `all_candidates_failed` | No caller registered for any tier in the resolved chain, or all candidates are quarantined | Check `candidates_by_tier`/`callers` keys match the policy's chain tier names exactly (a real bug this program's own test-writing hit twice, Workstream 5) |
| A tier is unexpectedly excluded from routing | Its `RouterState` circuit is `QUARANTINED` from prior failures | Wait for `quarantine_seconds` to elapse, or construct a fresh `RouterState` |
| Cache never hits | `NoOpCache` is the default; nothing is wrong, it's the documented default (Workstream 5) | Pass an `InMemoryExactCache()` or a real cache explicitly |

## Support

This is an internal prototype with one real "support" channel: it lives
in `hermes-agent`, a git repo with normal PR/issue conventions
(`UA4200/hermes-agent`). No external support surface exists or is
proposed.
