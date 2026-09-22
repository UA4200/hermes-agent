"""Task auto-classification.

Ported verbatim from ai_router.py's PMO_CATEGORIES/PMO_TIER_MAP/classify_pmo
(fetched live from ugos-mac-mini, Phase 2 Workstream 2) -- adaptive_router.py
has no equivalent (its callers must always supply an explicit task_type),
so this is a real capability being carried into the consolidated design,
not duplicated from it.
"""
from __future__ import annotations

# Keyword lists are the real, live ones -- not paraphrased -- so
# classification behavior can be tested for equivalence against the
# live system's actual categorization.
PMO_CATEGORIES: dict[str, list[str]] = {
    "monitoring":   ["health", "status", "alive", "ping", "check", "heartbeat"],
    "signal":       ["market", "kalshi", "polymarket", "trade", "score", "p_yes", "edge"],
    "lead_gen":     ["lead", "blco", "buyer", "outreach", "email", "prospect"],
    "research":     ["research", "analyze", "synthesize", "compare", "report"],
    "code":         ["code", "debug", "fix", "build", "deploy", "script"],
    "strategy":     ["strategy", "plan", "decision", "risk", "deal"],
    "coordination": ["summary", "log", "coordinate", "route", "dispatch"],
}

PMO_TIER_MAP: dict[str, str] = {
    "monitoring":   "local_only",
    "signal":       "ollama_first",
    "lead_gen":     "haiku_first",
    "research":     "high_value",
    "code":         "high_value",
    "strategy":     "paramount",
    "coordination": "cheap",
}


def classify_pmo(prompt: str, task_type: str | None = None, known_mappings: dict | None = None) -> str:
    """Classify a prompt into a PMO category. Mirrors ai_router.py's
    classify_pmo exactly: an explicit task_type that's already a known
    mapping key wins outright (no keyword scan needed); otherwise the
    first keyword match wins (dict order = priority order, same as the
    live system, since Python dicts preserve insertion order); with no
    match, falls back to "coordination" -- the same default the live
    system uses, not a new default invented here."""
    if task_type and known_mappings and task_type in known_mappings:
        return task_type
    prompt_lower = prompt.lower()
    for category, keywords in PMO_CATEGORIES.items():
        if any(kw in prompt_lower for kw in keywords):
            return category
    return "coordination"
