"""
Node functions for the Research Assistant Agent.

Each function is a graph node that takes ResearchState and returns updates.
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import AIMessage

load_dotenv()

# Import the search tool
from tools import web_search

# LLM Setup
if os.getenv("GOOGLE_API_KEY"):
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    USE_MOCK = False
else:
    USE_MOCK = True


def intake_node(state):
    """Receive the user's question and prepare for processing."""
    question = state["question"]
    print(f"\n  📥 INTAKE: Received question: '{question}'")

    # Decide whether this needs search or can be answered directly
    needs_search = any(word in question.lower() for word in [
        "what", "how", "why", "explain", "tell me", "search", "find", "look up"
    ])

    return {
        "status": "needs_search" if needs_search else "can_answer_directly",
        "search_count": 0,
        "has_enough_info": False,
    }


def search_node(state):
    """Execute a web search for the user's question."""
    query = state["question"]
    count = state["search_count"]
    print(f"\n  🔍 SEARCH #{count + 1}: Searching for '{query}'")

    result = web_search.invoke({"query": query})
    print(f"     Found: {str(result)[:80]}...")

    return {
        "search_results": [result],
        "search_count": count + 1,
        "status": "search_complete",
    }


def analyze_node(state):
    """Analyze search results and decide if we have enough info."""
    results = state["search_results"]
    count = state["search_count"]
    print(f"\n  🧠 ANALYZE: Reviewing {len(results)} search result(s)")

    if USE_MOCK:
        # Mock analysis
        has_enough = count >= 1  # One search is enough for mock
        analysis = f"[Mock analysis] Found {len(results)} results. {'Sufficient' if has_enough else 'Need more'}."
    else:
        from langchain_core.messages import HumanMessage
        analysis_prompt = (
            f"Analyze these search results for the question: '{state['question']}'\n"
            f"Results: {results}\n"
            f"Do you have enough information to answer? Respond with your analysis."
        )
        response = llm.invoke([HumanMessage(content=analysis_prompt)])
        analysis = response.content
        has_enough = count >= 1

    print(f"     Analysis: {analysis[:80]}...")
    print(f"     Enough info: {has_enough}")

    return {
        "analysis": analysis,
        "has_enough_info": has_enough,
        "status": "analyzed",
    }


def respond_node(state):
    """Generate the draft response."""
    question = state["question"]
    results = state.get("search_results", [])
    analysis = state.get("analysis", "")

    print(f"\n  ✍️  RESPOND: Generating draft response")

    if USE_MOCK:
        if results:
            draft = (
                f"Based on my research about '{question}':\n\n"
                f"Here's what I found:\n"
                + "\n".join(f"  • {r[:100]}" for r in results) +
                f"\n\nIn summary, the search results provide comprehensive "
                f"information about this topic."
            )
        else:
            draft = f"Regarding '{question}': This is a straightforward topic I can address directly without additional research."
    else:
        from langchain_core.messages import HumanMessage
        prompt = (
            f"Question: {question}\n"
            f"Search results: {results}\n"
            f"Analysis: {analysis}\n"
            f"Generate a comprehensive response."
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        draft = response.content

    print(f"     Draft preview: {draft[:80]}...")

    return {"draft_response": draft, "status": "draft_ready"}


def finalize_node(state):
    """Finalize the response with any human feedback applied."""
    draft = state["draft_response"]
    feedback = state.get("human_feedback", "")

    print(f"\n  ✅ FINALIZE: Publishing response")

    if feedback:
        final = f"{draft}\n\n[Revised based on feedback: {feedback}]"
        # to fix the draft base on feed
        llm.invoke
    else:
        final = draft

    return {"final_response": final, "status": "complete"}
