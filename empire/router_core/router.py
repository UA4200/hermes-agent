"""Unified routing entry point.

Combines policy.py's task-type -> chain resolution (ai_router.py's shape),
engine.py's health-aware scoring (adaptive_router.py's shape), and the
optional cache/compress hooks, behind one route() call. This is the
prototype's proof that both live systems' concepts compose cleanly into
one library -- see README.md for what is and isn't proven by that.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from .budget_enforcement import BudgetEnforcer
from .cache import NoOpCache, SemanticCache
from .compress import NoOpCompressor, Compressor
from .engine import Candidate, RouterState, rank_candidates
from .policy import Policy


ProviderCaller = Callable[[str, str], str]  # (model, prompt) -> response text


def _estimate_tokens(text: str) -> int:
    """Same rough estimate ai_router.py itself uses: 1 token ~= 4 chars."""
    return max(1, len(text) // 4)


@dataclass
class RouteResult:
    text: str
    provider: str
    model: str
    tier: str
    chain_key: str
    cache_hit: bool
    compressed: bool
    latency_ms: float
    attempts: list[str] = field(default_factory=list)
    success: bool = True
    error: str | None = None
    budget_warning: bool = False
    budget_blocked_tiers: list[str] = field(default_factory=list)


class Router:
    def __init__(
        self,
        policy: Policy,
        candidates_by_tier: dict[str, Candidate],
        callers: dict[str, ProviderCaller],
        state: RouterState | None = None,
        cache: SemanticCache | None = None,
        compressor: Compressor | None = None,
        compress_task_types: frozenset[str] = frozenset({"high_value", "paramount"}),
        compress_threshold_chars: int = 4000,
        budget: BudgetEnforcer | None = None,
        default_max_output_tokens: int = 500,
    ):
        """
        candidates_by_tier: maps a policy tier name (e.g. "local", "haiku")
            to the Candidate describing that tier's provider/model/capabilities.
            This is where a real deployment would plug in adaptive_router.py's
            actual ALL_CANDIDATES/PROVIDER_CAPS data.
        callers: maps a tier name to a function that actually makes the call.
            Kept as plain callables (not adaptive_router.py's endpoint-string
            dispatch) so tests can inject fakes with zero network/credentials.
        """
        self.policy = policy
        self.candidates_by_tier = candidates_by_tier
        self.callers = callers
        self.state = state or RouterState()
        self.cache = cache or NoOpCache()
        self.compressor = compressor or NoOpCompressor()
        self.compress_task_types = compress_task_types
        self.compress_threshold_chars = compress_threshold_chars
        self.budget = budget  # None = no enforcement, unchanged Workstream 5 behavior
        self.default_max_output_tokens = default_max_output_tokens

    def route(
        self,
        task_type: str,
        prompt: str,
        required_capabilities: frozenset[str] = frozenset({"text"}),
    ) -> RouteResult:
        t_start = time.time()

        cached = self.cache.get(prompt)
        if cached is not None:
            return RouteResult(
                text=cached, provider="cache", model="cache", tier="cache",
                chain_key="cache", cache_hit=True, compressed=False,
                latency_ms=(time.time() - t_start) * 1000,
            )

        chain_key, tier_names = self.policy.chain_for(task_type)

        compressed = False
        effective_prompt = prompt
        if (
            chain_key in self.compress_task_types
            and len(prompt) > self.compress_threshold_chars
        ):
            effective_prompt = self.compressor.compress(prompt)
            compressed = effective_prompt != prompt

        candidates = [
            self.candidates_by_tier[t] for t in tier_names if t in self.candidates_by_tier
        ]
        ranked = rank_candidates(candidates, required_capabilities, self.state)

        attempts: list[str] = []
        budget_blocked_tiers: list[str] = []
        budget_warning = self.budget.status().state == "warning" if self.budget else False

        for candidate in ranked:
            key = f"{candidate.provider}/{candidate.model}"
            tier_name = next(
                t for t, c in self.candidates_by_tier.items() if c is candidate
            )
            caller = self.callers.get(tier_name)
            if caller is None:
                continue

            # Real cost-limit enforcement (Phase 2 Workstream 6) -- the gap
            # Phase 1 found: a candidate whose estimated cost would breach
            # a budget, or that violates a local-first-only task type, is
            # treated as ineligible and skipped, exactly like a circuit-
            # broken provider. This IS "automatic downgrade" / "automatic
            # local-first execution" in practice -- the loop naturally
            # falls through to the next, cheaper/local candidate.
            if self.budget is not None:
                blocked, reason = self.budget.enforce_local_first(task_type, tier_name)
                if not blocked:
                    est_input = _estimate_tokens(effective_prompt)
                    est_cost = self.policy.cost_per_call(
                        tier_name, est_input, self.default_max_output_tokens
                    )
                    blocked, reason = self.budget.would_exceed(tier_name, candidate.model, est_cost)
                if blocked:
                    budget_blocked_tiers.append(f"{key}:{reason}")
                    continue

            attempts.append(key)
            call_start = time.time()
            try:
                text = caller(candidate.model, effective_prompt)
                latency_ms = (time.time() - call_start) * 1000
                self.state.record_success(key, latency_ms)
                self.cache.put(prompt, text)
                if self.budget is not None:
                    est_input = _estimate_tokens(effective_prompt)
                    est_output = _estimate_tokens(text)
                    actual_cost_est = self.policy.cost_per_call(tier_name, est_input, est_output)
                    self.budget.record_spend(candidate.model, actual_cost_est)
                return RouteResult(
                    text=text,
                    provider=candidate.provider,
                    model=candidate.model,
                    tier=tier_name,
                    chain_key=chain_key,
                    cache_hit=False,
                    compressed=compressed,
                    latency_ms=(time.time() - t_start) * 1000,
                    attempts=attempts,
                    success=True,
                    budget_warning=budget_warning,
                    budget_blocked_tiers=budget_blocked_tiers,
                )
            except Exception as e:  # noqa: BLE001 - mirrors adaptive_router.py's
                # broad catch-and-try-next-candidate behavior; a bad provider
                # must not take down the whole request.
                self.state.record_failure(key)
                attempts.append(f"{key}:FAILED:{e}")

        error = "all_candidates_failed"
        if budget_blocked_tiers and not attempts:
            # Every eligible candidate was budget-blocked, none was even
            # attempted -- a distinct, real failure mode from "tried and
            # failed", worth surfacing as such rather than collapsing into
            # the generic error.
            error = "all_candidates_budget_blocked"
        return RouteResult(
            text="",
            provider="",
            model="",
            tier="",
            chain_key=chain_key,
            cache_hit=False,
            compressed=compressed,
            latency_ms=(time.time() - t_start) * 1000,
            attempts=attempts,
            success=False,
            error=error,
            budget_warning=budget_warning,
            budget_blocked_tiers=budget_blocked_tiers,
        )
