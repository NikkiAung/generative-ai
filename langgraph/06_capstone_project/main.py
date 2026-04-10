"""
Research Assistant Agent — 06_capstone_project/main.py

The entry point for the complete research agent that combines:
- StateGraph with conditional edges and loops
- LLM integration (with mock fallback)
- Tool calling (web search)
- Checkpointing (MemorySaver)
- Human-in-the-loop (interrupt before finalize)

Run: python 06_capstone_project/main.py
"""

import sys
import os

# Add the capstone directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from langgraph.checkpoint.memory import MemorySaver
from graph import build_research_graph


def main():
    print("\n" + "=" * 70)
    print("🔬 RESEARCH ASSISTANT AGENT — Capstone Project")
    print("=" * 70)
    print("This agent combines ALL concepts: state, edges, loops, LLM,")
    print("tools, checkpointing, and human-in-the-loop.\n")

    checkpointer = MemorySaver()

    # ========================================
    # DEMO 1: Simple question (no search needed)
    # ========================================
    print("=" * 60)
    print("DEMO 1: Direct answer (no search)")
    print("=" * 60)

    app = build_research_graph(checkpointer=checkpointer)
    config1 = {"configurable": {"thread_id": "demo-1"}}

    result1 = app.invoke({
        "question": "Hello!",  # Bug 2 fix: no search keywords → routes directly to respond
        "search_results": [],
        "search_count": 0,
        "search_query": "",
        "analysis": "",
        "has_enough_info": False,
        "draft_response": "",
        "human_feedback": "",
        "final_response": "",
        "status": "new",
    }, config=config1)

    print(f"\n  📋 Status: {result1['status']}")
    print(f"  📝 Response: {result1['final_response'][:100]}...")

    # ========================================
    # DEMO 2: Research question (triggers search)
    # ========================================
    print(f"\n{'=' * 60}")
    print("DEMO 2: Research question (triggers search + analysis)")
    print("=" * 60)

    config2 = {"configurable": {"thread_id": "demo-2"}}

    result2 = app.invoke({
        "question": "What is LangGraph and how does it work?",
        "search_results": [],
        "search_count": 0,
        "search_query": "",
        "analysis": "",
        "has_enough_info": False,
        "draft_response": "",
        "human_feedback": "",
        "final_response": "",
        "status": "new",
    }, config=config2)

    print(f"\n  📋 Status: {result2['status']}")
    print(f"  🔍 Searches performed: {result2['search_count']}")
    print(f"  📝 Response:\n     {result2['final_response'][:200]}...")

    # ========================================
    # DEMO 3: Human-in-the-loop
    # ========================================
    print(f"\n{'=' * 60}")
    print("DEMO 3: Human-in-the-loop (pause before publish)")
    print("=" * 60)

    hitl_checkpointer = MemorySaver()
    hitl_app = build_research_graph(checkpointer=hitl_checkpointer, enable_hitl=True)
    config3 = {"configurable": {"thread_id": "demo-3"}}

    # Run — will pause before finalize
    result3 = hitl_app.invoke({
        "question": "Explain the ReAct pattern in AI",
        "search_results": [],
        "search_count": 0,
        "search_query": "",
        "analysis": "",
        "has_enough_info": False,
        "draft_response": "",
        "human_feedback": "",
        "final_response": "",
        "status": "new",
    }, config=config3)

    paused_state = hitl_app.get_state(config3)
    print(f"\n  🛑 Graph PAUSED before finalize!")
    print(f"     Status: {paused_state.values.get('status')}")
    print(f"     Draft: {paused_state.values.get('draft_response', '')[:80]}...")
    print(f"     Next: {paused_state.next}")

    # Human provides feedback
    hitl_app.update_state(config3, {"human_feedback": "Add more practical examples"})
    print(f"\n  📝 Human feedback added: 'Add more practical examples'")

    # Resume
    final_result = hitl_app.invoke(None, config=config3)
    print(f"\n  ✅ Resumed and finalized!")
    print(f"     Final response: {final_result['final_response'][:150]}...")

    # ========================================
    # SUMMARY
    # ========================================
    print(f"\n{'=' * 70}")
    print("🎉 CAPSTONE COMPLETE!")
    print("=" * 70)

    print("""
  What this agent demonstrated:

  ✅ State management    — ResearchState TypedDict with reducers
  ✅ Conditional edges   — Search vs direct answer routing
  ✅ Loops               — Search again if not enough info
  ✅ LLM integration     — Mock fallback for zero-cost learning
  ✅ Tool calling        — Web search tool
  ✅ Checkpointing       — MemorySaver (swappable to MongoDB)
  ✅ Human-in-the-loop   — Pause for review before publish
  ✅ Multi-file project  — state.py, tools.py, nodes.py, graph.py, main.py

  🔧 TO MAKE THIS PRODUCTION-READY:
  1. Swap MemorySaver → MongoDBSaver
  2. Add real search API (Tavily, SerpAPI, etc.)
  3. Set GOOGLE_API_KEY for real LLM responses (free: https://aistudio.google.com/apikey)
  4. Add error handling nodes
  5. Add streaming for real-time UI updates
  6. Add TTL cleanup for old checkpoints

  🎯 You've completed the LangGraph Learning Lab! 🎯
    """)


if __name__ == "__main__":
    main()
