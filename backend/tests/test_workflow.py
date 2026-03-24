"""Tests for workflow routing logic — US-012, US-013."""

import pytest
from backend.app.workflow.nodes import decision_node, get_next_node
from backend.app.services.workflow_service import _determine_route
from backend.app.models.workflow_state import DecisionRoute


class TestDecisionRouting:
    def test_auto_approve_high_score(self):
        route = _determine_route(95, True)
        assert route == DecisionRoute.AUTO_APPROVE

    def test_approver_only_score_80_90(self):
        route = _determine_route(85, True)
        assert route == DecisionRoute.APPROVER_ONLY

    def test_reviewer_approver_score_70_80(self):
        route = _determine_route(75, True)
        assert route == DecisionRoute.REVIEWER_APPROVER

    def test_auto_reject_low_score(self):
        route = _determine_route(50, True)
        assert route == DecisionRoute.AUTO_REJECT

    def test_invalid_evaluation_goes_to_reviewer(self):
        route = _determine_route(95, False)
        assert route == DecisionRoute.REVIEWER_APPROVER

    def test_boundary_90(self):
        route = _determine_route(90, True)
        assert route == DecisionRoute.APPROVER_ONLY

    def test_boundary_80(self):
        route = _determine_route(80, True)
        assert route == DecisionRoute.APPROVER_ONLY

    def test_boundary_70(self):
        route = _determine_route(70, True)
        assert route == DecisionRoute.REVIEWER_APPROVER

    def test_boundary_69(self):
        route = _determine_route(69, True)
        assert route == DecisionRoute.AUTO_REJECT


class TestGetNextNode:
    def test_auto_approve_route(self):
        state = {"decision_route": "auto_approve"}
        assert get_next_node(state) == "auto_approval"

    def test_approver_only_route(self):
        state = {"decision_route": "approver_only"}
        assert get_next_node(state) == "approver"

    def test_reviewer_route(self):
        state = {"decision_route": "reviewer_approver"}
        assert get_next_node(state) == "reviewer"

    def test_auto_reject_route(self):
        state = {"decision_route": "auto_reject"}
        assert get_next_node(state) == "rejection"

    def test_unknown_route_defaults_to_reviewer(self):
        state = {"decision_route": "unknown"}
        assert get_next_node(state) == "reviewer"


@pytest.mark.asyncio
class TestDecisionNode:
    async def test_high_score_auto_approve(self):
        state = {"score": 95, "is_valid_evaluation": True, "application_str_id": "APP-001"}
        result = await decision_node(state)
        assert result["decision_route"] == "auto_approve"

    async def test_low_score_auto_reject(self):
        state = {"score": 30, "is_valid_evaluation": True, "application_str_id": "APP-002"}
        result = await decision_node(state)
        assert result["decision_route"] == "auto_reject"

    async def test_invalid_eval_routes_to_reviewer(self):
        state = {"score": 95, "is_valid_evaluation": False, "application_str_id": "APP-003"}
        result = await decision_node(state)
        assert result["decision_route"] == "reviewer_approver"
