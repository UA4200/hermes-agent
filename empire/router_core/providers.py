"""Real provider callers, adapted from adaptive_router.py's call_freeway/
call_ollama/call_anthropic_direct/call_openai_direct (fetched live from
ugos-mac-mini, Phase 2 Workstream 2).

Adapted, not copy-pasted verbatim: the live functions return a dict with
text/tokens/latency/stop_reason (needed for adaptive_router.py's own
telemetry); router_core's ProviderCaller signature is the simpler
`(model, prompt) -> str` (Workstream 5's design choice, kept here for
consistency) -- these wrappers call the same real HTTP endpoints with the
same real request shapes, then return just the text. A caller needing
token counts/latency for cost tracking should call the underlying
`*_raw` function directly instead of the ProviderCaller-shaped wrapper.

Zero required dependencies, matching router_core's existing design
principle: uses urllib (stdlib), not the anthropic/openai SDKs --
this mirrors adaptive_router.py's own real implementation choice (it
also uses urllib for Free-Way/Ollama/Anthropic/OpenAI, not the SDKs;
ai_router.py's SDK-based haiku/sonnet/opus/gpt/gpt4o callers are the
ones NOT carried forward here, as a real, justified consolidation
decision -- one urllib-based function handles any model name per
provider, instead of five near-identical SDK-based functions).
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request


class ProviderCallError(RuntimeError):
    """Raised on any provider call failure -- callers (router_core.Router)
    catch this the same way adaptive_router.py's route() catches any
    Exception from a candidate call and tries the next one."""


def call_freeway_raw(
    model: str, prompt: str, *, api_key: str, system: str = "",
    max_tokens: int = 500, base_url: str = "http://127.0.0.1:8082",
    timeout: float = 30.0,
) -> dict:
    """Calls Free-Way's /v1/messages bridge -- real endpoint, real request
    shape, ported from adaptive_router.py's call_freeway. base_url
    defaults to the REAL confirmed port (8082, verified live in Phase 1 --
    not 8787, Free-Way's own README default, which does not match this
    deployment's actual runtime config)."""
    body = {"model": model, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    req = urllib.request.Request(
        f"{base_url}/v1/messages", data=json.dumps(body).encode(), method="POST",
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                 "Content-Type": "application/json"},
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise ProviderCallError(f"freeway HTTP {e.code}: {e.read()[:200]}") from e
    except urllib.error.URLError as e:
        raise ProviderCallError(f"freeway unreachable: {e}") from e
    latency_ms = int((time.time() - t0) * 1000)
    if "error" in data:
        raise ProviderCallError(str(data["error"])[:200])
    content = data.get("content", [])
    text = next((c.get("text", "") for c in content if c.get("type") == "text"), "")
    if not text and not any(c.get("type") == "tool_use" for c in content):
        raise ProviderCallError("freeway returned empty content")
    usage = data.get("usage", {})
    return {"text": text, "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0), "latency_ms": latency_ms}


def call_ollama_raw(
    model: str, prompt: str, *, max_tokens: int = 500,
    base_url: str = "http://127.0.0.1:11434", timeout: float = 90.0,
) -> dict:
    """Calls Ollama's native /api/generate -- ported from
    adaptive_router.py's call_ollama (which builds a flattened
    role-prefixed prompt itself; this version accepts a pre-built prompt
    string, leaving message-formatting to the caller, matching
    router_core's simpler (model, prompt) shape).

    Default timeout raised from 30.0 to 90.0 (Phase 2 Workstream 9
    follow-up, 2026-09-25): real measured cold-start model loads on the
    reference deployment host take 25-35+ seconds (pm2's own captured
    Ollama logs show HTTP 499s -- client gave up, not a server error --
    at consistent 30.2-32.1s, caused by mmap=false forcing a full
    sequential disk read of the model weights on every cold load). 30s
    was too tight a margin against that real worst case; 90s clears it
    with real headroom rather than just barely covering the median."""
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                        "options": {"num_predict": max_tokens}}).encode()
    req = urllib.request.Request(f"{base_url}/api/generate", data=body, method="POST",
                                   headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise ProviderCallError(f"ollama HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise ProviderCallError(f"ollama unreachable: {e}") from e
    latency_ms = int((time.time() - t0) * 1000)
    text = data.get("response", "")
    if not text.strip():
        raise ProviderCallError("ollama returned empty response")
    return {"text": text, "input_tokens": data.get("prompt_eval_count", 0),
            "output_tokens": data.get("eval_count", 0), "latency_ms": latency_ms}


def call_anthropic_direct_raw(
    model: str, prompt: str, *, api_key: str, system: str = "",
    max_tokens: int = 500, timeout: float = 60.0,
) -> dict:
    """Calls Anthropic's API directly -- ported from adaptive_router.py's
    call_anthropic_direct. Handles any Anthropic model by name (haiku,
    sonnet, opus), consolidating ai_router.py's three separate
    call_haiku/call_sonnet/call_opus functions into one."""
    body = {"model": model, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(), method="POST",
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                 "Content-Type": "application/json"},
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise ProviderCallError(f"anthropic HTTP {e.code}: {e.read()[:200]}") from e
    except urllib.error.URLError as e:
        raise ProviderCallError(f"anthropic unreachable: {e}") from e
    latency_ms = int((time.time() - t0) * 1000)
    content = data.get("content", [])
    text = next((c.get("text", "") for c in content if c.get("type") == "text"), "")
    usage = data.get("usage", {})
    return {"text": text, "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0), "latency_ms": latency_ms}


def call_openai_direct_raw(
    model: str, prompt: str, *, api_key: str, max_tokens: int = 500, timeout: float = 60.0,
) -> dict:
    """Calls OpenAI's API directly -- ported from adaptive_router.py's
    call_openai_direct, tool-call handling omitted (router_core's simpler
    (model, prompt) -> str shape has no tools parameter to convert)."""
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=body, method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise ProviderCallError(f"openai HTTP {e.code}: {e.read()[:200]}") from e
    except urllib.error.URLError as e:
        raise ProviderCallError(f"openai unreachable: {e}") from e
    latency_ms = int((time.time() - t0) * 1000)
    if "error" in data:
        raise ProviderCallError(str(data["error"])[:200])
    choice = data.get("choices", [{}])[0]
    text = choice.get("message", {}).get("content", "") or ""
    if not text:
        raise ProviderCallError("openai returned empty content")
    usage = data.get("usage", {})
    return {"text": text, "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0), "latency_ms": latency_ms}


# ── ProviderCaller-shaped wrappers (model, prompt) -> str ────────────────
# These are what get plugged into router_core.Router's `callers` dict.

def make_freeway_caller(api_key: str, base_url: str = "http://127.0.0.1:8082"):
    return lambda model, prompt: call_freeway_raw(model, prompt, api_key=api_key, base_url=base_url)["text"]


def make_ollama_caller(base_url: str = "http://127.0.0.1:11434"):
    return lambda model, prompt: call_ollama_raw(model, prompt, base_url=base_url)["text"]


def make_anthropic_caller(api_key: str):
    return lambda model, prompt: call_anthropic_direct_raw(model, prompt, api_key=api_key)["text"]


def make_openai_caller(api_key: str):
    return lambda model, prompt: call_openai_direct_raw(model, prompt, api_key=api_key)["text"]
