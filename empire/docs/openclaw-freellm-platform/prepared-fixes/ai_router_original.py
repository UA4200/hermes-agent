"""
ai_router.py — OpenClaw 6-tier LLM routing engine
Tiers: local (Ollama) → haiku → gpt-mini → sonnet → opus → gpt4o
Logs every call to PostgreSQL llm_usage_log for cost tracking.
"""
import os, json, time, datetime, requests
from pathlib import Path

try:
    from load_secrets import inject
    inject()
except Exception:
    pass

BASE = Path.home() / ".openclaw"
POLICY_PATH = BASE / "config/model_policy.json"
LOG_PATH = BASE / "memory/raw/ai_router.jsonl"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── DB connection (lazy) ──────────────────────────────────────────────────────
_db_conn = None

def _get_db():
    global _db_conn
    if _db_conn and not _db_conn.closed:
        try:
            _db_conn.cursor().execute("SELECT 1")
            return _db_conn
        except Exception:
            pass
    try:
        import psycopg2
        pw = os.getenv("CLAWDB_PASSWORD", "")
        _db_conn = psycopg2.connect(
            host=os.getenv("CLAWDB_HOST", "localhost"),
            port=int(os.getenv("CLAWDB_PORT", "5432")),
            user=os.getenv("CLAWDB_USER", "openclaw"),
            password=pw,
            dbname=os.getenv("CLAWDB_DB", "openclaw"),
            connect_timeout=3
        )
        _db_conn.autocommit = True
        return _db_conn
    except Exception:
        return None

def _log_db(row: dict):
    """Write usage row to PostgreSQL. Never raise — fall back to JSONL."""
    try:
        db = _get_db()
        if not db:
            return
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO llm_usage_log
                    (timestamp, agent, task_type, model_tier, provider, model_name,
                     input_tokens, output_tokens, cost_usd, success,
                     escalated_from, latency_ms, chain_key)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                row.get("timestamp", datetime.datetime.now(datetime.UTC).isoformat()),
                row.get("agent"),
                row.get("task_type"),
                row.get("tier"),
                row.get("provider"),
                row.get("model"),
                row.get("input_tokens"),
                row.get("output_tokens"),
                row.get("cost_usd"),
                row.get("success", True),
                row.get("escalated_from"),
                row.get("latency_ms"),
                row.get("chain_key")
            ))
    except Exception:
        pass

def _log(row: dict):
    row.setdefault("timestamp", datetime.datetime.now(datetime.UTC).isoformat())
    try:
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass
    _log_db(row)

# ── Policy ────────────────────────────────────────────────────────────────────

def policy():
    try:
        return json.loads(POLICY_PATH.read_text())
    except Exception:
        return {}

def _chain_for(task_type: str):
    p = policy()
    chain_key = p.get("mapping", {}).get(task_type, "standard")
    chain = p.get("chains", {}).get(chain_key, ["haiku", "gpt", "local"])
    return chain_key, chain

def _cost_per_tokens(tier_name: str, input_tok: int, output_tok: int) -> float:
    p = policy()
    tier = p.get("tiers", {}).get(tier_name, {})
    cpt = tier.get("cost_per_1k_tokens", 0)
    if isinstance(cpt, dict):
        return (input_tok / 1000) * cpt.get("input", 0) + (output_tok / 1000) * cpt.get("output", 0)
    return tier.get("cost_per_call", 0.0)

