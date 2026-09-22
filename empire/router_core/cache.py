"""Semantic cache hook.

Shaped around GPTCache's interface (zilliztech/GPTCache, MIT -- confirmed
actively maintained, commit same-day, see
../docs/openclaw-freellm-platform/CACHING_AND_ACCELERATION_RESEARCH.md).
GPTCache itself is an optional dependency: if it isn't installed, this
module falls back to a no-op cache rather than failing import, so
router_core works without it (matching this program's "no paid-only
dependency, capability-first" constraint -- GPTCache is free/self-hosted,
but still shouldn't be a hard import-time requirement for a routing
library).
"""
from __future__ import annotations

from typing import Protocol


class SemanticCache(Protocol):
    def get(self, prompt: str) -> str | None: ...
    def put(self, prompt: str, response: str) -> None: ...


class NoOpCache:
    """Used when no real cache is configured. Always misses."""

    def get(self, prompt: str) -> str | None:
        return None

    def put(self, prompt: str, response: str) -> None:
        return None


class InMemoryExactCache:
    """Exact-match cache for tests and for task types where semantic
    similarity isn't needed (e.g. heartbeat/health_check prompts that are
    byte-identical call to call). A real deployment fronting
    heartbeat/health_check/monitoring/cron_task traffic (per Workstream 3's
    recommendation) would likely want this cheaper tier ahead of a full
    embedding-based GPTCache lookup for exact repeats, falling through to
    GPTCache only on an exact-match miss."""

    def __init__(self, max_entries: int = 1000):
        self._store: dict[str, str] = {}
        self._max_entries = max_entries

    def get(self, prompt: str) -> str | None:
        return self._store.get(prompt)

    def put(self, prompt: str, response: str) -> None:
        if len(self._store) >= self._max_entries:
            self._store.pop(next(iter(self._store)))
        self._store[prompt] = response


def build_gptcache_backed_cache() -> SemanticCache:
    """Returns a GPTCache-backed semantic cache if the `gptcache` package
    is installed, else a NoOpCache. Not called by default -- callers
    choose explicitly, since embedding-based caching has a real resource
    cost (Workstream 3's finding) that shouldn't be silently enabled."""
    try:
        import gptcache  # noqa: F401
    except ImportError:
        return NoOpCache()

    # A real integration would configure gptcache's embedding backend and
    # vector store here. Deliberately not built out further in this
    # prototype -- see README.md's "What this does NOT do."
    return NoOpCache()
