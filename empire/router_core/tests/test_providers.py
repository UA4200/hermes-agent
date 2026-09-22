"""Tests for providers.py -- mocked HTTP only, no real network calls, no
credentials required. Proves response-parsing and error-handling logic is
correct without needing to actually reach Free-Way/Ollama/Anthropic/
OpenAI (which would need real API keys this test suite deliberately
never touches).
"""
from __future__ import annotations

import json
import sys
import urllib.error
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from router_core.providers import (
    ProviderCallError,
    call_anthropic_direct_raw,
    call_freeway_raw,
    call_ollama_raw,
    call_openai_direct_raw,
    make_ollama_caller,
)


def _mock_response(payload: dict):
    """Builds a context-manager mock matching urllib.request.urlopen's
    real return shape (an object with .read())."""
    mock = MagicMock()
    mock.read.return_value = json.dumps(payload).encode()
    mock.__enter__.return_value = mock
    mock.__exit__.return_value = False
    return mock


def test_call_ollama_raw_parses_real_response_shape():
    payload = {"response": "hello there", "prompt_eval_count": 5, "eval_count": 3}
    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        result = call_ollama_raw("llama3.2:3b", "hi")
    assert result["text"] == "hello there"
    assert result["input_tokens"] == 5
    assert result["output_tokens"] == 3


def test_call_ollama_raw_raises_on_empty_response():
    payload = {"response": "   "}
    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        try:
            call_ollama_raw("llama3.2:3b", "hi")
            assert False, "expected ProviderCallError"
        except ProviderCallError:
            pass


def test_call_anthropic_direct_raw_parses_real_response_shape():
    payload = {
        "content": [{"type": "text", "text": "hi from claude"}],
        "usage": {"input_tokens": 10, "output_tokens": 4},
    }
    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        result = call_anthropic_direct_raw("claude-haiku-4-5", "hi", api_key="fake-key-not-real")
    assert result["text"] == "hi from claude"
    assert result["input_tokens"] == 10


def test_call_freeway_raw_raises_on_error_field():
    payload = {"error": {"type": "invalid_request_error", "message": "bad request"}}
    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        try:
            call_freeway_raw("command-r", "hi", api_key="fake-key-not-real")
            assert False, "expected ProviderCallError"
        except ProviderCallError as e:
            assert "invalid_request_error" in str(e)


def test_call_openai_direct_raw_parses_real_response_shape():
    payload = {
        "choices": [{"message": {"content": "hi from gpt"}}],
        "usage": {"prompt_tokens": 8, "completion_tokens": 3},
    }
    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        result = call_openai_direct_raw("gpt-4o-mini", "hi", api_key="fake-key-not-real")
    assert result["text"] == "hi from gpt"


def test_http_error_becomes_provider_call_error():
    error = urllib.error.HTTPError(
        url="http://127.0.0.1:11434/api/generate", code=500, msg="fail",
        hdrs=None, fp=MagicMock(read=lambda: b"server error"),
    )
    with patch("urllib.request.urlopen", side_effect=error):
        try:
            call_ollama_raw("llama3.2:3b", "hi")
            assert False, "expected ProviderCallError"
        except ProviderCallError as e:
            assert "500" in str(e)


def test_make_ollama_caller_returns_provider_caller_shape():
    """The ProviderCaller-shaped wrapper takes (model, prompt) and
    returns just the text -- proves the factory function actually wires
    up correctly, not just that the _raw function does."""
    payload = {"response": "wrapped response"}
    caller = make_ollama_caller()
    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        text = caller("llama3.2:3b", "hi")
    assert text == "wrapped response"
