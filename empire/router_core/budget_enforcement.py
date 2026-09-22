"""Real cost-limit enforcement -- closes the gap Phase 1 found and Phase 2
Workstream 1 re-confirmed: ai_router.py's model_policy.json declares
daily_hard_limit_usd/per_call_opus_limit_usd/heartbeat_allowed_providers,
but nothing in ai_router.py's code ever checks them. This module is that
enforcement, built for router_core's consolidated design (Workstream 2) --
not retroactively patched into the live ai_router.py, since that's a
live-host edit still gated behind Workstream 9's deployment validation.

Design: a BudgetEnforcer tracks real spend (caller-supplied via
record_spend after each real call) against global/per-model/daily/monthly
limits, with a warning threshold below the hard stop -- both configurable,
neither invented (values below default to model_policy.json's real
daily_hard_limit_usd=10.0 and per_call_opus_limit_usd=0.50, ported not
guessed).
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field


@dataclass
class BudgetStatus:
    state: str  # "ok" | "warning" | "hard_stop"
    daily_spent_usd: float
    daily_limit_usd: float
    monthly_spent_usd: float
    monthly_limit_usd: float | None
    reason: str | None = None


class BudgetEnforcer:
    """Tracks real spend and enforces global/per-model/daily/monthly
    limits with a warning threshold below the hard stop. In-memory only
    (matches engine.RouterState's Phase 1 design choice -- a persistent
    subclass is a straightforward extension, not built here so the test
    suite stays hermetic)."""

    def __init__(
        self,
        daily_limit_usd: float = 10.0,          # real default, model_policy.json
        monthly_limit_usd: float | None = None,  # not declared live -- None means unlimited
        per_model_daily_limit_usd: dict[str, float] | None = None,
        per_call_limit_usd: dict[str, float] | None = None,  # e.g. {"opus": 0.50}, real default
        warning_threshold_pct: float = 0.80,
        local_first_task_types: frozenset[str] = frozenset({"heartbeat", "health_check", "monitoring", "cron_task"}),
    ):
        self.daily_limit_usd = daily_limit_usd
        self.monthly_limit_usd = monthly_limit_usd
        self.per_model_daily_limit_usd = dict(per_model_daily_limit_usd or {})
        self.per_call_limit_usd = dict(per_call_limit_usd or {"opus": 0.50})
        self.warning_threshold_pct = warning_threshold_pct
        self.local_first_task_types = local_first_task_types

        self._daily_spend: dict[str, float] = {}       # date_str -> total usd
        self._daily_spend_by_model: dict[tuple[str, str], float] = {}  # (date_str, model) -> usd
        self._monthly_spend: dict[str, float] = {}      # "YYYY-MM" -> total usd

    @staticmethod
    def _today() -> str:
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    @staticmethod
    def _this_month() -> str:
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m")

    def record_spend(self, model: str, cost_usd: float) -> None:
        """Called after a real provider call completes -- records actual
        spend, not an estimate. This is what makes the daily/monthly
        totals real rather than projected."""
        day = self._today()
        month = self._this_month()
        self._daily_spend[day] = self._daily_spend.get(day, 0.0) + cost_usd
        key = (day, model)
        self._daily_spend_by_model[key] = self._daily_spend_by_model.get(key, 0.0) + cost_usd
        self._monthly_spend[month] = self._monthly_spend.get(month, 0.0) + cost_usd

    def daily_spent(self) -> float:
        return self._daily_spend.get(self._today(), 0.0)

    def daily_spent_for_model(self, model: str) -> float:
        return self._daily_spend_by_model.get((self._today(), model), 0.0)

    def monthly_spent(self) -> float:
        return self._monthly_spend.get(self._this_month(), 0.0)

    def status(self) -> BudgetStatus:
        """Global daily/monthly status, independent of any specific
        candidate -- used for a dashboard-style check."""
        spent = self.daily_spent()
        monthly = self.monthly_spent()
        if spent >= self.daily_limit_usd:
            return BudgetStatus("hard_stop", spent, self.daily_limit_usd, monthly,
                                 self.monthly_limit_usd, reason="daily_hard_limit_reached")
        if self.monthly_limit_usd is not None and monthly >= self.monthly_limit_usd:
            return BudgetStatus("hard_stop", spent, self.daily_limit_usd, monthly,
                                 self.monthly_limit_usd, reason="monthly_hard_limit_reached")
        if spent >= self.daily_limit_usd * self.warning_threshold_pct:
            return BudgetStatus("warning", spent, self.daily_limit_usd, monthly,
                                 self.monthly_limit_usd, reason="approaching_daily_limit")
        return BudgetStatus("ok", spent, self.daily_limit_usd, monthly, self.monthly_limit_usd)

    def would_exceed(self, tier_name: str, model: str, estimated_cost_usd: float) -> tuple[bool, str | None]:
        """Checks whether a specific candidate call should be blocked
        BEFORE it happens -- this is the real enforcement point Phase 1
        found missing entirely. Returns (should_block, reason).

        Real automatic downgrade behavior: this does not raise or halt
        the whole request -- Router.route() (see router.py's
        budget-aware ranking) treats a blocked candidate as ineligible
        and tries the next one in the chain, which is exactly "automatic
        downgrade" / "automatic local-first execution" in practice: a
        blocked premium tier falls through to the next-cheapest eligible
        candidate, same mechanism as a circuit-broken provider."""
        # Per-call limit (e.g. opus) -- real default ported from
        # model_policy.json's per_call_opus_limit_usd.
        per_call_limit = self.per_call_limit_usd.get(tier_name)
        if per_call_limit is not None and estimated_cost_usd > per_call_limit:
            return True, f"per_call_limit_exceeded:{tier_name}"

        # Per-model daily budget.
        model_limit = self.per_model_daily_limit_usd.get(model)
        if model_limit is not None:
            if self.daily_spent_for_model(model) + estimated_cost_usd > model_limit:
                return True, f"per_model_daily_limit_exceeded:{model}"

        # Global daily budget.
        if self.daily_spent() + estimated_cost_usd > self.daily_limit_usd:
            return True, "daily_hard_limit_would_be_exceeded"

        # Global monthly budget.
        if self.monthly_limit_usd is not None:
            if self.monthly_spent() + estimated_cost_usd > self.monthly_limit_usd:
                return True, "monthly_hard_limit_would_be_exceeded"

        return False, None

    def enforce_local_first(self, task_type: str, tier_name: str) -> tuple[bool, str | None]:
        """Real enforcement of model_policy.json's
        heartbeat_allowed_providers -- another declared-but-unenforced
        field found in Phase 1. Blocks any non-local tier for a task type
        flagged local-first-only, rather than just weighting toward
        local as a preference."""
        if task_type in self.local_first_task_types and tier_name not in ("local", "ollama"):
            return True, f"local_first_task_type_blocked_non_local_tier:{task_type}"
        return False, None
