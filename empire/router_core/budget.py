"""Token budget enforcement.

Ported verbatim from ai_router.py's _trim_prompt (fetched live from
ugos-mac-mini, Phase 2 Workstream 2) -- adaptive_router.py has no
equivalent (it sends whatever prompt a caller supplies, untrimmed), so
this is a real capability being carried into the consolidated design.
"""
from __future__ import annotations


def trim_prompt(prompt: str, max_chars: int = 3000) -> str:
    """Trim prompt to max_chars, preserving start and end context. Same
    algorithm, same default, as the live system's _trim_prompt -- a
    verbatim port, not a reinterpretation."""
    if len(prompt) <= max_chars:
        return prompt
    half = max_chars // 2
    return prompt[:half] + "\n...[trimmed]...\n" + prompt[-half:]
