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

    @classmethod
    def from_dict(cls, data: dict) -> "Policy":
        return cls(
            chains=dict(data.get("chains", {})),
            mapping=dict(data.get("mapping", {})),
            cost_limits=dict(data.get("cost_limits", {})),
        )

    @classmethod
    def from_file(cls, path: str | Path) -> "Policy":
        data = json.loads(Path(path).read_text())
        return cls.from_dict(data)

    @classmethod
    def default(cls) -> "Policy":
        return cls.from_dict(DEFAULT_POLICY)

    def chain_for(self, task_type: str, fallback_chain: str = "standard") -> tuple[str, list[str]]:
        """Resolve a task_type to (chain_name, tier_list). Unknown task
        types fall back to `fallback_chain`, matching ai_router.py's own
        `.get(task_type, "standard")` behavior rather than raising."""
        chain_key = self.mapping.get(task_type, fallback_chain)
        chain = self.chains.get(chain_key, self.chains.get(fallback_chain, []))
        return chain_key, list(chain)
