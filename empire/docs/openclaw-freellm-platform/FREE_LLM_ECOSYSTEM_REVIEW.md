# OpenClaw Free LLM Platform — Workstream 3: Ecosystem Review

**Evidence class:** Verified (tool/model landscape — sourced against
`ollama.com/library` and each project's own docs, same-day research) +
Live_Verified (this repo's own framework capabilities, read directly).

## 1. Tool/Model Landscape (summary — full research in the sibling EL-003 program)

Earlier today, a separate program (EL-003, `engineering-lab/` — an unrelated
sibling workspace, not part of this repo) did thorough live research on the
same OSS LLM ecosystem this workstream asks about: Ollama, LiteLLM, Open
WebUI, Continue.dev, Aider, OpenRouter, LM Studio, and current model
families (Qwen2.5-Coder, DeepSeek-R1, Llama 3.1/3.3, Gemma 3, Mistral),
checked against `ollama.com/library` and each project's own docs — not
repeated here to avoid duplicate work. Headlines relevant to this program:

- **Ollama** (MIT): the local runner already deployed here (v0.34.2 on this
  session's other host; this Mac Mini runs an unspecified but working
  version — confirm exact version before any upgrade decision).
- **LiteLLM** (MIT core): **not used anywhere in this system.** This
  program's stack (`ai_router.py`, `adaptive_router.py`) is bespoke Python,
  not LiteLLM-based — a real architectural choice already made, not an
  oversight. Workstream 4 should decide explicitly whether to keep it that
  way or migrate, rather than silently assuming either.
- **Qwen2.5-Coder / DeepSeek-R1 / Llama 3.1 / Gemma 3 / Mistral**: current
  as of today. This Mac Mini's actual pulled models
  (`qwen2.5:3b`, `qwen2.5:1.5b`, `gemma2:2b`, `phi3:mini`, `llama3.2:3b`,
  `tinyllama`) are **4 months old and smaller/older** than the versions
  EL-003 identified as current (e.g. `qwen2.5-coder:7b` vs. this host's
  plain `qwen2.5:3b`, `gemma2:2b` vs. current `gemma3:4b`). Worth a
  refresh — flagged for Workstream 4/5, not acted on here (read-only
  discovery).

## 2. Caching, Compression, and Inference Acceleration

Full sourced research (GitHub-API-verified maintenance status, not
README-trusted) in the companion doc:
[`CACHING_AND_ACCELERATION_RESEARCH.md`](./CACHING_AND_ACCELERATION_RESEARCH.md).
Headlines:

- **GPTCache** (semantic caching): actively maintained (commit today).
  Best fit: front `ai_router.py`'s `heartbeat`/`health_check`/`monitoring`/
  `cron_task` traffic — near-identical repeated prompts, exactly what
  semantic caching is for.
- **LLMLingua** (context compression): actively maintained (commit 12 days
  ago — verified via API since the project's own README looks stale).
  Best fit: compress the fixed context block (SOUL.md + recent events +
  empire state) `natural_response()` sends on every `high_value`/
  `paramount`-tier (Sonnet/Opus) call.
- **Ollama KV cache**: `OLLAMA_KV_CACHE_TYPE=q8_0` is a real, free,
  no-code-change win (halves KV cache memory) — not currently set on this
  deployment.
- **Anthropic/OpenAI prompt caching**: automatic at ≥1,024 tokens, no
  integration work needed beyond keeping `ai_router.py`'s prompt prefix
  stable call-to-call — worth verifying it already does this.
- **This Mac Mini is confirmed Intel** (`x86_64`, Core i5-4278U — an
  old, low-power dual-core chip), not Apple Silicon. No Metal/MLX
  acceleration applies at all; this resolves the caching research's one
  open item and rules out the MLX/speculative-decoding discussion
  entirely for this host.

## 3. A Finding Not in the Original Brief: This Repo Already Has Caching/Compression Infrastructure

`hermes-agent` (this repo, the actual framework `ugos-mac-mini`'s
production system is built alongside, not necessarily on top of) ships its
own `agent/prompt_caching.py` and `agent/context_compressor.py` modules,
governed by an explicit project policy (`AGENTS.md`): *"Hermes-Agent
ensures caching remains valid throughout a conversation... The ONLY time we
alter context is during context compression."*

**This directly matters for root cause:** the live production agent
(`alusi_gateway.py` → `ai_router.py`) does not use `hermes-agent`'s
`AIAgent` class at all — it hand-rolls system/user message construction
and calls the Anthropic/OpenAI SDKs directly. It gets none of this
framework's existing, policy-governed caching/compression handling for
free, and independently has none of its own. This is a third instance of
the same root-cause pattern from Workstream 2 (parallel, non-integrated
implementations) — except here the "other implementation" isn't a
competing router, it's the base framework's own capability sitting unused.

**Recommendation carried to Workstream 4:** evaluate whether migrating the
live agent path onto `hermes-agent`'s `AIAgent` class (gaining
`prompt_caching.py`/`context_compressor.py` for free, maintained by the
upstream project going forward) is cheaper than building equivalent
caching/compression bespoke into `ai_router.py`/`adaptive_router.py`. Not
decided here — this is a real architecture tradeoff (migration risk vs.
duplicate-maintenance cost) for Workstream 4 to weigh explicitly, not a
foregone conclusion.

## 4. Actively Maintained? — Summary Table

| Project | Verified active? | How |
|---|---|---|
| Ollama | Yes (already running, versioned) | Direct check |
| LiteLLM | Yes (per EL-003's same-day check) | Not used in this stack |
| GPTCache | **Yes — commit today** | GitHub API |
| LLMLingua | **Yes — commit 12 days ago** (README alone would mislead) | GitHub API |
| Free-Way | Yes — actively used, real traffic | Live usage.json |
| `hermes-agent`'s own `prompt_caching.py`/`context_compressor.py` | Yes — this repo, actively developed (RELEASE_v0.12.0.md etc.) | This repo's own git history |
| `native-router`, `model-cost-gateway`, `economic_guard.py`, `groq_rotator.py`, `fcc_router.py` | N/A — these are this program's own prior local experiments, not third-party projects; "maintained" doesn't apply the same way. Status: dormant (Workstream 2). |
