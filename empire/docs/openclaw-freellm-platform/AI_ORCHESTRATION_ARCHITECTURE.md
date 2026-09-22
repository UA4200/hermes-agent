# OpenClaw Free LLM Platform — Workstream 9: AI Orchestration Architecture

Generalizes `OPENCLAW_PLATFORM_ARCHITECTURE.md` (Workstream 4, which was
about *this specific empire's* two live routers) into the reusable shape
`router_core` actually implements. See that document for the
Alusi-specific consolidation plan; this one describes the capability in
the abstract.

```
                     Caller (any process, any product)
                                  │
                                  ▼
                     ┌────────────────────────┐
                     │   router_core.Router     │
                     │  .route(task_type,prompt) │
                     └────────────┬────────────┘
                                  │
        ┌──────────────┬──────────┴──────────┬──────────────┐
        ▼              ▼                     ▼              ▼
   SemanticCache   Policy.chain_for     RouterState/     Compressor
   (cache.py)         (policy.py)      score_candidate    (compress.py)
                                         (engine.py)
                                              │
                                              ▼
                                    ProviderCaller callables
                                    (caller supplies these —
                                     Ollama, Free-Way, Anthropic,
                                     OpenAI, or anything else with
                                     the same (model, prompt) -> text
                                     shape)
```

## Why This Shape Generalizes

Every dependency a caller must supply (`Policy`, `Candidate` list,
`callers` dict) is plain data or a plain callable — nothing in
`router_core` imports a specific provider SDK, a specific product's
config format, or a specific deployment's file paths. A second product
(e.g. a future EOS Trading Project, per the brief's stated reuse targets)
adopts this by writing its own policy JSON and provider callables, not by
forking or modifying `router_core` itself. This is what "capability-first,
provider-independent, no vendor lock-in" means concretely for this
component.

## Explicit Non-Goals (This Pass)

- Not a message-format translator (unlike `ollama-anthropic-bridge` or
  Free-Way, which normalize between Anthropic/OpenAI wire formats) —
  `router_core` routes at the `(model, prompt) -> text` level, one layer
  above wire-format concerns. A product needing format translation
  supplies a caller that does it internally.
- Not a replacement for either live router on `ugos-mac-mini` today — see
  `OPENCLAW_PLATFORM_ARCHITECTURE.md`'s staged migration plan for what
  that would actually require.
