# Caching & Acceleration Research (supporting Workstream 3)

**Scope:** prompt caching, semantic caching, KV caching, context compression,
inference acceleration. Tool/model comparisons (Ollama, LiteLLM, Open WebUI,
Continue.dev, Aider, OpenRouter, LM Studio, Qwen/DeepSeek/Llama/Gemma/Mistral)
are covered elsewhere and intentionally not duplicated here.

**Method:** live web search + GitHub API commit checks, 2026-09-22. Every
maintenance-status claim below is backed by an actual latest-commit date
pulled from the GitHub API, not inferred from README text or star count.

---

## 1. Prompt Caching (provider-side)

**Anthropic:** cache reads cost $0.30/M tokens vs. $3.00/M fresh; cache
writes cost 1.25x base rate; break-even after 2 reads. Minimum 1,024 tokens
per cache checkpoint, up to 4 checkpoints/request. TTL: 5 min default,
extendable to 1 hour with repeat hits. Reports up to 90% cost reduction and
85% latency reduction on cached prefixes. [Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

**OpenAI:** fully automatic on prompts ≥1,024 tokens, no caller-side
config — cached portion billed at 10% of normal input price (90% off).
Cache duration extended to up to 24 hours as of a May 2026 update. Shows up
in the response's `usage.cached_tokens` field. [OpenAI API docs](https://developers.openai.com/api/docs/guides/prompt-caching)

**Applying this to this system's bespoke Python routers (`ai_router.py`,
`adaptive_router.py`) — neither LiteLLM nor Free-Way's caching applies
since this stack doesn't run LiteLLM:**
- For the `haiku`/`sonnet`/`opus` tiers in `ai_router.py`: this is free
  money already available — Anthropic's cache activates automatically once
  a request crosses 1,024 tokens; the router doesn't need to do anything
  except make sure repeated calls reuse an identical prompt prefix (e.g.,
  keep `system_msg`'s SOUL.md content and static instructions first, put
  the variable per-call content last) so the cacheable prefix stays stable
  call to call. Worth checking whether `ai_router.py`'s current prompt
  construction already does this — not verified in this pass.
- For local Ollama calls: Ollama has no equivalent "billed" cache concept
  (nothing to charge), but see §3 (KV cache) for the local analog.
