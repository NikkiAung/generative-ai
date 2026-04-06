"""
Graph construction for the Research Assistant Agent.

This file builds the graph by connecting nodes with edges.
"""

from langgraph.graph import StateGraph, START, END
from state import ResearchState
from nodes import intake_node, search_node, analyze_node, respond_node, finalize_node


def should_search(state) -> str:
    """Route: search or answer directly?"""
    if state["status"] == "needs_search":
        return "search"
    return "respond"


def need_more_info(state) -> str:
    """Route: search again or respond?"""
    if state["has_enough_info"]:
        return "respond"
    return "search"


def build_research_graph(checkpointer=None, enable_hitl=False):
    """Build and compile the research assistant graph."""
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("intake", intake_node)
    graph.add_node("search", search_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("respond", respond_node)
    graph.add_node("finalize", finalize_node)

    # Edges
    graph.add_edge(START, "intake")
    graph.add_conditional_edges("intake", should_search, {"search": "search", "respond": "respond"})
    graph.add_edge("search", "analyze")
    graph.add_conditional_edges("analyze", need_more_info, {"search": "search", "respond": "respond"})
    graph.add_edge("respond", "finalize")
    graph.add_edge("finalize", END)

    # Compile with optional checkpointer and HITL
    compile_kwargs = {}
    if checkpointer:
        compile_kwargs["checkpointer"] = checkpointer
    if enable_hitl:
        compile_kwargs["interrupt_before"] = ["finalize"]

    return graph.compile(**compile_kwargs)
