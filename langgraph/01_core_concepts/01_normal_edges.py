"""
Normal Edges — 01_core_concepts/01_normal_edges.py

WHAT THIS TEACHES:
    Fixed edges that always go from one node to the next — the simplest routing.
    This is a review + deeper look at what you learned in foundations.

WHAT YOU WILL SEE:
    A 4-node pipeline: intake → validate → process → output.
    Every transition is fixed — no branching, no conditions.

EXPRESS.JS PARALLEL:
    Normal edges are like a fixed middleware chain:
        app.use(intake);
        app.use(validate);
        app.use(process);
        app.use(output);
    Every request goes through ALL middleware in order.

PREREQUISITES:
    Complete section 00_foundations first.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    order_id: str
    item: str
    quantity: int
    validated: bool
    total_price: float
    receipt: str


# ========================================
# NODE FUNCTIONS — An Order Processing Pipeline
# ========================================
# EXPRESS PARALLEL: Think of this as processing an e-commerce order.
# Each middleware does one step of order fulfillment.

def intake(state: State) -> dict:
    """Receive the order."""
    print("\n  📦 INTAKE: Received new order")
    print(f"     Order #{state['order_id']}: {state['quantity']}x {state['item']}")
    return {}  # No changes needed — just print

def validate(state: State) -> dict:
    """Validate the order."""
    print("\n  ✅ VALIDATE: Checking order")
    is_valid = state["quantity"] > 0 and state["item"] != ""
    print(f"     Valid: {is_valid}")
    return {"validated": is_valid}

def process(state: State) -> dict:
    """Calculate the price."""
    print("\n  💰 PROCESS: Calculating price")
    # CONCEPT: price lookup — simple dict instead of a database
    prices = {"widget": 9.99, "gadget": 24.99, "doohickey": 14.99}
    price = prices.get(state["item"], 5.00)
    total = price * state["quantity"]
    print(f"     {state['quantity']} x ${price:.2f} = ${total:.2f}")
    return {"total_price": total}

def output(state: State) -> dict:
    """Generate receipt."""
    print("\n  🧾 OUTPUT: Generating receipt")
    receipt = (
        f"--- RECEIPT ---\n"
        f"Order: {state['order_id']}\n"
        f"Item:  {state['item']} x{state['quantity']}\n"
        f"Total: ${state['total_price']:.2f}\n"
        f"Valid: {state['validated']}\n"
        f"--------------"
    )
    print(f"     {receipt}")
    return {"receipt": receipt}


# ========================================
# BUILD THE GRAPH
# ========================================
print("\n" + "=" * 50)
print("ORDER PROCESSING PIPELINE (Normal Edges)")
print("=" * 50)
print("Flow: START → intake → validate → process → output → END")

graph = StateGraph(State)

graph.add_node("intake", intake)
graph.add_node("validate", validate)
graph.add_node("process", process)
graph.add_node("output", output)

# CONCEPT: Normal edges — every order follows the EXACT same path.
# There's no branching, no skipping. This is why they're called "normal" edges.
graph.add_edge(START, "intake")
graph.add_edge("intake", "validate")
graph.add_edge("validate", "process")
graph.add_edge("process", "output")
graph.add_edge("output", END)

app = graph.compile()


# ========================================
# RUN: Order 1
# ========================================
print("\n" + "=" * 50)
print("ORDER 1")
print("=" * 50)

result1 = app.invoke({
    "order_id": "ORD-001",
    "item": "widget",
    "quantity": 3,
    "validated": False,
    "total_price": 0.0,
    "receipt": "",
})


# ========================================
# RUN: Order 2
# ========================================
print("\n" + "=" * 50)
print("ORDER 2")
print("=" * 50)

result2 = app.invoke({
    "order_id": "ORD-002",
    "item": "gadget",
    "quantity": 1,
    "validated": False,
    "total_price": 0.0,
    "receipt": "",
})

print("\n" + "=" * 50)
print("KEY INSIGHT")
print("=" * 50)
print("""
Both orders went through the EXACT same 4 nodes in the EXACT same order.
Normal edges = fixed routing. No decisions. No branches.

But what if Order 2 is invalid and should be REJECTED instead of processed?
That requires a CONDITIONAL EDGE — see the next file!
""")


# ========================================
# WHAT YOU LEARNED
# ========================================
# 1. Normal edges (add_edge) create FIXED, unconditional paths
# 2. Every invocation follows the same path — no runtime decisions
# 3. Good for pipelines where every item needs the same processing
# 4. Not good when you need branching — that's conditional edges
#
# NEXT: 01_core_concepts/02_conditional_edges.py — Branching based on state
# ========================================