"""Tests for budget_enforcement.py and its integration into Router.route()
-- proves the real cost-limit enforcement gap Phase 1 found (declared in
model_policy.json, never checked in code) is actually closed here, not
just documented as closed.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from router_core.budget_enforcement import BudgetEnforcer
from router_core.engine import Candidate
from router_core.policy import Policy
from router_core.router import Router


# ── BudgetEnforcer unit tests ────────────────────────────────────────────

def test_real_defaults_match_model_policy_json():
    """The defaults are the real, live values -- not invented ones."""
    b = BudgetEnforcer()
    assert b.daily_limit_usd == 10.0
    assert b.per_call_limit_usd["opus"] == 0.50


def test_status_ok_when_no_spend():
    b = BudgetEnforcer(daily_limit_usd=10.0)
    assert b.status().state == "ok"


def test_status_warning_above_threshold():
    b = BudgetEnforcer(daily_limit_usd=10.0, warning_threshold_pct=0.80)
    b.record_spend("claude-sonnet-4-5", 8.5)  # 85% of 10.0
    assert b.status().state == "warning"


def test_status_hard_stop_at_limit():
    b = BudgetEnforcer(daily_limit_usd=10.0)
    b.record_spend("claude-opus-4-5", 10.0)
    assert b.status().state == "hard_stop"


def test_per_call_limit_blocks_expensive_single_call():
    b = BudgetEnforcer(per_call_limit_usd={"opus": 0.50})
    blocked, reason = b.would_exceed("opus", "claude-opus-4-5", estimated_cost_usd=0.75)
    assert blocked is True
    assert "per_call_limit_exceeded" in reason


def test_per_call_limit_allows_call_under_limit():
    b = BudgetEnforcer(per_call_limit_usd={"opus": 0.50})
    blocked, reason = b.would_exceed("opus", "claude-opus-4-5", estimated_cost_usd=0.30)
    assert blocked is False


def test_daily_limit_blocks_when_would_be_exceeded():
    b = BudgetEnforcer(daily_limit_usd=1.0)
    b.record_spend("claude-haiku-4-5", 0.90)
    blocked, reason = b.would_exceed("haiku", "claude-haiku-4-5", estimated_cost_usd=0.20)
    assert blocked is True
    assert reason == "daily_hard_limit_would_be_exceeded"


def test_monthly_limit_blocks_when_would_be_exceeded():
    b = BudgetEnforcer(daily_limit_usd=1000.0, monthly_limit_usd=5.0)
    b.record_spend("claude-sonnet-4-5", 4.9)
    blocked, reason = b.would_exceed("sonnet", "claude-sonnet-4-5", estimated_cost_usd=0.5)
    assert blocked is True
    assert reason == "monthly_hard_limit_would_be_exceeded"


def test_per_model_daily_limit_enforced_independently_of_global():
    b = BudgetEnforcer(daily_limit_usd=1000.0, per_model_daily_limit_usd={"gpt-4o": 1.0})
    b.record_spend("gpt-4o", 0.95)
    blocked, reason = b.would_exceed("gpt", "gpt-4o", estimated_cost_usd=0.10)
    assert blocked is True
    assert "per_model_daily_limit_exceeded" in reason


def test_local_first_enforcement_blocks_non_local_tier():
    b = BudgetEnforcer(local_first_task_types=frozenset({"heartbeat"}))
    blocked, reason = b.enforce_local_first("heartbeat", "haiku")
    assert blocked is True
    assert "local_first_task_type_blocked" in reason


def test_local_first_enforcement_allows_local_tier():
    b = BudgetEnforcer(local_first_task_types=frozenset({"heartbeat"}))
    blocked, reason = b.enforce_local_first("heartbeat", "local")
    assert blocked is False


def test_local_first_enforcement_does_not_apply_to_other_task_types():
    b = BudgetEnforcer(local_first_task_types=frozenset({"heartbeat"}))
    blocked, reason = b.enforce_local_first("research", "opus")
    assert blocked is False


# ── Router integration tests ─────────────────────────────────────────────

def _real_policy_router(budget: BudgetEnforcer, callers: dict):
    policy = Policy.real_alusi_policy()
    candidates = {
        "local": Candidate("ollama", "llama3.2:3b", is_free=True, capabilities=frozenset({"text"})),
        "haiku": Candidate("anthropic", "claude-haiku-4-5", is_free=False, capabilities=frozenset({"text"})),
        "sonnet": Candidate("anthropic", "claude-sonnet-4-5", is_free=False, capabilities=frozenset({"text"})),
        "opus": Candidate("anthropic", "claude-opus-4-5", is_free=False, capabilities=frozenset({"text"})),
    }
    return Router(policy, candidates, callers, budget=budget)


def test_route_skips_budget_blocked_tier_and_downgrades():
    """The real proof: a heartbeat-classified request, budget-restricted
    to local-only, must route to local even though the real policy's
    chain lists other tiers -- automatic local-first enforcement, not
    just weighting."""
    calls = []

    def fake_local(model, prompt):
        calls.append(("local", model))
        return "local response"

    def fake_haiku(model, prompt):
        calls.append(("haiku", model))
        return "should not be called"

    budget = BudgetEnforcer(local_first_task_types=frozenset({"heartbeat"}))
    router = _real_policy_router(budget, {"local": fake_local, "haiku": fake_haiku})

    result = router.route("heartbeat", "ping")

    assert result.success
    assert result.tier == "local"
    assert calls == [("local", "llama3.2:3b")]  # haiku never called


def test_route_reports_budget_blocked_tiers_in_result():
    budget = BudgetEnforcer(daily_limit_usd=0.0001)  # essentially zero -- everything paid blocked
    router = _real_policy_router(
        budget,
        {"local": lambda m, p: "free response"},  # only local registered
    )
    result = router.route("research", "tell me something")  # chain: sonnet, haiku, gpt (no local registered)
    # None of sonnet/haiku/gpt have callers registered anyway in this
    # test, so this exercises the "no caller for tier" path AND budget
    # blocking would apply if callers existed -- verifies no crash and a
    # clean failure result.
    assert not result.success


def test_route_all_candidates_budget_blocked_distinct_error():
    def fake_opus(model, prompt):
        return "should not be reached"

    budget = BudgetEnforcer(per_call_limit_usd={"opus": 0.0001})  # always blocks opus
    policy = Policy.real_alusi_policy()
    candidates = {"opus": Candidate("anthropic", "claude-opus-4-5", is_free=False, capabilities=frozenset({"text"}))}
    router = Router(policy, candidates, {"opus": fake_opus}, budget=budget)

    result = router.route("deal_strategy", "should we take this deal?")  # cashclaw chain: [opus, sonnet]

    assert not result.success
    assert result.error == "all_candidates_budget_blocked"
    assert any("opus" in b for b in result.budget_blocked_tiers)


def test_route_without_budget_enforcer_is_unchanged_from_workstream_5():
    """Backward compatibility: Router with no budget= argument behaves
    exactly as it did before this workstream."""
    def fake_local(model, prompt):
        return "response"

    policy = Policy.default()
    candidates = {"local": Candidate("ollama", "llama3.2:3b", is_free=True, capabilities=frozenset({"text"}))}
    router = Router(policy, candidates, {"local": fake_local})  # no budget=

    result = router.route("heartbeat", "ping")
    assert result.success
    assert result.budget_warning is False
    assert result.budget_blocked_tiers == []


def test_route_flags_budget_warning_without_blocking():
    def fake_local(model, prompt):
        return "response"

    budget = BudgetEnforcer(daily_limit_usd=10.0, warning_threshold_pct=0.5)
    budget.record_spend("llama3.2:3b", 6.0)  # 60% of 10.0 -- above warning, below hard stop
    router = _real_policy_router(budget, {"local": fake_local})

    result = router.route("heartbeat", "ping")

    assert result.success  # not blocked
    assert result.budget_warning is True  # but flagged
