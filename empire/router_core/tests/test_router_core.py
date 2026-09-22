"""Tests for router_core. All provider calls are fake -- no network, no
credentials, hermetic and fast. Proves the design composes correctly; does
not prove parity with either live system on ugos-mac-mini (see README.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # empire/

from router_core.cache import InMemoryExactCache, NoOpCache
from router_core.compress import NoOpCompressor, TruncatingCompressor
from router_core.engine import Candidate, RouterState, rank_candidates, score_candidate
from router_core.policy import Policy
from router_core.router import Router


# ── policy.py ────────────────────────────────────────────────────────────

def test_policy_resolves_known_task_type():
    policy = Policy.default()
    chain_key, tiers = policy.chain_for("heartbeat")
    assert chain_key == "local_only"
    assert tiers == ["local"]


def test_policy_falls_back_for_unknown_task_type():
    policy = Policy.default()
    chain_key, tiers = policy.chain_for("some_never_seen_task_type")
    assert chain_key == "standard"
    assert tiers == policy.chains["standard"]


# ── engine.py ────────────────────────────────────────────────────────────

def test_score_candidate_rejects_missing_capability():
    state = RouterState()
    candidate = Candidate("ollama", "tinyllama", is_free=True, capabilities=frozenset({"text"}))
    score = score_candidate(candidate, frozenset({"text", "code"}), state)
    assert score == -1.0


def test_score_candidate_prefers_free_over_paid():
    state = RouterState()
    free = Candidate("ollama", "llama3.2:3b", is_free=True, capabilities=frozenset({"text"}))
    paid = Candidate("openai", "gpt-4o", is_free=False, capabilities=frozenset({"text"}))
    free_score = score_candidate(free, frozenset({"text"}), state)
    paid_score = score_candidate(paid, frozenset({"text"}), state)
    assert free_score > paid_score


def test_circuit_breaker_degrades_then_quarantines():
    state = RouterState(degrade_after=2, quarantine_after=4, quarantine_seconds=9999)
    key = "flaky/model"
    assert state.get(key).circuit_state == "HEALTHY"
    state.record_failure(key)
    state.record_failure(key)
    assert state.get(key).circuit_state == "DEGRADED"
    state.record_failure(key)
    state.record_failure(key)
    assert state.get(key).circuit_state == "QUARANTINED"
    assert state.is_healthy(key) is False


def test_circuit_breaker_recovers_on_success():
    state = RouterState(degrade_after=1, quarantine_after=99)
    key = "recovering/model"
    state.record_failure(key)
    assert state.get(key).circuit_state == "DEGRADED"
    state.record_success(key, latency_ms=100)
    assert state.get(key).circuit_state == "HEALTHY"


def test_rank_candidates_excludes_quarantined():
    # degrade_after=1, quarantine_after=1: each record_failure() call can
    # only advance the state machine one step (HEALTHY->DEGRADED or
    # DEGRADED->QUARANTINED, mirrored from adaptive_router.py's elif
    # chain) -- so two failures, not one, are needed to reach QUARANTINED.
    state = RouterState(degrade_after=1, quarantine_after=1, quarantine_seconds=9999)
    good = Candidate("ollama", "good", is_free=True, capabilities=frozenset({"text"}))
    bad = Candidate("ollama", "bad", is_free=True, capabilities=frozenset({"text"}))
    state.record_failure("ollama/bad")
    state.record_failure("ollama/bad")
    assert state.get("ollama/bad").circuit_state == "QUARANTINED"
    ranked = rank_candidates([good, bad], frozenset({"text"}), state)
    assert [c.model for c in ranked] == ["good"]


# ── cache.py / compress.py ───────────────────────────────────────────────

def test_noop_cache_always_misses():
    cache = NoOpCache()
    cache.put("hello", "world")
    assert cache.get("hello") is None


def test_exact_cache_hits_on_identical_prompt():
    cache = InMemoryExactCache()
    cache.put("what time is it", "cached answer")
    assert cache.get("what time is it") == "cached answer"
    assert cache.get("a different prompt") is None


def test_noop_compressor_returns_input_unchanged():
    compressor = NoOpCompressor()
    text = "x" * 10000
    assert compressor.compress(text) == text


def test_truncating_compressor_reduces_length():
    compressor = TruncatingCompressor()
    text = "x" * 1000
    compressed = compressor.compress(text, target_ratio=0.5)
    assert len(compressed) == 500


# ── router.py (integration) ──────────────────────────────────────────────

def _make_router(callers, cache=None, compressor=None, **kwargs):
    policy = Policy.default()
    candidates = {
        "local": Candidate("ollama", "llama3.2:3b", is_free=True, capabilities=frozenset({"text"})),
        "haiku": Candidate("anthropic", "claude-haiku-4-5", is_free=False, capabilities=frozenset({"text"})),
        "sonnet": Candidate("anthropic", "claude-sonnet-4-5", is_free=False, capabilities=frozenset({"text"})),
    }
    return Router(policy, candidates, callers, cache=cache, compressor=compressor, **kwargs)


def test_route_calls_first_healthy_candidate_in_chain():
    calls = []

    def fake_local(model, prompt):
        calls.append(model)
        return f"local response to: {prompt}"

    router = _make_router({"local": fake_local})
    result = router.route("heartbeat", "ping")

    assert result.success
    assert result.provider == "ollama"
    assert result.text == "local response to: ping"
    assert calls == ["llama3.2:3b"]


def test_route_escalates_on_failure():
    def failing_local(model, prompt):
        raise ConnectionError("ollama is down")

    def working_haiku(model, prompt):
        return "haiku saved the day"

    router = _make_router({"local": failing_local, "haiku": working_haiku})
    result = router.route("standard", "hello")

    assert result.success
    assert result.provider == "anthropic"
    assert result.model == "claude-haiku-4-5"
    assert any("FAILED" in a for a in result.attempts)


def test_route_returns_failure_when_all_candidates_fail():
    def always_fails(model, prompt):
        raise RuntimeError("nope")

    router = _make_router({"local": always_fails, "haiku": always_fails})
    result = router.route("standard", "hello")

    assert not result.success
    assert result.error == "all_candidates_failed"


def test_route_uses_cache_before_calling_any_provider():
    calls = []

    def fake_local(model, prompt):
        calls.append(model)
        return "fresh response"

    cache = InMemoryExactCache()
    cache.put("ping", "cached response")
    router = _make_router({"local": fake_local}, cache=cache)

    result = router.route("heartbeat", "ping")

    assert result.cache_hit is True
    assert result.text == "cached response"
    assert calls == []  # provider never called


def test_route_compresses_long_prompts_on_expensive_chains_only():
    seen_prompts = []

    def fake_sonnet(model, prompt):
        seen_prompts.append(prompt)
        return "ok"

    compressor = TruncatingCompressor()
    router = _make_router(
        {"sonnet": fake_sonnet},
        compressor=compressor,
        compress_threshold_chars=100,
    )

    long_prompt = "x" * 1000
    # "research" maps to the "high_value" chain in DEFAULT_POLICY.
    result = router.route("research", long_prompt)

    assert result.compressed is True
    assert len(seen_prompts[0]) < len(long_prompt)


def test_route_does_not_compress_short_prompts():
    seen_prompts = []

    def fake_sonnet(model, prompt):
        seen_prompts.append(prompt)
        return "ok"

    compressor = TruncatingCompressor()
    router = _make_router(
        {"sonnet": fake_sonnet}, compressor=compressor, compress_threshold_chars=10000
    )

    short_prompt = "hello"
    result = router.route("research", short_prompt)

    assert result.compressed is False
    assert seen_prompts[0] == short_prompt


def test_route_does_not_compress_cheap_chains_even_if_long():
    """local_only/cheap chains aren't in compress_task_types by default --
    compression is reserved for the expensive tiers where cost matters
    most (Workstream 3's recommendation)."""
    seen_prompts = []

    def fake_local(model, prompt):
        seen_prompts.append(prompt)
        return "ok"

    compressor = TruncatingCompressor()
    router = _make_router(
        {"local": fake_local}, compressor=compressor, compress_threshold_chars=10
    )

    long_prompt = "x" * 1000
    result = router.route("heartbeat", long_prompt)

    assert result.compressed is False
    assert seen_prompts[0] == long_prompt
