# OpenClaw Free LLM Platform Phase 2 — Workstream 4: AI Routing

**Evidence class:** Real, tested code (44/44 passing, 7 new tests this
workstream).

## Design Principle Check (Already Satisfied, Verified Not Assumed)

The brief asks for routing that is capability-based, policy-driven,
configuration-driven, with "no provider-specific logic inside products."
Checked, not assumed: `engine.py` and `router.py` contain **zero**
references to any specific provider name — `Router`/`score_candidate`/
`rank_candidates` operate purely on `Candidate.capabilities` (sets) and
injected `ProviderCaller` callables. Every provider this workstream adds
is new *data* in `catalog.py`, not new *code* in the routing mechanism.

## Two Real Gaps Found and Closed

1. **`gemma2:2b` and `phi3:mini` are installed on `ugos-mac-mini`**
   (Workstream 3, live-checked) **but `adaptive_router.py`'s own
   `PROVIDER_CAPS` never declares `gemma2:2b`** — an installed-but-
   unroutable model on the live host itself, not a router_core-only gap.
   `catalog.EXTENDED_PROVIDER_CAPS` closes this in `router_core`'s view;
   the live host's own catalog is unchanged (that's a live-host edit,
   out of this workstream's read-only-to-the-catalog scope — flagged for
   whoever next edits `adaptive_router.py` directly).
2. **DeepSeek and Codex have zero mentions in either live routing
   system** (grepped both full source files this session — confirmed,
   not assumed). Added as genuine new capability declarations per the
   brief's "Future providers" framing.

## What Was Added

| Addition | Installed/credentialed today? | Source of sizing/capability data |
|---|---|---|
| `ollama/gemma2:2b` capability | Yes (Workstream 3) | Declared here for the first time anywhere in this system |
| `ollama/deepseek-r1:8b` | No | EL-003's same-day research (separate, unrelated sandbox program) — not independently re-verified against `ollama.com/library` this session |
| `ollama/qwen2.5-coder:7b` | No | Same source |
| `ollama/gemma3:4b` | No | Same source |
| `openai/gpt-5-codex` | Codex CLI is installed (Workstream 3); credential/routing wiring is not | Modeled as an OpenAI-family capability, not a new provider namespace — same API surface as existing `openai/*` entries |

`future_provider_candidates()` returns all four as real `Candidate`
objects with real capability sets — they score normally the moment a
real `ProviderCaller` is registered for them. Nothing about their
declaration assumes they're live.

## What Was Deliberately Not Touched

`real_alusi_candidates()` — Workstream 2's live-fidelity reference for
the actual 9-candidate auto-routed pool — is unchanged and tested as
such (`test_extension_did_not_change_live_fidelity_pool`). This
workstream's additions are additive, not a replacement of the
equivalence-proof data.

## "Codex" Specifically

Per Workstream 3's finding, Codex CLI is installed and actively used but
unrouted. This workstream makes it *representable* in `router_core`'s
catalog (capability-declared); it does **not** wire Codex CLI's own
`OPENAI_BASE_URL` to anything — that would be a live-host configuration
change to a tool someone is using right now, out of scope for a routing-
library extension and properly a Workstream 5 (Client Toolchain) or
Workstream 9 (deployment) concern if pursued.
