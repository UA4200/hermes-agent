"""Health-tracking provider scoring engine.

Pattern borrowed from adaptive_router.py's RouterState/score_candidate/
rank_candidates on ugos-mac-mini (read live, not guessed) -- reimplemented
independently, not copy-pasted, so this can be reviewed and tested on its
own before anyone considers pointing real traffic at it. Does NOT carry
over adaptive_router.py's tuned scoring weights, provider catalog, or
circuit-breaker timing -- those encode real production tuning decisions
that shouldn't be guessed at from outside. See README.md.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ProviderHealth:
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0
    avg_latency_ms: float = 1000.0
    circuit_state: str = "HEALTHY"  # HEALTHY -> DEGRADED -> QUARANTINED -> RETEST
    quarantine_until: float | None = None

    @property
    def total_calls(self) -> int:
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.75  # prior: assume decent, matches adaptive_router.py's convention
        return self.success_count / self.total_calls


class RouterState:
    """In-memory provider health tracker. A persistent (file-backed)
    subclass is a straightforward extension (see adaptive_router.py's
    JSON-file version) -- kept in-memory here to keep the test suite
    hermetic and fast; not a functional regression for the prototype's
    purpose."""

    def __init__(self, quarantine_seconds: float = 300.0,
                 degrade_after: int = 2, quarantine_after: int = 4):
        self._providers: dict[str, ProviderHealth] = {}
        self.quarantine_seconds = quarantine_seconds
        self.degrade_after = degrade_after
        self.quarantine_after = quarantine_after

    def get(self, key: str) -> ProviderHealth:
        return self._providers.setdefault(key, ProviderHealth())

    def record_success(self, key: str, latency_ms: float) -> None:
        p = self.get(key)
        p.success_count += 1
        p.consecutive_failures = 0
        p.avg_latency_ms = 0.7 * p.avg_latency_ms + 0.3 * latency_ms
        p.circuit_state = "HEALTHY"

    def record_failure(self, key: str) -> None:
        p = self.get(key)
        p.failure_count += 1
        p.consecutive_failures += 1
        if p.circuit_state == "HEALTHY" and p.consecutive_failures >= self.degrade_after:
            p.circuit_state = "DEGRADED"
        elif p.circuit_state == "DEGRADED" and p.consecutive_failures >= self.quarantine_after:
            p.circuit_state = "QUARANTINED"
            p.quarantine_until = time.time() + self.quarantine_seconds

    def is_healthy(self, key: str) -> bool:
        p = self.get(key)
        if p.circuit_state != "QUARANTINED":
            return True
        if p.quarantine_until is not None and time.time() >= p.quarantine_until:
            p.circuit_state = "RETEST"
            p.consecutive_failures = 0
            return True  # allow one retest attempt, matches adaptive_router.py
        return False


@dataclass
class Candidate:
    provider: str
    model: str
    is_free: bool
    capabilities: frozenset[str] = field(default_factory=frozenset)


DEFAULT_WEIGHTS = {
    "task_fit": 0.30,
    "quality": 0.20,
    "cost": 0.20,
    "reliability": 0.15,
    "latency": 0.10,
    "quota": 0.05,
}


def score_candidate(
    candidate: Candidate,
    required_capabilities: frozenset[str],
    state: RouterState,
    weights: dict[str, float] | None = None,
) -> float:
    """Score a candidate for a task. Returns -1.0 if ineligible
    (missing capability or circuit-broken), matching adaptive_router.py's
    sentinel convention rather than raising -- callers filter on >= 0."""
    weights = weights or DEFAULT_WEIGHTS
    if not required_capabilities.issubset(candidate.capabilities):
        return -1.0

    key = f"{candidate.provider}/{candidate.model}"
    if not state.is_healthy(key):
        return -1.0

    p = state.get(key)
    cost_score = 1.0 if candidate.is_free else 0.2
    quality_score = 0.7  # no history tracked in this prototype; a real
    # deployment would persist quality feedback the way adaptive_router.py
    # does via record_success(..., quality=...)
    reliability_score = p.success_rate
    latency_score = max(0.0, 1.0 - p.avg_latency_ms / 5000)
    quota_score = 0.5 if p.circuit_state == "DEGRADED" else 1.0

    total = (
        weights["task_fit"] * 1.0
        + weights["quality"] * quality_score
        + weights["cost"] * cost_score
        + weights["reliability"] * reliability_score
        + weights["latency"] * latency_score
        + weights["quota"] * quota_score
    )
    return round(total, 4)


def rank_candidates(
    candidates: list[Candidate],
    required_capabilities: frozenset[str],
    state: RouterState,
    weights: dict[str, float] | None = None,
) -> list[Candidate]:
    scored = [
        (score_candidate(c, required_capabilities, state, weights), c)
        for c in candidates
    ]
    eligible = [(s, c) for s, c in scored if s >= 0]
    eligible.sort(key=lambda pair: -pair[0])
    return [c for _, c in eligible]
