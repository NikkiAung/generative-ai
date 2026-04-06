"""
Tool definitions for the Research Assistant Agent.
"""

from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for information on a topic."""
    # Mock search results for learning purposes
    knowledge_base = {
        "langgraph": (
            "LangGraph is a library by LangChain for building stateful, multi-actor "
            "applications with LLMs. It uses a graph-based approach where nodes are "
            "functions and edges define the execution flow. Key features include "
            "checkpointing, human-in-the-loop support, and streaming."
        ),
        "react pattern": (
            "The ReAct (Reason + Act) pattern is an AI agent paradigm where the LLM "
            "alternates between reasoning about what to do and taking actions (calling tools). "
            "The loop continues until the LLM has enough information to respond."
        ),
        "checkpoint": (
            "LangGraph checkpointing saves the graph state after each node execution. "
            "This enables crash recovery, time travel (rewinding to previous states), "
            "and multi-turn conversations. Supported backends include MemorySaver (dev) "
            "and MongoDBSaver (production)."
        ),
        "python": (
            "Python is a high-level programming language created by Guido van Rossum in 1991. "
            "It's known for its clean syntax and extensive library ecosystem. "
            "Python is widely used in AI, data science, web development, and automation."
        ),
        "express": (
            "Express.js is a minimal web framework for Node.js. It provides routing, "
            "middleware support, and HTTP utilities. It's the most popular backend "
            "framework in the JavaScript ecosystem."
        ),
    }

    for key, info in knowledge_base.items():
        if key in query.lower():
            return f"[Search result for '{query}']: {info}"

    return f"[Search result for '{query}']: General information found. The topic is well-documented."


# List of available tools
tools = [web_search]