- For Free-Way's free-tier providers (Cohere, Groq, NVIDIA, etc.): caching
  support varies by provider and isn't something Free-Way itself adds — it
  would need a caching layer built into `adaptive_router.py` (e.g., a
  simple exact-match or short-TTL response cache keyed on prompt hash) if
  cost/latency reduction on those routes matters. Not present today (not
  found in `adaptive_router.py`'s functions reviewed in Workstream 2).

## 2. Semantic Caching

**GPTCache** (`zilliztech/GPTCache`, MIT): embedding-based cache — converts
queries to embeddings, does similarity search against a vector store, and
returns a cached response for semantically-similar (not just identical)
prior queries. **Actively maintained — most recent commit 2026-09-22 (the
same day as this research), verified via the GitHub API, not the README.**
Integrates with LangChain and llama_index; installs via `pip install
gptcache`. A relevant recent addition per commit history: "cache reuse
compatibility benchmarks."

**Applying it here:** semantic caching is most valuable for the
high-repeat-question surface — `ai_router.py`'s `heartbeat`/`health_check`/
`monitoring`/`cron_task` task types (all mapped to `local_only` in
`model_policy.json`) are exactly this pattern: near-identical prompts sent
repeatedly. A lightweight GPTCache layer in front of the `local` tier could
cut a meaningful fraction of the 76,981 logged local Ollama calls (Workstream
1) to near-zero latency for repeat queries, at the cost of running an
embedding model + vector store locally (additional resource footprint —
sizing not evaluated here).

## 3. KV Caching (inference-engine level — directly relevant to Ollama)

KV (key/value) caching is how the underlying inference engine (llama.cpp,
which Ollama wraps) avoids recomputing attention over the full context on
every generated token — it's inference-level, not something Free-Way,
`ai_router.py`, or `adaptive_router.py` can add or remove; it's about how
Ollama itself is configured.

**Ollama exposes real user-facing control:** `OLLAMA_KV_CACHE_TYPE`
environment variable — `f16` (default, full precision), `q8_0` (8-bit,
halves KV cache memory, negligible quality loss), `q4_0` (4-bit, quarter
memory, modest quality loss). Combined with flash attention, `q8_0`
roughly doubles the usable context length before hitting memory limits.
[ModelPiper writeup](https://modelpiper.com/blog/ollama-kv-cache-quantization),
[Mitja Martini](https://mitjamartini.com/posts/ollama-kv-cache-quantization/).
Not on by default — must be set explicitly.

A newer option, `tq3`/`tq4` (TurboQuant, a Google research technique using
randomized Hadamard rotation before quantizing key vectors — [arXiv
2504.19874](https://arxiv.org/abs/2504.19874), ICLR 2026), exists as an
Ollama PR (`ollama/ollama#15090`) but **the underlying llama.cpp PR
(#21089) was closed without merging in 2026 — no shipping timeline.** Do
not plan on `tq3`/`tq4` being available; `q8_0` is the current, proven,
shippable option.

**Recommendation:** set `OLLAMA_KV_CACHE_TYPE=q8_0` on this deployment —
free memory/context-length win, no code change required, not currently set
(per Workstream 1's `OLLAMA_KV_CACHE_TYPE` was not found among the env vars
inspected — worth confirming directly before assuming it's unset).

## 4. Context Compression

**LLMLingua** (`microsoft/LLMLingua`, MIT, 6,156 stars): compresses prompts
up to 20x with claimed minimal performance loss; also compresses KV-cache.
Six papers in the series from EMNLP 2023 through CoLM 2025.
**Actively maintained — most recent commit 2026-09-10 (12 days before this
research), verified via GitHub API** (the project's own README/news section
reads as stale, last visible announcement Dec 2024 — the API check is what
actually confirms currency; don't trust the README's news section alone
for this kind of check). [microsoft/LLMLingua](https://github.com/microsoft/LLMLingua)

**Applying it here:** most relevant to `ai_router.py`'s `research` and
`critical_reasoning` task types (routed to `high_value`/`paramount` chains
— i.e., the expensive Sonnet/Opus tiers), where large context (SOUL.md,
recent events, empire state JSON — all loaded into `natural_response()`'s
system/user messages per Workstream 1) is sent on every call regardless of
whether the current request actually needs all of it. Compressing that
fixed context block before the expensive tiers would reduce cost on
exactly the calls where cost matters most. Not currently implemented
anywhere in the reviewed routers.

## 5. Inference Acceleration (local Ollama specifically)

**Chip architecture note:** not confirmed this pass whether `ugos-mac-mini`
is Apple Silicon or Intel (`sw_vers` doesn't report chip architecture) —
Workstream 1 found an MLX library load failure on every Ollama call
(`libmlxc.dylib` not found), which is *consistent with* Apple Silicon
hardware trying and failing to use MLX acceleration, but isn't conclusive
proof by itself. Confirm with `uname -m` (`arm64` = Apple Silicon) before
acting on the recommendations below.

**If Apple Silicon:** MLX (Apple's own ML framework) measurably outperforms
llama.cpp's Metal backend for speculative decoding specifically — one
benchmark (M4 Pro, Qwen 3.6 27B) showed MTPLX going from ~7 tok/s to
18.3 tok/s (2.6x) at draft depth 3, versus llama.cpp's Metal MTP managing
only 10.5 tok/s on the same hardware, because MLX fuses draft+verify into
one compute graph while llama.cpp's Metal backend pays a per-token kernel-
dispatch cost. **However:** a separate, more current finding
(`ggml-org/llama.cpp#23752`) reports MTP speculative decoding on Metal is
currently a **net loss** at every tested configuration (up to 28% slower
at higher draft ceilings) due to that same dispatch overhead outweighing
the speculative gain — so speculative decoding via llama.cpp/Ollama's
Metal path is not recommended today; it would require switching to an
MLX-based runtime instead of Ollama to realize the gain, a bigger change
than tuning Ollama's existing config.

**If Intel/CPU-only:** no Metal/MLX acceleration applies at all; the KV
cache quantization in §3 (`q8_0`) is the most impactful lever available
without a hardware change, plus standard GGUF model-size selection
(smaller/more quantized model weights = faster CPU inference, at a quality
cost) — already the operative constraint noted in this session's separate
EL-003 evaluation on a different (confirmed Intel) host.

**Multi-Token Prediction (MTP), 2026 context:** newer model releases are
increasingly trained with built-in extra prediction heads that draft their
own next few tokens, removing the need for a separate draft model
entirely — worth watching as models in the qualified stack (Qwen2.5-Coder,
DeepSeek-R1, etc. — see the separate model research) get newer point
releases, but not something to build infrastructure around today.

---

## Summary Table

| Technique | Actively maintained? (verified) | Applies to this stack how |
|---|---|---|
| Anthropic prompt caching | N/A (provider feature, not a project) | Automatic ≥1,024 tokens; verify `ai_router.py`'s prompt construction keeps a stable prefix |
| OpenAI prompt caching | N/A (provider feature) | Automatic ≥1,024 tokens, zero config |
| GPTCache (semantic cache) | **Yes — commit today, 2026-09-22** | Front the `local_only`-tier heartbeat/health/cron traffic |
| Ollama KV cache quantization | N/A (built into Ollama) | Set `OLLAMA_KV_CACHE_TYPE=q8_0`; `tq3/tq4` NOT shippable (upstream llama.cpp PR closed) |
| LLMLingua (context compression) | **Yes — commit 12 days ago** (README looks stale; API says otherwise) | Compress fixed context blocks before Sonnet/Opus-tier calls |
| MLX speculative decoding | Active research area, mixed current results | Only if confirmed Apple Silicon; llama.cpp/Metal MTP is currently a net loss per upstream issue #23752 |
