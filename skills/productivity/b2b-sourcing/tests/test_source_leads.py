"""Tests for B2B lead sourcing pipeline — scoring, normalization, edge cases."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from source_leads import score_lead


class TestScoreLead(unittest.TestCase):

    # ------------------------------------------------------------------
    # Staff-size band
    # ------------------------------------------------------------------

    def test_dental_in_band_scores_2(self):
        assert score_lead({"niche": "dental", "employee_count": 8}) >= 2

    def test_dental_at_lower_bound_scores_2(self):
        assert score_lead({"niche": "dental", "employee_count": 4}) >= 2

    def test_dental_at_upper_bound_scores_2(self):
        assert score_lead({"niche": "dental", "employee_count": 15}) >= 2

    def test_dental_dso_size_scores_0_for_size(self):
        lead = {"niche": "dental", "employee_count": 200}
        assert score_lead(lead) < score_lead({**lead, "employee_count": 8})

    def test_law_in_band_scores_2(self):
        assert score_lead({"niche": "law", "employee_count": 5}) >= 2

    def test_law_solo_practitioner_scores_0_for_size(self):
        lead = {"niche": "law", "employee_count": 1}
        bigger = {**lead, "employee_count": 5}
        assert score_lead(lead) < score_lead(bigger)

    def test_real_estate_in_band_scores_2(self):
        assert score_lead({"niche": "real-estate", "employee_count": 12}) >= 2

    # ------------------------------------------------------------------
    # Growth signal
    # ------------------------------------------------------------------

    def test_growth_signal_adds_2(self):
        base = {"niche": "dental", "employee_count": 8}
        with_signal = {**base, "growth_signal": "Hiring front desk coordinator"}
        assert score_lead(with_signal) == score_lead(base) + 2

    def test_empty_growth_signal_not_counted(self):
        base = {"niche": "dental", "employee_count": 8}
        empty = {**base, "growth_signal": ""}
        assert score_lead(empty) == score_lead(base)

    # ------------------------------------------------------------------
    # Automation tools — no tools = +1
    # ------------------------------------------------------------------

    def test_no_automation_tools_adds_1(self):
        base = {"niche": "dental", "employee_count": 8}
        with_tools = {**base, "technologies": ["zapier", "quickbooks"]}
        assert score_lead(base) == score_lead(with_tools) + 1

    def test_non_automation_tech_not_penalised(self):
        base = {"niche": "dental", "employee_count": 8}
        with_nonauto = {**base, "technologies": ["quickbooks", "google workspace"]}
        assert score_lead(base) == score_lead(with_nonauto)

    def test_technologies_none_treated_as_no_tools(self):
        lead = {"niche": "dental", "employee_count": 8, "technologies": None}
        assert score_lead(lead) == score_lead({"niche": "dental", "employee_count": 8})

    # ------------------------------------------------------------------
    # Decision-maker title
    # ------------------------------------------------------------------

    def test_owner_title_adds_1(self):
        base = {"niche": "dental", "employee_count": 8}
        with_owner = {**base, "decision_maker_title": "Practice Owner"}
        assert score_lead(with_owner) == score_lead(base) + 1

    def test_dr_prefix_adds_1(self):
        base = {"niche": "dental", "employee_count": 8}
        with_dr = {**base, "decision_maker_title": "Dr. Jane Smith DDS"}
        assert score_lead(with_dr) == score_lead(base) + 1

    def test_office_manager_title_does_not_add(self):
        base = {"niche": "dental", "employee_count": 8}
        with_mgr = {**base, "decision_maker_title": "Office Manager"}
        assert score_lead(with_mgr) == score_lead(base)

    def test_missing_title_does_not_raise(self):
        score_lead({"niche": "dental"})  # must not crash

    # ------------------------------------------------------------------
    # Independent (not chain / DSO)
    # ------------------------------------------------------------------

    def test_independent_name_adds_1(self):
        base = {"niche": "dental", "employee_count": 8, "company_name": "Sunrise Dental"}
        chain = {**base, "company_name": "Aspen Dental Group"}
        assert score_lead(base) > score_lead(chain)

    def test_dso_in_name_penalised(self):
        lead = {"niche": "dental", "employee_count": 8, "company_name": "Chicago DSO Partners"}
        assert score_lead(lead) < score_lead({"niche": "dental", "employee_count": 8})

    def test_keller_williams_in_name_penalised(self):
        lead = {"niche": "real-estate", "employee_count": 12, "company_name": "Keller Williams Preferred"}
        independent = {"niche": "real-estate", "employee_count": 12, "company_name": "West Side Realty"}
        assert score_lead(independent) > score_lead(lead)

    # ------------------------------------------------------------------
    # Email found
    # ------------------------------------------------------------------

    def test_email_found_adds_1(self):
        base = {"niche": "dental", "employee_count": 8}
        with_email = {**base, "email": "dr.smith@sunshinedental.com"}
        assert score_lead(with_email) == score_lead(base) + 1

    def test_empty_email_not_counted(self):
        base = {"niche": "dental", "employee_count": 8}
        empty_email = {**base, "email": ""}
        assert score_lead(empty_email) == score_lead(base)

    # ------------------------------------------------------------------
    # Score ceiling and floor
    # ------------------------------------------------------------------

    def test_perfect_lead_scores_at_most_8(self):
        lead = {
            "niche": "dental",
            "employee_count": 8,
            "growth_signal": "Hiring front desk",
            "technologies": [],
            "decision_maker_title": "Practice Owner",
            "company_name": "Sunrise Dental",
            "email": "owner@sunshinedental.com",
        }
        assert score_lead(lead) == 8

    def test_empty_lead_scores_2(self):
        # Blank lead scores 2: "no automation tools" (+1) and "independent" (+1)
        # both fire because empty strings/lists contain no chain or automation keywords.
        assert score_lead({}) == 2

    def test_score_never_negative(self):
        assert score_lead({"niche": "dental", "employee_count": 1000, "technologies": ["zapier"]}) >= 0


class TestEmailNormalization(unittest.TestCase):
    """Smoke-tests for the verify_email_hunter wrapper (mocked HTTP)."""

    def test_missing_hunter_key_returns_empty(self):
        import os
        from unittest.mock import patch
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import source_leads as sl
            result = sl.verify_email_hunter("Jane", "Doe", "example.com")
        assert result == {}


if __name__ == "__main__":
    unittest.main()
