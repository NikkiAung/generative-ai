"""
State schema for the Research Assistant Agent.

WHY a separate file?
    In real projects, the state schema is shared across multiple files.
    Keeping it in its own module makes it the single source of truth.
"""

import operator
from typing import Annotated, TypedDict


class ResearchState(TypedDict):
    """The shared state for the research assistant agent."""

    # User input
    question: str

    # Search results accumulated via reducer
    search_results: Annotated[list, operator.add]

    # Number of searches performed
    search_count: int

    # LLM's analysis of search results
    analysis: str

    # Whether the agent has enough information
    has_enough_info: bool

    # The final response draft
    draft_response: str

    # Human feedback (from HITL)
    human_feedback: str

    # The final published response
    final_response: str

    # Current status for routing
    status: str
