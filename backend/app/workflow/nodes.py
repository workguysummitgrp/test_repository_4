"""LangGraph workflow node functions — US-012, US-013."""

import logging
from typing import Any

from backend.app.workflow.state import OnboardingState

logger = logging.getLogger(__name__)


async def start_node(state: dict[str, Any]) -> dict[str, Any]:
    """Entry point — marks workflow as started."""
    logger.info("Workflow started for application %s", state.get("application_str_id"))
    return {**state, "current_node": "llm_evaluation"}


async def llm_evaluation_node(state: dict[str, Any]) -> dict[str, Any]:
    """Invokes AI evaluation. Actual evaluation is performed by evaluation_service;
    this node transitions state."""
    logger.info("LLM evaluation for application %s", state.get("application_str_id"))
    return {**state, "current_node": "decision"}


async def decision_node(state: dict[str, Any]) -> dict[str, Any]:
    """Route based on score thresholds (configurable)."""
    score = state.get("score", 0)
    is_valid = state.get("is_valid_evaluation", True)

    if not is_valid:
        route = "reviewer_approver"
    elif score > 90:
        route = "auto_approve"
    elif score >= 80:
        route = "approver_only"
    elif score >= 70:
        route = "reviewer_approver"
    else:
        route = "auto_reject"

    logger.info("Application %s scored %d -> route: %s", state.get("application_str_id"), score, route)
    return {**state, "decision_route": route, "current_node": route}


async def auto_approval_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Auto-approving application %s", state.get("application_str_id"))
    return {**state, "current_node": "notification"}


async def auto_reject_node(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("Auto-rejecting application %s", state.get("application_str_id"))
    return {**state, "current_node": "notification"}


async def reviewer_node(state: dict[str, Any]) -> dict[str, Any]:
    """Pauses workflow for human reviewer input."""
    logger.info("Application %s routed to reviewer", state.get("application_str_id"))
    return {**state, "current_node": "reviewer_waiting"}


async def approver_node(state: dict[str, Any]) -> dict[str, Any]:
    """Pauses workflow for approver input."""
    logger.info("Application %s routed to approver", state.get("application_str_id"))
    return {**state, "current_node": "approver_waiting"}


async def notification_node(state: dict[str, Any]) -> dict[str, Any]:
    """Sends notifications on completion."""
    logger.info("Sending notifications for application %s", state.get("application_str_id"))
    return {**state, "current_node": "completed"}


def get_next_node(state: dict[str, Any]) -> str:
    """Conditional edge router for decision node."""
    route = state.get("decision_route", "reviewer_approver")
    route_map = {
        "auto_approve": "auto_approval",
        "approver_only": "approver",
        "reviewer_approver": "reviewer",
        "auto_reject": "rejection",
    }
    return route_map.get(route, "reviewer")
