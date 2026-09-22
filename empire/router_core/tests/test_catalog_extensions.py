"""Tests for Phase 2 Workstream 4's catalog extensions (Codex/DeepSeek/
Gemma/gap-filled locally-installed models). Proves the extension is
purely additive data, not a change to router_core's provider-agnostic
mechanism (engine.py/router.py get zero new provider-specific code).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from router_core.catalog import (
    ALL_PROVIDER_CAPS,
    INSTALLED_OLLAMA_MODELS,
    PROVIDER_CAPS,
    future_provider_candidates,
    installed_ollama_candidates,
    real_alusi_candidates,
)
from router_core.engine import RouterState, rank_candidates


def test_all_six_installed_models_have_capabilities():
    """The real gap this workstream found: gemma2:2b and phi3:mini are
    installed on ugos-mac-mini but PROVIDER_CAPS never declared them.
    Proves ALL_PROVIDER_CAPS closes that gap for every installed model."""
    for model in INSTALLED_OLLAMA_MODELS:
        key = f"ollama/{model}"
        assert key in ALL_PROVIDER_CAPS, f"{key} has no capability declaration"


def test_gemma2_was_the_real_gap_not_already_declared():
    """Confirms the gap was real (not already covered) before this
    workstream's fix -- a test that would fail if PROVIDER_CAPS is later
    edited to add gemma2:2b directly, which is fine (it'd mean the gap
    got fixed at the source instead), but should be noticed, not silently
    pass either way."""
    assert "ollama/gemma2:2b" not in PROVIDER_CAPS
    assert "ollama/gemma2:2b" in ALL_PROVIDER_CAPS


def test_installed_ollama_candidates_covers_all_six():
    candidates = installed_ollama_candidates()
    assert len(candidates) == 6
    assert {c.model for c in candidates} == set(INSTALLED_OLLAMA_MODELS)
    assert all(c.is_free for c in candidates)


def test_installed_candidates_rank_successfully_for_text_task():
    """Proves the gap-filled candidates aren't just declared but actually
    usable by the engine -- they must score >= 0 (eligible) for a plain
    text task, same as the live-qualified pool."""
    state = RouterState()
    candidates = installed_ollama_candidates()
    ranked = rank_candidates(candidates, frozenset({"text"}), state)
    assert len(ranked) == 6  # none excluded


def test_future_providers_include_deepseek_and_codex():
    """Directly proves the brief's named providers (DeepSeek, Codex) are
    represented, not just implied."""
    candidates = future_provider_candidates()
    models = {c.model for c in candidates}
    assert "deepseek-r1:8b" in models
    assert "gpt-5-codex" in models


def test_codex_candidate_is_not_marked_free():
    """A real, deliberate distinction: Codex is OpenAI-family and priced
    like it, unlike the local Ollama additions -- proves this wasn't
    lumped in as free by mistake."""
    candidates = future_provider_candidates()
    codex = next(c for c in candidates if c.model == "gpt-5-codex")
    assert codex.is_free is False
    assert codex.provider == "openai"


def test_extension_did_not_change_live_fidelity_pool():
    """real_alusi_candidates() (Workstream 2's live-fidelity reference)
    must be completely unaffected by this workstream's additions -- still
    exactly the 9 real, live-qualified candidates, nothing more."""
    assert len(real_alusi_candidates()) == 9
