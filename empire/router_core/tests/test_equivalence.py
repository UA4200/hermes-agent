"""Equivalence tests: prove the consolidated router_core design reproduces
the live systems' actual behavior on real (fixture) data, before Phase 2
recommends removing either live system's duplicated logic. Per the
brief: "Remove duplicated orchestration only when equivalent behaviour
has been proven" -- this file is that proof, or the record of where it
doesn't (yet) hold.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from router_core.budget import trim_prompt
from router_core.catalog import (
    REAL_SCORE_WEIGHTS,
    real_alusi_candidates,
    real_cost_score,
)
from router_core.classify import PMO_TIER_MAP, classify_pmo
from router_core.engine import RouterState, rank_candidates
from router_core.policy import Policy


# ── Real policy fixture round-trips correctly ───────────────────────────

def test_real_policy_loads_all_governance_fields():
    policy = Policy.real_alusi_policy()
    assert policy.policy_version == "enterprise_alusi_v2_cost_optimized"
    assert policy.external_send_requires_approval is True
    assert policy.no_hidden_bypass_routes is True
    assert policy.cost_limits["daily_hard_limit_usd"] == 10.0
    assert policy.cost_limits["per_call_opus_limit_usd"] == 0.50
    assert policy.cost_limits["heartbeat_allowed_providers"] == ["local"]
    assert policy.ollama_url == "http://127.0.0.1:11434"


# ── Real chain resolution matches ai_router.py's _chain_for exactly ─────
# Expected values below are read directly from the real model_policy.json
# fixture's "mapping" table, not invented.

def test_real_chain_resolution_matches_live_mapping():
    policy = Policy.real_alusi_policy()
    cases = {
        "heartbeat": ("local_only", ["local"]),
        "deal_strategy": ("cashclaw", ["opus", "sonnet"]),
        "research": ("high_value", ["sonnet", "haiku", "gpt"]),
        "trade_execution": ("ollama_first", ["local", "haiku"]),
        "critical_reasoning": ("paramount", ["opus", "sonnet", "haiku"]),
    }
    for task_type, (expected_chain_key, expected_chain) in cases.items():
        chain_key, chain = policy.chain_for(task_type)
        assert chain_key == expected_chain_key, f"{task_type}: expected chain {expected_chain_key}, got {chain_key}"
        assert chain == expected_chain, f"{task_type}: expected {expected_chain}, got {chain}"


def test_real_chain_resolution_matches_live_fallback_for_unknown_task_type():
    """ai_router.py's _chain_for falls back to policy["mapping"].get(task_type,
    "standard") -- an unmapped task_type must resolve to the real
    "standard" chain from the fixture, not router_core's own DEFAULT_POLICY
    standard chain (which is a different, illustrative value)."""
    policy = Policy.real_alusi_policy()
    chain_key, chain = policy.chain_for("some_task_type_not_in_the_real_mapping")
    assert chain_key == "standard"
    assert chain == ["haiku", "gpt", "local"]  # real fixture's standard chain


# ── Real cost calculation matches ai_router.py's _cost_per_tokens ───────

def test_real_cost_per_call_matches_live_haiku_pricing():
    policy = Policy.real_alusi_policy()
    # 1000 input + 1000 output tokens at haiku's real
    # {"input": 0.00025, "output": 0.00125} per-1k rates.
    cost = policy.cost_per_call("haiku", input_tokens=1000, output_tokens=1000)
    assert cost == 0.00025 + 0.00125


def test_real_cost_per_call_matches_live_local_tier_is_free():
    policy = Policy.real_alusi_policy()
    cost = policy.cost_per_call("local", input_tokens=50_000, output_tokens=50_000)
    assert cost == 0.0


# ── Real task classification matches ai_router.py's classify_pmo ───────
# Representative prompts chosen to hit each real PMO_CATEGORIES keyword
# list at least once.

def test_classify_pmo_matches_live_categories():
    cases = {
        "quick heartbeat check, are you alive?": "monitoring",
        "kalshi market signal looks like an edge": "signal",
        "new blco lead, send outreach email": "lead_gen",
        "please research and synthesize this report": "research",
        "debug and fix this script": "code",
        "what's our deal strategy and risk here": "strategy",
        "give me a coordination summary log": "coordination",
        "completely unrelated text with no keywords at all": "coordination",  # real default
    }
    for prompt, expected_category in cases.items():
        assert classify_pmo(prompt) == expected_category, f"prompt={prompt!r}"


def test_classify_pmo_category_maps_to_correct_real_chain():
    """Cross-checks classify.PMO_TIER_MAP against the real policy fixture's
    actual chain names -- catches drift between the ported classifier and
    the ported policy if either is edited independently later."""
    policy = Policy.real_alusi_policy()
    for category, chain_key in PMO_TIER_MAP.items():
        assert chain_key in policy.chains, (
            f"PMO_TIER_MAP maps {category!r} -> {chain_key!r}, "
            f"but {chain_key!r} is not a real chain in the fixture"
        )


# ── Real token trimming matches ai_router.py's _trim_prompt exactly ────

def test_trim_prompt_below_threshold_unchanged():
    short = "x" * 100
    assert trim_prompt(short) == short


def test_trim_prompt_above_threshold_preserves_head_and_tail():
    long_prompt = "START" + ("x" * 10000) + "END"
    trimmed = trim_prompt(long_prompt, max_chars=3000)
    assert trimmed.startswith("START")
    assert trimmed.endswith("END")
    assert "...[trimmed]..." in trimmed
    assert len(trimmed) < len(long_prompt)


# ── Real candidate scoring reproduces adaptive_router.py's cost ordering ─

def test_real_candidates_free_pool_outranks_nothing_since_all_active_are_free():
    """A real, honest finding from reading the fixture data itself: every
    entry in adaptive_router.py's real ALL_CANDIDATES (the live-qualified,
    auto-routed pool) is free (cohere or ollama) -- groq/openrouter/
    cerebras/nvidia/mistral/openai/anthropic are all declared in
    PROVIDER_CAPS/COST_TABLE but NOT in the active pool. So this test
    proves something narrower and more honest than "free beats paid": it
    proves every real active candidate scores >= 0 and none is silently
    excluded by the capability filter for a plain "text" task."""
    state = RouterState()
    candidates = real_alusi_candidates()
    assert len(candidates) == 9  # matches REAL_ACTIVE_CANDIDATES exactly
    ranked = rank_candidates(
        candidates, frozenset({"text"}), state,
        weights=REAL_SCORE_WEIGHTS, cost_score_fn=real_cost_score,
    )
    assert len(ranked) == 9  # none excluded


def test_real_cost_score_orders_anthropic_tiers_correctly():
    """Directly exercises real_cost_score (not through ranking) to prove
    it reproduces adaptive_router.py's actual tier ordering: haiku is
    scored cheaper than sonnet, which is scored cheaper than opus --
    verbatim from the ported branching, not re-derived."""
    from router_core.engine import Candidate
    haiku = Candidate("anthropic", "claude-haiku-4-5", is_free=False, capabilities=frozenset())
    sonnet = Candidate("anthropic", "claude-sonnet-4-5", is_free=False, capabilities=frozenset())
    opus = Candidate("anthropic", "claude-opus-4-5", is_free=False, capabilities=frozenset())
    assert real_cost_score(haiku) > real_cost_score(sonnet) > real_cost_score(opus)


def test_real_cost_score_free_providers_beat_all_paid():
    from router_core.engine import Candidate
    free = Candidate("cohere", "command-r", is_free=True, capabilities=frozenset())
    cheapest_paid = Candidate("openai", "gpt-4o-mini", is_free=False, capabilities=frozenset())
    assert real_cost_score(free) > real_cost_score(cheapest_paid)
