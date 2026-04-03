"""
Multiple Nodes Pipeline — 00_foundations/03_multiple_nodes.py

WHAT THIS TEACHES:
    A 3-node data processing pipeline where each node transforms the state.
    This shows how LangGraph works as a data pipeline — like Express middleware.

WHAT YOU WILL SEE:
    A text processing pipeline that takes raw input, cleans it, analyzes it,
    and formats the output. Each step prints its work clearly.

EXPRESS.JS PARALLEL:
    This is like a middleware chain that processes a request:
        app.use(parseBody)       →  validate node
        app.use(authenticate)    →  transform node
        app.use(handleRequest)   →  format node

PREREQUISITES:
    Run 00_foundations/02_state_basics.py first.
"""

# ========================================
# SETUP
# ========================================
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# ========================================
# STEP 1: Define a Richer State
# ========================================
print("\n" + "=" * 50)
print("STEP 1: Defining state for a text processing pipeline")
print("=" * 50)

# CONCEPT: For a data pipeline, the state carries data through stages.
# Each stage reads the previous stage's output and writes its own.
# EXPRESS PARALLEL: Like req.body being enriched as it passes through middleware.

class State(TypedDict):
    raw_input: str          # Original user input
    cleaned_text: str       # After cleaning (lowercase, trim)
    word_count: int         # After analysis
    char_count: int         # After analysis
    formatted_output: str   # Final formatted result

print("State schema: raw_input → cleaned_text → word_count/char_count → formatted_output")


# ========================================
# STEP 2: Define Pipeline Nodes
# ========================================
print("\n" + "=" * 50)
print("STEP 2: Defining 3 pipeline nodes")
print("=" * 50)

def validate_and_clean(state: State) -> dict:
    """Stage 1: Validate input and clean the text."""
    print("\n  🔵 STAGE 1: Validate & Clean")
    raw = state["raw_input"]
    print(f"  Input received: '{raw}'")

    # CONCEPT: This node does one thing well — clean the text.
    # WHY: Each node should have a single responsibility.
    # EXPRESS PARALLEL: Like a bodyParser middleware that only parses/cleans request body.
    cleaned = raw.strip().lower()
    print(f"  Cleaned text:   '{cleaned}'")

    return {"cleaned_text": cleaned}


def analyze(state: State) -> dict:
    """Stage 2: Analyze the cleaned text."""
    print("\n  🟢 STAGE 2: Analyze")
    text = state["cleaned_text"]
    print(f"  Analyzing: '{text}'")

    # CONCEPT: This node reads what Stage 1 wrote and adds its own data.
    # The state keeps growing with new information.
    words = len(text.split())
    chars = len(text)
    print(f"  Word count: {words}")
    print(f"  Char count: {chars}")

    return {"word_count": words, "char_count": chars}


def format_output(state: State) -> dict:
    """Stage 3: Create a formatted summary."""
    print("\n  🟠 STAGE 3: Format Output")

    # CONCEPT: This node reads from ALL previous stages to create the final output.
    # It has access to: raw_input, cleaned_text, word_count, char_count.
    output = (
        f"📊 Text Analysis Report\n"
        f"  Original:  '{state['raw_input']}'\n"
        f"  Cleaned:   '{state['cleaned_text']}'\n"
        f"  Words:     {state['word_count']}\n"
        f"  Characters: {state['char_count']}"
    )
    print(f"  Formatted output created")

    return {"formatted_output": output}


print("Pipeline: validate_and_clean → analyze → format_output")


# ========================================
# STEP 3: Build and Run
# ========================================
print("\n" + "=" * 50)
print("STEP 3: Building the pipeline graph")
print("=" * 50)

graph = StateGraph(State)

# Add nodes
graph.add_node("validate_and_clean", validate_and_clean)
graph.add_node("analyze", analyze)
graph.add_node("format_output", format_output)

# Add edges — a straight pipeline
graph.add_edge(START, "validate_and_clean")
graph.add_edge("validate_and_clean", "analyze")
graph.add_edge("analyze", "format_output")
graph.add_edge("format_output", END)

app = graph.compile()

# Run with sample input
initial_state = {
    "raw_input": "  Hello World! This is LangGraph Learning Lab.  ",
    "cleaned_text": "",
    "word_count": 0,
    "char_count": 0,
    "formatted_output": "",
}

print(f"Input: '{initial_state['raw_input']}'")
print("\n--- Running the pipeline ---")

final_state = app.invoke(initial_state)


# ========================================
# STEP 4: Show the Final Result
# ========================================
print("\n" + "=" * 50)
print("STEP 4: Final Result")
print("=" * 50)

print(f"\n{final_state['formatted_output']}")


# ========================================
# STEP 5: Run a Second Example
# ========================================
print("\n" + "=" * 50)
print("STEP 5: Running with different input")
print("=" * 50)

second_input = {
    "raw_input": "   LangGraph Is Like Express.js For AI!   ",
    "cleaned_text": "",
    "word_count": 0,
    "char_count": 0,
    "formatted_output": "",
}

print(f"Input: '{second_input['raw_input']}'")
print("\n--- Running the pipeline ---")

final_state_2 = app.invoke(second_input)

print(f"\n{final_state_2['formatted_output']}")


# ========================================
# STEP 6: Key Takeaways
# ========================================
print("\n" + "=" * 50)
print("STEP 6: Key takeaways")
print("=" * 50)

print("""
🎯 What this pipeline demonstrated:

1. SAME GRAPH, DIFFERENT INPUT
   - We ran the pipeline twice with different strings
   - The graph is REUSABLE — just like Express routes handle different requests

2. EACH NODE HAS ONE JOB
   - validate_and_clean → only cleans text
   - analyze → only counts words/chars
   - format_output → only creates the report
   This is the Single Responsibility Principle, same as in Express middleware

3. DATA ACCUMULATES IN STATE
   - Stage 1 added cleaned_text
   - Stage 2 added word_count and char_count
   - Stage 3 read everything and created formatted_output
   The state grows richer as it passes through the pipeline

4. THIS IS A LINEAR PIPELINE (no branching yet!)
   - START → A → B → C → END
   - Next section: we'll add BRANCHING (conditional edges)
   - That's where LangGraph gets interesting
""")

# TRY THIS: Add a 4th node that checks if the text is too short (< 3 words)
# and adds a warning to the formatted_output. Can you add it between
# analyze and format_output?


# ========================================
# WHAT YOU LEARNED
# ========================================
# 1. Multiple nodes form a pipeline — each reading from and writing to shared state
# 2. The graph is reusable — invoke() with different inputs runs the same pipeline
# 3. State accumulates data — later nodes can read what earlier nodes wrote
# 4. Linear pipelines are simple but limited — next we add BRANCHING
#
# NEXT: 01_core_concepts/CONCEPT.md — Learn about edges, conditions, and loops
# ========================================