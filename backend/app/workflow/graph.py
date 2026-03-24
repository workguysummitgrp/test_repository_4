"""LangGraph workflow graph definition — US-012, US-013."""

from langgraph.graph import END, StateGraph

from backend.app.workflow.nodes import (
    approver_node,
    auto_approval_node,
    auto_reject_node,
    decision_node,
    get_next_node,
    llm_evaluation_node,
    notification_node,
    reviewer_node,
    start_node,
)


def build_onboarding_graph() -> StateGraph:
    """Construct the LangGraph workflow for onboarding processing."""
    graph = StateGraph(dict)

    # Add nodes
    graph.add_node("start", start_node)
    graph.add_node("llm_evaluation", llm_evaluation_node)
    graph.add_node("decision", decision_node)
    graph.add_node("auto_approval", auto_approval_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("approver", approver_node)
    graph.add_node("rejection", auto_reject_node)
    graph.add_node("notification", notification_node)

    # Edges
    graph.set_entry_point("start")
    graph.add_edge("start", "llm_evaluation")
    graph.add_edge("llm_evaluation", "decision")
    graph.add_conditional_edges("decision", get_next_node, {
        "auto_approval": "auto_approval",
        "approver": "approver",
        "reviewer": "reviewer",
        "rejection": "rejection",
    })
    graph.add_edge("auto_approval", "notification")
    graph.add_edge("rejection", "notification")
    graph.add_edge("notification", END)
    # reviewer and approver nodes pause the workflow (human-in-the-loop)

    return graph


# Compiled graph singleton
onboarding_workflow = build_onboarding_graph().compile()
