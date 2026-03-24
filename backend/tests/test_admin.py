"""Tests for admin service — US-014, US-027, US-028."""

import pytest
from backend.app.services.admin_service import DEFAULT_THRESHOLDS, DEFAULT_WORKFLOW_NODES


class TestAdminDefaults:
    def test_default_thresholds_cover_full_range(self):
        all_ranges = set()
        for t in DEFAULT_THRESHOLDS:
            for score in range(t["min_score"], t["max_score"] + 1):
                all_ranges.add(score)
        assert 0 in all_ranges
        assert 100 in all_ranges

    def test_default_thresholds_no_gaps(self):
        sorted_thresholds = sorted(DEFAULT_THRESHOLDS, key=lambda x: x["min_score"])
        for i in range(len(sorted_thresholds) - 1):
            current_max = sorted_thresholds[i]["max_score"]
            next_min = sorted_thresholds[i + 1]["min_score"]
            assert next_min <= current_max + 1, f"Gap between {current_max} and {next_min}"

    def test_default_workflow_nodes_contain_required(self):
        required = {"start", "llm_evaluation", "decision", "auto_approval", "reviewer", "approver", "rejection", "notification", "completed"}
        assert required.issubset(set(DEFAULT_WORKFLOW_NODES))

    def test_threshold_band_names(self):
        names = {t["band_name"] for t in DEFAULT_THRESHOLDS}
        assert "auto_approve" in names
        assert "approver_only" in names
        assert "reviewer_approver" in names
        assert "auto_reject" in names