def _estimate_tokens(text: str) -> int:
    """Rough estimate: 1 token ≈ 4 chars."""
    return max(1, len(text) // 4)

# ── Provider calls ────────────────────────────────────────────────────────────

def call_ollama(prompt: str, max_tokens: int) -> tuple[str, int, int]:
    p = policy()
    url = p.get("ollama_url", "http://127.0.0.1:11434") + "/api/generate"
    model = p.get("models", {}).get("ollama", "llama3.2:3b")
    r = requests.post(url, json={"model": model, "prompt": prompt, "stream": False},
                      timeout=30)  # Short timeout — fall through to haiku if Ollama is down
    r.raise_for_status()
    text = r.json().get("response", "").strip()
    inp = r.json().get("prompt_eval_count") or _estimate_tokens(prompt)
    out = r.json().get("eval_count") or _estimate_tokens(text)
    return text, inp, out

def call_haiku(prompt: str, max_tokens: int, system: str = "") -> tuple[str, int, int]:
    import anthropic
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("missing_ANTHROPIC_API_KEY")
    p = policy()
    model = p.get("models", {}).get("haiku", "claude-haiku-4-5")
    client = anthropic.Anthropic(api_key=key)
    kwargs = dict(model=model, max_tokens=max_tokens,
                  messages=[{"role": "user", "content": prompt}])
    if system:
        kwargs["system"] = system
    r = client.messages.create(**kwargs)
    return r.content[0].text, r.usage.input_tokens, r.usage.output_tokens

def call_sonnet(prompt: str, max_tokens: int, system: str = "") -> tuple[str, int, int]:
    import anthropic
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("missing_ANTHROPIC_API_KEY")
    p = policy()
    model = p.get("models", {}).get("sonnet", "claude-sonnet-4-5")
    client = anthropic.Anthropic(api_key=key)
    kwargs = dict(model=model, max_tokens=max_tokens,
                  messages=[{"role": "user", "content": prompt}])
    if system:
        kwargs["system"] = system
    r = client.messages.create(**kwargs)
    return r.content[0].text, r.usage.input_tokens, r.usage.output_tokens

def call_opus(prompt: str, max_tokens: int, system: str = "") -> tuple[str, int, int]:
    import anthropic
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("missing_ANTHROPIC_API_KEY")
    p = policy()
    model = p.get("models", {}).get("opus", "claude-opus-4-5")
    client = anthropic.Anthropic(api_key=key)
    kwargs = dict(model=model, max_tokens=max_tokens,
                  messages=[{"role": "user", "content": prompt}])
    if system:
        kwargs["system"] = system
    r = client.messages.create(**kwargs)
    return r.content[0].text, r.usage.input_tokens, r.usage.output_tokens

def call_gpt(prompt: str, max_tokens: int) -> tuple[str, int, int]:
    from openai import OpenAI
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("missing_OPENAI_API_KEY")
    p = policy()
    model = p.get("models", {}).get("gpt", "gpt-4o-mini")
    client = OpenAI(api_key=key)
    r = client.responses.create(model=model, input=prompt, max_output_tokens=max_tokens)
    text = getattr(r, "output_text", str(r)).strip()
    usage = getattr(r, "usage", None)
    inp = getattr(usage, "input_tokens", None) or _estimate_tokens(prompt)
    out = getattr(usage, "output_tokens", None) or _estimate_tokens(text)
    return text, inp, out

def call_gpt4o(prompt: str, max_tokens: int) -> tuple[str, int, int]:
    from openai import OpenAI
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("missing_OPENAI_API_KEY")
    client = OpenAI(api_key=key)
    r = client.responses.create(model="gpt-4o", input=prompt, max_output_tokens=max_tokens)
    text = getattr(r, "output_text", str(r)).strip()
    usage = getattr(r, "usage", None)
    inp = getattr(usage, "input_tokens", None) or _estimate_tokens(prompt)
    out = getattr(usage, "output_tokens", None) or _estimate_tokens(text)
    return text, inp, out

_CALLERS = {
    "local":  ("ollama",  call_ollama),
    "ollama": ("ollama",  call_ollama),
    "haiku":  ("haiku",   call_haiku),
    "sonnet": ("sonnet",  call_sonnet),
    "opus":   ("opus",    call_opus),
    "gpt":    ("gpt",     call_gpt),
    "gpt4o":  ("gpt4o",   call_gpt4o),
}

# ── Core routing ──────────────────────────────────────────────────────────────

def generate_text(prompt: str, task_type: str = "coordination",
                  max_tokens: int = 500, agent: str = None,
                  system: str = "") -> dict:
    # Apply token budget (trim prompt before any provider call)
    prompt = _trim_prompt(prompt)
    # PMO auto-classification: if task_type is "auto", classify via PMO
    if task_type == "auto":
        task_type = PMO_TIER_MAP.get(classify_pmo(prompt), "cheap")
    chain_key, chain = _chain_for(task_type)
    errors = {}
    escalated_from = None

    for idx, tier_name in enumerate(chain):
        if tier_name not in _CALLERS:
            continue
        provider_name, caller = _CALLERS[tier_name]
        t0 = time.time()
        try:
            # Pass system prompt to Anthropic callers; Ollama/GPT ignore it gracefully
            import inspect
            if "system" in inspect.signature(caller).parameters:
                text, inp_tok, out_tok = caller(prompt, max_tokens, system=system)
            else:
                text, inp_tok, out_tok = caller(prompt, max_tokens)
            latency_ms = int((time.time() - t0) * 1000)
            cost = _cost_per_tokens(tier_name, inp_tok, out_tok)

            row = {
                "status": "success",
                "agent": agent,
                "task_type": task_type,
                "chain_key": chain_key,
                "tier": tier_name,
                "provider": provider_name,
                "model": policy().get("models", {}).get(
                    tier_name if tier_name != "local" else "ollama", tier_name),
                "input_tokens": inp_tok,
                "output_tokens": out_tok,
                "cost_usd": round(cost, 6),
                "success": True,
                "escalated_from": escalated_from,
                "latency_ms": latency_ms
            }
            _log(row)

            return {
                "text": text,
                "provider": provider_name,
                "tier": tier_name,
                "task_type": task_type,
                "chain_key": chain_key,
                "cost_usd": round(cost, 6),
                "input_tokens": inp_tok,
                "output_tokens": out_tok,
                "latency_ms": latency_ms
            }
        except Exception as e:
            latency_ms = int((time.time() - t0) * 1000)
            errors[tier_name] = str(e)
            escalated_from = tier_name
            _log({
                "status": "error",
                "agent": agent,
                "task_type": task_type,
                "chain_key": chain_key,
                "tier": tier_name,
                "provider": provider_name,
                "cost_usd": 0.0,
                "success": False,
                "latency_ms": latency_ms,
                "error": str(e)
            })

    _log({"status": "failed", "task_type": task_type, "errors": errors, "success": False})
    return {
        "text": "All providers failed. Inspect system health.",
        "provider": "fallback",
        "tier": "fallback",
        "task_type": task_type,
        "errors": errors,
        "cost_usd": 0
    }

# ── PMO Council Classifier ─────────────────────────────────────────────────────────

PMO_CATEGORIES = {
    "monitoring":   ["health", "status", "alive", "ping", "check", "heartbeat"],
    "signal":       ["market", "kalshi", "polymarket", "trade", "score", "p_yes", "edge"],
    "lead_gen":     ["lead", "blco", "buyer", "outreach", "email", "prospect"],
    "research":     ["research", "analyze", "synthesize", "compare", "report"],
    "code":         ["code", "debug", "fix", "build", "deploy", "script"],
    "strategy":     ["strategy", "plan", "decision", "risk", "deal"],
    "coordination": ["summary", "log", "coordinate", "route", "dispatch"],
}

PMO_TIER_MAP = {
    "monitoring":   "local_only",
    "signal":       "ollama_first",
    "lead_gen":     "haiku_first",
    "research":     "high_value",
    "code":         "high_value",
    "strategy":     "paramount",
    "coordination": "cheap",
}


def classify_pmo(prompt: str, task_type: str = None) -> str:
    """Classify prompt into PMO category and return recommended chain."""
    if task_type and task_type in policy().get("mapping", {}):
        return task_type  # explicit override wins
    pl = prompt.lower()
    for category, keywords in PMO_CATEGORIES.items():
        if any(kw in pl for kw in keywords):
            return category
    return "coordination"


# ── Token Budget Enforcer ─────────────────────────────────────────────────────────

def _trim_prompt(prompt: str, max_chars: int = 3000) -> str:
    """Trim prompt to max_chars, preserving start and end context."""
    if len(prompt) <= max_chars:
        return prompt
    half = max_chars // 2
    return prompt[:half] + "\n...[trimmed]...\n" + prompt[-half:]


def estimate_cost(task_type: str, prompt: str, max_tokens: int) -> dict:
    """Estimate cost before making a call."""
    chain_key, chain = _chain_for(task_type)
    tier_name = chain[0] if chain else "haiku"
    p = policy()
    tier = p.get("tiers", {}).get(tier_name, {})
    inp_est = _estimate_tokens(prompt)
    cpt = tier.get("cost_per_1k_tokens", 0)
    if isinstance(cpt, dict):
        est_cost = (inp_est / 1000) * cpt.get("input", 0) + (max_tokens / 1000) * cpt.get("output", 0)
    else:
        est_cost = tier.get("cost_per_call", 0.0)
    return {
        "tier": tier_name,
        "chain": chain,
        "input_tokens_est": inp_est,
        "output_tokens_max": max_tokens,
        "cost_usd_est": round(est_cost, 6),
        "is_free": tier_name in ("local", "ollama")
    }


# ── Task Decomposer ───────────────────────────────────────────────────────────────────

def decompose_and_route(task_description: str, agent: str = None) -> list:
    """
    Break a complex task into subtasks, route each to optimal tier.
    Returns list of results, one per subtask.
    """
    import re as _re
    # Use local Ollama to decompose (free)
    decomp_prompt = (
        "Break this task into 2-4 atomic subtasks. Return JSON only.\n"
        f"Task: {task_description}\n"
        'Format: [{"subtask": "...", "type": "monitoring|signal|lead_gen|research|code|strategy|coordination"}]'
    )

    try:
        decomp_result = generate_text(decomp_prompt, task_type="task_decomposition", max_tokens=300, agent=agent)
        m = _re.search(r'\[.*\]', decomp_result.get("text", ""), _re.DOTALL)
        if m:
            subtasks = json.loads(m.group())
            results = []
            for st in subtasks[:4]:  # cap at 4 subtasks
                pmo_cat = classify_pmo(st.get("subtask", ""), st.get("type"))
                chain_key = PMO_TIER_MAP.get(pmo_cat, "cheap")
                result = generate_text(
                    st["subtask"],
                    task_type=chain_key,
                    max_tokens=400,
                    agent=agent
                )
                result["subtask"] = st["subtask"]
                result["pmo_category"] = pmo_cat
                results.append(result)
            return results
    except Exception:
        pass

    # Fallback: treat as single task
    pmo_cat = classify_pmo(task_description)
    result = generate_text(task_description, task_type=PMO_TIER_MAP.get(pmo_cat, "coordination"), max_tokens=500, agent=agent)
    result["pmo_category"] = pmo_cat
    return [result]


# ── Convenience wrappers (backwards-compatible) ───────────────────────────────

def generate(prompt: str, task_type: str = "coordination",
             max_tokens: int = 500, agent: str = None) -> str:
    return generate_text(prompt, task_type, max_tokens, agent).get("text", "")

def humanize_text(text: str, purpose: str = "business") -> dict:
    return generate_text(
        f"Rewrite naturally for {purpose}. Preserve meaning. Avoid hype.\n\n{text}",
        "humanize", 700)

def ats_optimize_text(text: str, target: str) -> dict:
    return generate_text(
        f"Make this ATS-friendly without inventing experience.\nTarget: {target}\n\n{text}",
        "ats_optimize", 900)

def deal_strategy(context: dict) -> dict:
    return generate_text(
        "Act as a deal strategist. Recommend next action, risk controls, and operator decision.\n\n"
        + json.dumps(context, indent=2),
        "deal_strategy", 900)

# ── Cost reporting ────────────────────────────────────────────────────────────

def cost_report(days: int = 7) -> dict:
    """Pull cost summary from PostgreSQL."""
    try:
        db = _get_db()
        if not db:
            return {"error": "no_db"}
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    provider,
                    task_type,
                    COUNT(*) AS calls,
                    SUM(input_tokens) AS input_tokens,
                    SUM(output_tokens) AS output_tokens,
                    ROUND(SUM(cost_usd)::numeric, 4) AS total_cost,
                    ROUND(AVG(latency_ms)::numeric, 0) AS avg_latency_ms,
                    SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) AS failures
                FROM llm_usage_log
                WHERE timestamp > NOW() - INTERVAL '%s days'
                GROUP BY provider, task_type
                ORDER BY total_cost DESC
            """, (days,))
            rows = cur.fetchall()
            cols = ["provider", "task_type", "calls", "input_tokens",
                    "output_tokens", "total_cost", "avg_latency_ms", "failures"]
            return {"rows": [dict(zip(cols, r)) for r in rows], "days": days}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        r = cost_report(30)
        print(json.dumps(r, indent=2, default=str))
    else:
        # Quick test
        result = generate_text("Say OK in one word.", task_type="heartbeat", max_tokens=10)
        print(json.dumps(result, indent=2))
