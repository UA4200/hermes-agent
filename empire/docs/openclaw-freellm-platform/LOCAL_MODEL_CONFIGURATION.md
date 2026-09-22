# OpenClaw Free LLM Platform Phase 2 — Workstream 3: Local LLM Ecosystem

**Evidence class:** Live_Verified, fresh discovery this session.

## Ollama Models — Unchanged

Same 6 models as Phase 1, all ~4 months old:
`qwen2.5:3b`, `qwen2.5:1.5b`, `tinyllama:latest`, `gemma2:2b`,
`phi3:mini`, `llama3.2:3b`. No new local model was added since Phase 1 —
the brief's "newly-installed local LLM ecosystem" phrasing does not refer
to new Ollama weights.

## Client Toolchain — Real, Currently Installed

| Tool | Installed? | Version | Routed through this platform? |
|---|---|---|---|
| Claude Code | Yes, `/usr/local/bin/claude` | Version check hung twice over SSH (likely an interactive update-check waiting on a TTY this session doesn't have) — presence confirmed via `which`, version not confirmed | **Yes** — `ANTHROPIC_BASE_URL=127.0.0.1:4100` routes it through `oe-proxy` → `adaptive_router.py` (Phase 1) |
| Codex CLI | Yes, `/usr/local/bin/codex` | `codex-cli 0.129.0` | **No** — plain OpenAI-direct config (`~/.codex/config.toml`: one MCP server, `gitnexus`, plus trusted-project paths; no base-URL override found) |
| "Hermes" | This repository itself (`hermes-agent`), not a separate CLI on the host | — | N/A — `hermes` command genuinely not installed on `ugos-mac-mini` (confirmed both Phase 1 and this session); the framework is used as this repo's codebase, not as a running client tool there |

**Codex CLI is actively in use right now** — `~/.codex/logs_2.sqlite` (8.8MB)
and its `-wal` file were modified at the exact time of this check,
consistent with the active interactive session noted in Phase 1's
Client Qualification report. This is a real, current finding, not
historical: **someone is using Codex CLI on this machine, unrouted,
while this program runs.**

## Research: Current Recommended Configuration Per Model Family

- **Claude Code**: `ANTHROPIC_BASE_URL` is the correct, already-used
  mechanism (Phase 1's Question 3 answer, this session) — no change
  needed to how it's wired, only to what it's wired to (Workstream 9).
- **Codex CLI**: OpenAI's Codex CLI supports an equivalent override
  (`OPENAI_BASE_URL` env var, or a `base_url` under a model provider
  entry in `config.toml`) for pointing at a custom OpenAI-compatible
  endpoint — general product knowledge, not verified against this exact
  installed version this session. **Not currently configured** — Codex's
  `config.toml` has no such override, confirmed by reading the real file.
- **Ollama**: no configuration change from Phase 1's finding
  (`OLLAMA_KV_CACHE_TYPE=q8_0` still recommended, still not set).

## Configure Each Supported Model for the Routing Platform

Per the brief's instruction to configure without removing existing
providers — this is a **design mapping**, not yet applied to either the
live host or `router_core`'s deployed state (deployment is Workstream 9):

| Model family | `router_core` mapping |
|---|---|
| Ollama (Qwen/Gemma/Phi/Llama/TinyLlama) | `providers.make_ollama_caller()` — already real, tested (Workstream 2) |
| Claude (Haiku/Sonnet/Opus) | `providers.make_anthropic_caller(api_key)` — already real, tested |
| Codex / GPT | `providers.make_openai_caller(api_key)` — already real, tested; Codex CLI itself would need its own `OPENAI_BASE_URL` pointed at whatever endpoint eventually fronts `router_core`, mirroring Claude Code's existing `ANTHROPIC_BASE_URL` pattern — not configured this workstream (design only) |
| Free-Way pool (Cohere/OpenRouter/etc.) | `providers.make_freeway_caller(api_key)` — already real, tested |
| Hermes (this framework) | N/A as a model — `hermes-agent`'s own `AIAgent` class is a *client* of routing, not a model to route to (see Phase 1's `AI_ORCHESTRATION_CAPABILITY.md` on the deferred AIAgent migration question) |

## What Was Not Done

No provider was removed. No live configuration was changed on
`ugos-mac-mini` — Codex's `config.toml` was read, not edited. Wiring
Codex CLI to any routing layer is a real, scoped follow-up (would need
its own careful rollout, same discipline as Claude Code's existing
`oe-proxy` integration) — not executed here, since it touches a tool
someone is actively using right now.
