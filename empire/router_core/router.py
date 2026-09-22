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

from .cache import NoOpCache, SemanticCache
from .compress import NoOpCompressor, Compressor
from .engine import Candidate, RouterState, rank_candidates
from .policy import Policy


ProviderCaller = Callable[[str, str], str]  # (model, prompt) -> response text


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
        for candidate in ranked:
            key = f"{candidate.provider}/{candidate.model}"
            tier_name = next(
                t for t, c in self.candidates_by_tier.items() if c is candidate
            )
            caller = self.callers.get(tier_name)
            if caller is None:
                continue
            attempts.append(key)
            call_start = time.time()
            try:
                text = caller(candidate.model, effective_prompt)
                latency_ms = (time.time() - call_start) * 1000
                self.state.record_success(key, latency_ms)
                self.cache.put(prompt, text)
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
                )
            except Exception as e:  # noqa: BLE001 - mirrors adaptive_router.py's
                # broad catch-and-try-next-candidate behavior; a bad provider
                # must not take down the whole request.
                self.state.record_failure(key)
                attempts.append(f"{key}:FAILED:{e}")

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
            error="all_candidates_failed",
        )
