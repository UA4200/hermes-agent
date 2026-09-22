"""Real provider capability/cost catalog.

Ported verbatim from adaptive_router.py's TASK_CAPS/PROVIDER_CAPS/
COST_TABLE/FREE_PROVIDERS/ALL_CANDIDATES (fetched live from
ugos-mac-mini, 657 lines read in full, Phase 2 Workstream 2) -- not
reinvented or approximated. This is real production tuning data,
including its own recorded incident history (see the Groq comment
below), kept intact rather than smoothed over.

engine.py's DEFAULT_WEIGHTS remain the illustrative Phase 1 values --
SCORE_WEIGHTS here is the real ones, offered as an explicit opt-in
(real_scoring_weights()) so a caller/test can choose real fidelity
without silently changing router_core's own defaults.
"""
from __future__ import annotations

from .engine import Candidate

# ── Task capability requirements (verbatim from adaptive_router.py) ───────
TASK_CAPS: dict[str, frozenset[str]] = {
    "heartbeat":      frozenset({"text"}),
    "classify":       frozenset({"text"}),
    "summarize":      frozenset({"text"}),
    "extract":        frozenset({"text"}),
    "json_gen":       frozenset({"text", "json"}),
    "general":        frozenset({"text"}),
    "analysis":       frozenset({"text", "reasoning"}),
    "coding":         frozenset({"text", "code"}),
    "complex_coding": frozenset({"text", "code", "reasoning"}),
    "long_context":   frozenset({"text", "long_context"}),
    "tool_use":       frozenset({"text", "tools"}),
    "critical":       frozenset({"text", "reasoning"}),
}

# ── Provider capability declarations (verbatim) ────────────────────────────
PROVIDER_CAPS: dict[str, frozenset[str]] = {
    "groq/llama-3.1-8b":        frozenset({"text", "json", "code"}),
    "groq/llama-3.3-70b":       frozenset({"text", "json", "code", "reasoning"}),
    # 2026-09-14 live-qualified Free-Way/Cohere pool (adaptive_router.py's
    # own comment, kept intact -- command-r: 5/5 quality benchmark).
    "cohere/command-a":         frozenset({"text", "json", "code", "reasoning"}),
    "cohere/command-r7b":       frozenset({"text", "json", "code"}),
    "cohere/command-r":         frozenset({"text", "json", "code", "reasoning"}),
    "cohere/command-r-plus":    frozenset({"text", "json", "code", "reasoning"}),
    "openrouter/north-mini-code":            frozenset({"text", "code"}),
    "openrouter/nemotron-3-nano-30b-a3b":    frozenset({"text", "json", "reasoning"}),
    "openrouter/nemotron-3-super-120b-a12b": frozenset({"text", "json", "code", "reasoning", "long_context"}),
    "openrouter/gpt-oss-20b":     frozenset({"text", "json", "code"}),
    "openrouter/command-r-plus":  frozenset({"text", "json", "reasoning"}),
    "cerebras/zai-glm-4.7":       frozenset({"text"}),
    "nvidia/llama-3.1-nemotron-ultra": frozenset({"text", "json", "reasoning"}),
    "mistral/mistral-medium-3":   frozenset({"text", "json", "code", "reasoning"}),
    "ollama/qwen2.5:3b":          frozenset({"text", "json", "code"}),
    "ollama/qwen2.5:1.5b":        frozenset({"text", "json"}),
    "ollama/phi3:mini":           frozenset({"text", "code"}),
    "ollama/llama3.2:3b":         frozenset({"text"}),
    "ollama/tinyllama:latest":    frozenset({"text"}),
    "openai/gpt-4o-mini":         frozenset({"text", "json", "code", "reasoning", "tools"}),
    "openai/gpt-4.1-mini":        frozenset({"text", "json", "code", "tools"}),
    "openai/gpt-4o":              frozenset({"text", "json", "code", "reasoning", "tools", "long_context"}),
    "openai/gpt-4.1":             frozenset({"text", "json", "code", "reasoning", "tools", "long_context"}),
    "openai/o3-mini":             frozenset({"text", "json", "code", "reasoning", "tools"}),
    "anthropic/claude-haiku-4-5":  frozenset({"text", "json", "code", "reasoning", "tools"}),
    "anthropic/claude-sonnet-4-5": frozenset({"text", "json", "code", "reasoning", "tools", "long_context"}),
    "anthropic/claude-opus-4-5":   frozenset({"text", "json", "code", "reasoning", "tools", "long_context", "critical"}),
}

