"""Task-type -> escalation chain policy.

Shape borrowed from ai_router.py's model_policy.json on ugos-mac-mini
(read live, not guessed): a "chains" table of named tier sequences, and a
"mapping" table from task_type to chain name. This module does not ship
the live policy data -- callers supply their own policy dict or JSON file.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_POLICY = {
    "chains": {
        "local_only": ["local"],
        "cheap": ["local", "haiku"],
        "standard": ["haiku", "local"],
        "high_value": ["sonnet", "haiku"],
        "paramount": ["opus", "sonnet"],
    },
    "mapping": {
        "heartbeat": "local_only",
        "health_check": "local_only",
        "coordination": "cheap",
        "research": "high_value",
        "critical_reasoning": "paramount",
    },
    "cost_limits": {
        "daily_hard_limit_usd": 10.0,
    },
}


@dataclass
class Policy:
    chains: dict[str, list[str]] = field(default_factory=dict)
    mapping: dict[str, str] = field(default_factory=dict)
    cost_limits: dict[str, float] = field(default_factory=dict)
    # Fields below complete the real model_policy.json schema (Phase 2
    # Workstream 2, ported for equivalence testing against a real fixture
    # -- see fixtures/alusi_model_policy.json). Optional so the minimal
    # DEFAULT_POLICY above still round-trips unchanged.
    tiers: dict[str, dict] = field(default_factory=dict)
    models: dict[str, str] = field(default_factory=dict)
    ollama_url: str = "http://127.0.0.1:11434"
    external_send_requires_approval: bool = False
    no_hidden_bypass_routes: bool = False
    policy_version: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Policy":
        return cls(
            chains=dict(data.get("chains", {})),
            mapping=dict(data.get("mapping", {})),
            cost_limits=dict(data.get("cost_limits", {})),
            tiers=dict(data.get("tiers", {})),
            models=dict(data.get("models", {})),
            ollama_url=data.get("ollama_url", "http://127.0.0.1:11434"),
            external_send_requires_approval=bool(data.get("external_send_requires_approval", False)),
            no_hidden_bypass_routes=bool(data.get("no_hidden_bypass_routes", False)),
            policy_version=data.get("policy_version", ""),
        )

    @classmethod
    def from_file(cls, path: str | Path) -> "Policy":
        data = json.loads(Path(path).read_text())
        return cls.from_dict(data)

    @classmethod
    def default(cls) -> "Policy":
        return cls.from_dict(DEFAULT_POLICY)

    @classmethod
    def real_alusi_policy(cls) -> "Policy":
        """Loads fixtures/alusi_model_policy.json -- a faithful, byte-for-
        byte copy of the real model_policy.json on ugos-mac-mini (fetched
        live, Phase 2 Workstream 2; contains no secrets, only cost/chain
        data). Used for equivalence testing against ai_router.py's actual
        real-world configuration, not as router_core's own default."""
        return cls.from_file(Path(__file__).parent / "fixtures" / "alusi_model_policy.json")

    def cost_per_call(self, tier_name: str, input_tokens: int, output_tokens: int) -> float:
        """Mirrors ai_router.py's _cost_per_tokens exactly (same branching
        on dict-shaped vs flat cost_per_1k_tokens)."""
        tier = self.tiers.get(tier_name, {})
        cpt = tier.get("cost_per_1k_tokens", 0)
        if isinstance(cpt, dict):
            return (input_tokens / 1000) * cpt.get("input", 0) + (output_tokens / 1000) * cpt.get("output", 0)
        return tier.get("cost_per_call", 0.0)

    def chain_for(self, task_type: str, fallback_chain: str = "standard") -> tuple[str, list[str]]:
        """Resolve a task_type to (chain_name, tier_list). Unknown task
        types fall back to `fallback_chain`, matching ai_router.py's own
        `.get(task_type, "standard")` behavior rather than raising."""
        chain_key = self.mapping.get(task_type, fallback_chain)
        chain = self.chains.get(chain_key, self.chains.get(fallback_chain, []))
        return chain_key, list(chain)
