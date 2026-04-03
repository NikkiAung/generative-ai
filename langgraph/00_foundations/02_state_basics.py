"""
State Basics — 00_foundations/02_state_basics.py

WHAT THIS TEACHES:
    How state is created, passed to nodes, modified, and passed to the next node.
    You will SEE the state changing step by step in the terminal.

WHAT YOU WILL SEE:
    The state printed BEFORE and AFTER each node runs, so you can visually
    track how data transforms as it flows through the graph.

EXPRESS.JS PARALLEL:
    This is like logging req.body before and after each middleware:
        app.use((req, res, next) => {
            console.log('BEFORE:', req.body);
            req.body.count++;
            console.log('AFTER:', req.body);
            next();
        });

PREREQUISITES:
    Run 00_foundations/01_hello_graph.py first.
"""

# ========================================
# SETUP
# ========================================
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# ========================================
# STEP 1: Define a State with MULTIPLE Fields
# ========================================
print("\n" + "=" * 50)
print("STEP 1: Defining a state with 3 different types")
print("=" * 50)

# CONCEPT: State can have multiple fields of different types.
# This is like a TypeScript interface with multiple properties:
#   interface State {
#       user_name: string;
#       messages: string[];
#       step_count: number;
#   }

class State(TypedDict):
    user_name: str         # A simple string
    messages: list         # A list of strings (like an array in JS)
    step_count: int        # A counter (like a number in JS)

print("State schema:")
print("  - user_name: str    (like a string)")
print("  - messages: list    (like an array)")
print("  - step_count: int   (like a number)")


# ========================================
# STEP 2: Define Nodes That Modify Different Fields
# ========================================
print("\n" + "=" * 50)
print("STEP 2: Defining three nodes")
print("=" * 50)

def greeter(state: State) -> dict:
    """Node 1: Sets the user name and adds a greeting message."""
    print("\n  📌 GREETER NODE")
    print(f"  State BEFORE: user_name='{state['user_name']}', "
          f"messages={state['messages']}, step_count={state['step_count']}")

    # CONCEPT: We return ONLY the fields we want to change.
    # LangGraph merges these into the existing state.
    # GOTCHA: For lists, returning a new list REPLACES the old one (we'll learn
    #         about reducers in 01_core_concepts/04_reducers.py to change this).
    updates = {
        "user_name": "LangGraph Learner",
        "messages": ["Hello! Welcome to the learning lab."],
        "step_count": 1,
    }

    print(f"  Returning updates: {updates}")
    return updates


def processor(state: State) -> dict:
    """Node 2: Reads the name and adds a personalized message."""
    print("\n  📌 PROCESSOR NODE")
    print(f"  State BEFORE: user_name='{state['user_name']}', "
          f"messages={state['messages']}, step_count={state['step_count']}")

    # CONCEPT: This node can see what the GREETER wrote.
    # The state flows forward — each node sees the accumulated changes.
    # EXPRESS PARALLEL: Like req.body being modified by previous middleware.
    name = state["user_name"]

    updates = {
        "messages": [f"Processing data for {name}..."],
        "step_count": state["step_count"] + 1,
    }

    print(f"  Returning updates: {updates}")
    return updates


def finalizer(state: State) -> dict:
    """Node 3: Adds a final summary message."""
    print("\n  📌 FINALIZER NODE")
    print(f"  State BEFORE: user_name='{state['user_name']}', "
          f"messages={state['messages']}, step_count={state['step_count']}")

    updates = {
        "messages": [f"All done! {state['user_name']} completed {state['step_count'] + 1} steps."],
        "step_count": state["step_count"] + 1,
    }

    print(f"  Returning updates: {updates}")
    return updates


print("Three nodes defined: greeter → processor → finalizer")


# ========================================
# STEP 3: Build and Run the Graph
# ========================================
print("\n" + "=" * 50)
print("STEP 3: Building and running the graph")
print("=" * 50)

graph = StateGraph(State)

# Add nodes
graph.add_node("greeter", greeter)
graph.add_node("processor", processor)
graph.add_node("finalizer", finalizer)

# Add edges: START → greeter → processor → finalizer → END
graph.add_edge(START, "greeter")
graph.add_edge("greeter", "processor")
graph.add_edge("processor", "finalizer")
graph.add_edge("finalizer", END)

app = graph.compile()

# Run with an initial state — all fields start empty/zero
initial_state = {
    "user_name": "",
    "messages": [],
    "step_count": 0,
}

print(f"\nInitial state: {initial_state}")
print("\n--- Running the graph ---")

final_state = app.invoke(initial_state)


# ========================================
# STEP 4: Inspect the Final State
# ========================================
print("\n" + "=" * 50)
print("STEP 4: Final state inspection")
print("=" * 50)

print(f"\n  user_name:  '{final_state['user_name']}'")
print(f"  messages:   {final_state['messages']}")
print(f"  step_count: {final_state['step_count']}")


# ========================================
# STEP 5: Key Observations
# ========================================
print("\n" + "=" * 50)
print("STEP 5: Key observations")
print("=" * 50)

print("""
👀 NOTICE these important things:

1. EACH NODE SEES THE LATEST STATE
   - greeter saw empty state
   - processor saw what greeter wrote
   - finalizer saw what processor wrote

2. RETURNING A LIST REPLACES IT
   - greeter set messages to ["Hello! Welcome..."]
   - processor REPLACED it with ["Processing data..."]
   - finalizer REPLACED it with ["All done!..."]
   - The final messages list only has the LAST message!

   ❓ What if you want to ACCUMULATE messages instead of replacing?
   → That's what REDUCERS do! See 01_core_concepts/04_reducers.py

3. NUMBERS WORK NATURALLY
   - step_count went from 0 → 1 → 2 → 3
   - Each node read the current value and added 1

4. STRINGS ARE OVERWRITTEN
   - user_name was set once by greeter and stayed the same
   - processor and finalizer didn't change it
""")


# ========================================
# WHAT YOU LEARNED
# ========================================
# 1. State can have multiple fields of different types (str, list, int)
# 2. Each node sees the LATEST state — changes accumulate as the graph runs
# 3. Returning a dict REPLACES those fields in the state (lists get overwritten!)
# 4. To accumulate list items instead of replacing, you need REDUCERS (next section)
#
# NEXT: 00_foundations/03_multiple_nodes.py — Build a 3-node data pipeline
# ========================================