# ── Cost table, USD per 1M tokens (in, out) -- verbatim ─────────────────────
COST_TABLE: dict[str, tuple[float, float]] = {
    "groq":       (0.00, 0.00),
    "cohere":     (0.00, 0.00),
    "openrouter": (0.00, 0.00),
    "cerebras":   (0.00, 0.00),
    "nvidia":     (0.00, 0.00),
    "mistral":    (0.27, 0.27),
    "ollama":     (0.00, 0.00),
    "openai_4omini":    (0.15, 0.60),
    "openai_4dot1mini": (0.40, 1.60),
    "openai_4o":        (2.50, 10.00),
    "openai_4dot1":     (2.00, 8.00),
    "openai_o3mini":    (1.10, 4.40),
    "openai_o1mini":    (3.00, 12.00),
    "anthropic_haiku":  (0.80, 4.00),
    "anthropic_sonnet": (3.00, 15.00),
    "anthropic_opus":   (15.00, 75.00),
}

FREE_PROVIDERS: frozenset[str] = frozenset({"cohere", "openrouter", "cerebras", "nvidia", "ollama"})
# Groq: API returned 403 on 2026-08-28 test -- cost UNVERIFIED, removed
# from the free pool by the live system. Kept out of FREE_PROVIDERS here
# too, faithfully, rather than assuming it should be free because its
# catalog entry looks similar to the others.
UNVERIFIED_COST_PROVIDERS: frozenset[str] = frozenset({"groq"})

# ── Real scoring weights (verbatim from SCORE_WEIGHTS) ──────────────────────
REAL_SCORE_WEIGHTS: dict[str, float] = {
    "task_fit":    0.30,
    "quality":     0.20,
    "cost":        0.20,
    "reliability": 0.15,
    "latency":     0.10,
    "quota":       0.05,
}

# ── Real, currently-active candidate pool (verbatim ALL_CANDIDATES) ─────────
# This is deliberately smaller than PROVIDER_CAPS/COST_TABLE -- the live
# system declares capabilities for many providers but only routes to a
# pruned, live-qualified subset (groq, openrouter, cerebras, nvidia,
# mistral, openai, anthropic are all declared but NOT in this list --
# configured, not currently auto-routed to). Preserved as-is: this is a
# real operational decision on the live host, not an oversight to "fix".
REAL_ACTIVE_CANDIDATES: list[tuple[str, str]] = [
    ("cohere", "command-r"),
    ("cohere", "command-a"),
    ("cohere", "command-r-plus"),
    ("cohere", "command-r7b"),
    ("ollama", "qwen2.5:1.5b"),
    ("ollama", "qwen2.5:3b"),
    ("ollama", "phi3:mini"),
    ("ollama", "llama3.2:3b"),
    ("ollama", "tinyllama:latest"),
]


def real_cost_score(candidate: Candidate) -> float:
    """Verbatim port of adaptive_router.py's graduated cost_score
    branching (not the simplified binary free/paid default in
    engine.py's score_candidate) -- pass as engine.score_candidate's/
    rank_candidates's cost_score_fn for exact fidelity to the live
    system's actual cost preference ordering."""
    provider, model = candidate.provider, candidate.model
    if provider in FREE_PROVIDERS:
        return 1.0
    if provider in UNVERIFIED_COST_PROVIDERS:
        return 0.4
    if provider == "openai":
        if "4o-mini" in model:
            return 0.38
        if "4.1-mini" in model or "4.1-nano" in model:
            return 0.30
        if "o3-mini" in model:
            return 0.18
        if "4.1" in model:
            return 0.12
        return 0.10
    if "haiku" in model:
        return 0.28
    if "sonnet" in model:
        return 0.12
    return 0.05  # opus/expensive


def real_alusi_candidates() -> list[Candidate]:
    """Builds router_core.Candidate objects from the real, live-qualified
    provider pool -- for equivalence testing against adaptive_router.py's
    actual routing behavior, not as router_core's own default catalog
    (router_core stays product-agnostic; a caller opts into this)."""
    candidates = []
    for provider, model in REAL_ACTIVE_CANDIDATES:
        key = f"{provider}/{model}"
        caps = PROVIDER_CAPS.get(key, frozenset({"text"}))
        candidates.append(Candidate(provider, model, is_free=provider in FREE_PROVIDERS, capabilities=caps))
    return candidates
