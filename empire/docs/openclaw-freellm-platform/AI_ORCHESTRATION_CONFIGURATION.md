# OpenClaw Free LLM Platform — Workstream 9: AI Orchestration Configuration

## Policy

A `Policy` is three plain dicts (`policy.py`):

```json
{
  "chains": {
    "local_only": ["local"],
    "cheap": ["local", "haiku"],
    "high_value": ["sonnet", "haiku"]
  },
  "mapping": {
    "heartbeat": "local_only",
    "research": "high_value"
  },
  "cost_limits": {
    "daily_hard_limit_usd": 10.0
  }
}
```

Load it with `Policy.from_file("policy.json")` or `Policy.from_dict(...)`.
Unknown `task_type`s fall back to a configurable default chain
(`fallback_chain="standard"` by default) rather than raising — matching
`ai_router.py`'s own `.get(task_type, "standard")` convention (Workstream
5), so a caller can add new task types without every code path needing to
know about them upfront.

**Note:** `cost_limits` is accepted and stored by `Policy` but **not yet
enforced by `Router`** — this mirrors the real gap found in `ai_router.py`
itself (Workstream 6). Any deployment relying on `router_core` for real
budget enforcement needs to add that check before treating the field as
load-bearing; it's currently documentation, not code, exactly like its
live-host counterpart.

## Candidates

A dict mapping policy tier names to `Candidate` objects (`engine.py`):

```python
from router_core.engine import Candidate

candidates = {
    "local": Candidate("ollama", "llama3.2:3b", is_free=True,
                        capabilities=frozenset({"text"})),
    "haiku": Candidate("anthropic", "claude-haiku-4-5", is_free=False,
                        capabilities=frozenset({"text"})),
}
```

`capabilities` gates eligibility (`score_candidate` returns `-1.0` if a
task's required capabilities aren't a subset) — same mechanism as
`adaptive_router.py`'s `TASK_CAPS`/`PROVIDER_CAPS` (Workstream 5), not
carried over with its actual tuned values.

## Callers

A dict mapping tier name to a `(model: str, prompt: str) -> str` callable.
Real deployments plug in their own provider SDK calls here — `router_core`
deliberately has no built-in Ollama/Anthropic/OpenAI/Free-Way client code,
so there's nothing to configure with API keys or base URLs at the library
level. This is a design choice, not an oversight: it keeps `router_core`
credential-free and testable without secrets (Workstream 5's 18 tests
prove this).

## Tuning the Scoring Engine

`RouterState`'s three knobs (`engine.py`):

| Parameter | Default | Meaning |
|---|---|---|
| `degrade_after` | 2 | Consecutive failures before `HEALTHY → DEGRADED` |
| `quarantine_after` | 4 | Consecutive failures before `DEGRADED → QUARANTINED` |
| `quarantine_seconds` | 300 | Cooldown before a `RETEST` attempt is allowed |

`score_candidate`'s six weights (`DEFAULT_WEIGHTS`) sum to 1.0 and can be
overridden per call — not tuned against real traffic in this prototype
(Workstream 5's explicit scope limit).

## What Is Not Configurable (Yet)

Persistence (`RouterState` is in-memory only — a file-backed subclass,
matching `adaptive_router.py`'s own `router_state.json` pattern, is a
straightforward extension not built here), telemetry sink, and the
cost-limit enforcement noted above.
