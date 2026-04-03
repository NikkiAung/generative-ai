"""
Hello Graph — 00_foundations/01_hello_graph.py

WHAT THIS TEACHES:
    The absolute simplest LangGraph program possible — two nodes connected by one edge.

WHAT YOU WILL SEE:
    Two print messages in order, showing that Node A runs before Node B.
    This proves the graph executes nodes in the order defined by edges.

EXPRESS.JS PARALLEL:
    This is like having two middleware functions:
        app.use(middlewareA)  →  app.use(middlewareB)
    Where middlewareA runs first, then middlewareB, and they share the req object.

PREREQUISITES:
    Read 00_foundations/CONCEPT.md first.
"""

# ========================================
# SETUP
# ========================================

# CONCEPT: LangGraph uses TypedDict to define the "shape" of your state.
# This is like defining an interface/type in TypeScript:
#     interface State { message: string }
from typing import TypedDict

# CONCEPT: StateGraph is the main class — it builds graphs that pass state between nodes.
# Think of it as Express() — it's the app factory.
from langgraph.graph import StateGraph, START, END


# ========================================
# STEP 1: Define the State
# ========================================
print("\n" + "=" * 50)
print("STEP 1: Defining the state schema")
print("=" * 50)

# CONCEPT: State is a TypedDict — a dictionary with defined keys and types.
# EXPRESS PARALLEL: This is like the `req` object in Express.
#   In Express, req has req.body, req.params, etc.
#   In LangGraph, State has whatever fields you define.

class State(TypedDict):
    message: str  # Just one field to keep it dead simple

print("State schema defined: { message: str }")
print("This is like defining: interface State { message: string } in TypeScript")


# ========================================
# STEP 2: Define the Node Functions
# ========================================
print("\n" + "=" * 50)
print("STEP 2: Defining node functions")
print("=" * 50)

# CONCEPT: A node is just a Python function that:
#   1. Takes the current state as input
#   2. Does some work
#   3. Returns a dictionary of state updates
#
# EXPRESS PARALLEL: A node is like a middleware function:
#   function myMiddleware(req, res, next) {
#       req.body.processed = true;  // modify shared state
#       next();                     // pass to next middleware
#   }
#
# In LangGraph, instead of calling next(), the EDGES define what runs next.

def node_a(state: State) -> dict:
    """First node — sets the message."""
    print("  → Node A is running!")
    print(f"  → Node A received state: {state}")

    # WHY: We return a dict with only the fields we want to update.
    # LangGraph merges this into the existing state automatically.
    return {"message": "Hello from Node A!"}


def node_b(state: State) -> dict:
    """Second node — reads and updates the message."""
    print(f"  → Node B is running!")
    print(f"  → Node B received state: {state}")

    # CONCEPT: Node B can see what Node A wrote to the state.
    # The state flows through the graph like req flows through middleware.
    return {"message": state["message"] + " And hello from Node B!"}


print("Two node functions defined: node_a, node_b")


# ========================================
# STEP 3: Build the Graph
# ========================================
print("\n" + "=" * 50)
print("STEP 3: Building the graph")
print("=" * 50)

# CONCEPT: StateGraph is the builder. You:
#   1. Create it with your State type
#   2. Add nodes (functions)
#   3. Add edges (connections between nodes)
#   4. Compile it into a runnable app
#
# EXPRESS PARALLEL:
#   const app = express();          →  graph = StateGraph(State)
#   app.use(middlewareA);           →  graph.add_node("a", node_a)
#   app.use(middlewareB);           →  graph.add_node("b", node_b)
#   // order = order of app.use()  →  graph.add_edge(START, "a")
#                                      graph.add_edge("a", "b")
#                                      graph.add_edge("b", END)

graph = StateGraph(State)

# Add nodes — give each a name and a function
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)

# Add edges — define the execution order
# START → node_a → node_b → END
graph.add_edge(START, "node_a")   # When the graph starts, run node_a first
graph.add_edge("node_a", "node_b")  # After node_a, run node_b
graph.add_edge("node_b", END)     # After node_b, the graph is done

print("Graph structure: START → node_a → node_b → END")

# CONCEPT: compile() validates the graph and creates a runnable.
# If you forgot an edge or created a dead end, compile() will catch it.
app = graph.compile()

print("Graph compiled successfully! ✅")


# ========================================
# STEP 4: Run the Graph
# ========================================
print("\n" + "=" * 50)
print("STEP 4: Running the graph")
print("=" * 50)

# CONCEPT: invoke() starts the graph with an initial state.
# It runs all nodes in order, following the edges, and returns the final state.
#
# EXPRESS PARALLEL: This is like sending a request to your Express app:
#   fetch('/api/endpoint', { body: { message: '' } })
#   The request flows through all middleware and comes back with a response.

initial_state = {"message": ""}
print(f"Initial state: {initial_state}\n")

# Run it!
final_state = app.invoke(initial_state)

print(f"\nFinal state: {final_state}")


# ========================================
# STEP 5: Understanding the Output
# ========================================
print("\n" + "=" * 50)
print("STEP 5: What just happened?")
print("=" * 50)

print("""
Here's what happened step by step:

1. We created a State with one field: message (string)
2. We defined two functions (nodes): node_a and node_b
3. We connected them: START → node_a → node_b → END
4. We ran the graph with an empty message
5. node_a set the message to "Hello from Node A!"
6. node_b received that message and appended " And hello from Node B!"
7. The graph returned the final state with the complete message

This is the simplest possible LangGraph program.
Everything else builds on top of this pattern.
""")


# ========================================
# WHAT YOU LEARNED
# ========================================
# 1. A LangGraph graph has NODES (functions) and EDGES (connections)
# 2. State is a TypedDict that flows through the graph like req in Express
# 3. Nodes receive state, do work, and return updates (not the full state)
# 4. The flow is: StateGraph() → add_node() → add_edge() → compile() → invoke()
#
# NEXT: 00_foundations/02_state_basics.py — See state changing as it flows through nodes
# ========================================