"""Context compression hook.

Shaped around LLMLingua's interface (microsoft/LLMLingua, MIT -- confirmed
actively maintained via GitHub API commit date, not its README, see
../docs/openclaw-freellm-platform/CACHING_AND_ACCELERATION_RESEARCH.md).
Same optional-dependency pattern as cache.py: falls back to a no-op
(returns the prompt unchanged) rather than requiring the dependency at
import time.
"""
from __future__ import annotations

from typing import Protocol


class Compressor(Protocol):
    def compress(self, text: str, target_ratio: float = 0.5) -> str: ...


class NoOpCompressor:
    def compress(self, text: str, target_ratio: float = 0.5) -> str:
        return text


class TruncatingCompressor:
    """A crude, dependency-free fallback: truncates to the target ratio
    by character count. Not a substitute for real semantic compression --
    exists so router_core's compression *hook point* is exercised by tests
    without requiring LLMLingua, and so a caller who wants "something,
    cheaply" has a non-no-op option before adopting the real dependency."""

    def compress(self, text: str, target_ratio: float = 0.5) -> str:
        if not (0.0 < target_ratio < 1.0):
            return text
        target_len = max(1, int(len(text) * target_ratio))
        return text[:target_len]


def build_llmlingua_backed_compressor() -> Compressor:
    """Returns an LLMLingua-backed compressor if the `llmlingua` package
    is installed, else NoOpCompressor. Like cache.py's equivalent, the
    real LLMLingua integration is deliberately not built out in this
    prototype -- see README.md."""
    try:
        import llmlingua  # noqa: F401
    except ImportError:
        return NoOpCompressor()
    return NoOpCompressor()
