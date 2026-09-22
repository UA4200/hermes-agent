# OpenClaw Free LLM Platform — Workstream 9: AI Orchestration Capability

**Status: design + prototype, not yet promoted anywhere.** The brief asks
for this to become "a permanent reusable EOS capability." That phrase has
a specific, real meaning in the sibling `engineering-operating-system`
repo (encountered during the earlier EL-003 program, same broader
context): a capability is only formally registered
(`capabilities/CAP-NNNN.md`, `registries/CAPABILITY_REGISTRY.md`) after it
clears `docs/CAPABILITY_PROMOTION_CRITERIA.md`'s 8 criteria — a
Chief-Architect-level decision, not something a single program
unilaterally performs, per that repo's own "Nothing Enters EOS Without
Proving Value" principle. `router_core` (Workstream 5) is a tested
prototype, not yet through a staged production rollout
(`OPENCLAW_PLATFORM_ARCHITECTURE.md`'s migration plan, not executed).
**This workstream therefore defines the capability's shape and scope —
ready for a future formal promotion decision once the prototype has real
production mileage — rather than registering it as done today.**

## Capability Name

AI Orchestration (working name, matching the brief).

## Scope: What It Abstracts

Per the brief's responsibility list, mapped to what actually exists today
vs. what's designed but not built:

| Responsibility | Status |
|---|---|
| Model routing | **Built, tested** — `router_core.Router` (Workstream 5) |
| Task classification | **Built, tested** — `router_core.policy.Policy.chain_for` |
| Provider abstraction | **Built, tested** — `ProviderCaller` protocol, any callable |
| LiteLLM integration | **Deliberately not built** — this stack doesn't use LiteLLM (Workstream 4's explicit decision) |
| Ollama integration | **Built (design)** — `Candidate`/caller pattern supports it; real Ollama caller not wired in prototype |
| OpenAI-compatible provider integration | **Built (design)** — same pattern |
| Future provider adapters | **Built (design)** — adding a provider is a dict entry, not new routing code (Workstream 5) |
| Prompt caching | **Hook built, not implemented** — `cache.py`'s `SemanticCache` protocol + `NoOpCache`/`InMemoryExactCache`; real GPTCache integration deferred (Workstream 3/5) |
| Semantic caching | Same as above |
| Context compression | **Hook built, not implemented** — `compress.py`'s `Compressor` protocol; real LLMLingua integration deferred |
| Token budgeting | **Not built** — `ai_router.py`'s `_trim_prompt` exists on the live host but wasn't ported into `router_core` |
| Cost optimization | **Partially built** — `engine.py`'s free-vs-paid cost scoring; the *enforcement* gap from Workstream 6/7 is not yet fixed anywhere |
| Local-first execution | **Built, tested** — `score_candidate`'s cost weighting prefers free/local by default |
| Premium escalation | **Built, tested** — chain-based escalation in both `router_core` and both live systems |
| Fallback routing | **Built, tested** — `Router.route`'s try-next-candidate loop |
| Model health monitoring | **Built, tested** — `RouterState`'s circuit breaker |
| Provider failover | **Built, tested** — same mechanism |
| Telemetry | **Not built in `router_core`** — both live systems have their own (JSONL logs); not unified in the prototype |
| Capability metrics | **Not built** |
| Configuration management | **Built, tested** — `Policy.from_file`/`from_dict` |
| Capability registry integration | **N/A this pass** — see status note above |
| Knowledge Graph integration | **Not built** — no connection to `empire/knowledge-governance/` attempted |
| Engineering Memory integration | **N/A** — that's an `engineering-operating-system` concept, not this repo's |
| Documentation | **This document and its siblings** |
| Reusable APIs | **Built** — `Router`, `Policy`, `Candidate`, `RouterState` are the public surface |
| Reusable templates | **Built** — `DEFAULT_POLICY` in `policy.py` is a template a new deployment starts from |
| Reusable installer | See `AI_ORCHESTRATION_INSTALLER.md` |
| Reusable configuration | See `AI_ORCHESTRATION_CONFIGURATION.md` |
| Reusable diagnostics | **Partially** — the live host's own `empire_efficiency.py` (Workstream 7) is the real diagnostics tool in production use today; not yet generalized into `router_core` itself |
| Reusable validation | **Built** — the 18-test suite (Workstream 5), extensible to new providers/policies |

## Where It Would Sit (If Promoted)

Not decided by this program. Two real options exist, both legitimate,
neither chosen here:
1. Stay in `hermes-agent/empire/router_core/` — scoped to this specific
   empire, reusable by copying, not by formal dependency.
2. Become an actual `hermes-agent` plugin (per `AGENTS.md`'s plugin
   surface — `plugins/<name>/` with a `register(ctx)` function) — would
   make it reusable across *any* hermes-agent deployment, not just this
   one, at the cost of needing to fit the plugin lifecycle hooks
   (`pre_llm_call`/`post_llm_call` etc.) rather than being called
   directly. This is the more genuinely "reusable EOS capability"-shaped
   option, and the one worth pursuing if this program continues past
   prototype stage.

## Not Done Here

Per the brief's own constraint ("Do NOT: Duplicate orchestration logic
across products") and this program's running discipline: no code was
deployed, no capability was registered anywhere, no live routing was
changed. This document states the target shape; `AI_ORCHESTRATION_
ARCHITECTURE.md`, `_INSTALLER.md`, and `_CONFIGURATION.md` detail it
further without executing a rollout.
