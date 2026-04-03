"""
Conditional Edges — 01_core_concepts/02_conditional_edges.py

WHAT THIS TEACHES:
    How to make the graph take DIFFERENT paths based on the state.
    A router function reads the state and returns which node to run next.

WHAT YOU WILL SEE:
    Two orders processed differently:
    - Order with quantity > 0 → approved → processed
    - Order with quantity <= 0 → rejected → skipped processing

EXPRESS.JS PARALLEL:
    This is like route-based middleware:
        if (req.body.type === 'premium') premiumHandler(req, res);
        else standardHandler(req, res);
    The key difference: in Express you write if/else inline.
    In LangGraph, the branching logic is separated into a ROUTER FUNCTION.

PREREQUISITES:
    Run 01_core_concepts/01_normal_edges.py first.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    order_id: str
    item: str
    quantity: int
    status: str
    total_price: float
    message: str


# ========================================
# NODE FUNCTIONS
# ========================================

def intake(state: State) -> dict:
    """Receive and log the order."""
    print(f"\n  📦 INTAKE: Order #{state['order_id']} — {state['quantity']}x {state['item']}")
    return {"status": "received"}

def approve(state: State) -> dict:
    """Approved path — calculate price."""
    print(f"  ✅ APPROVED: Order #{state['order_id']}")
    prices = {"widget": 9.99, "gadget": 24.99, "doohickey": 14.99}
    price = prices.get(state["item"], 5.00)
    total = price * state["quantity"]
    return {"status": "approved", "total_price": total, "message": f"Total: ${total:.2f}"}

def reject(state: State) -> dict:
    """Rejected path — mark as failed."""
    print(f"  ❌ REJECTED: Order #{state['order_id']} — invalid quantity")
    return {"status": "rejected", "total_price": 0.0, "message": "Order rejected: invalid quantity"}

def complete(state: State) -> dict:
    """Final node — both paths merge here."""
    print(f"  🏁 COMPLETE: Order #{state['order_id']} — Status: {state['status']}")
    print(f"     Message: {state['message']}")
    return {}


# ========================================
# THE ROUTER FUNCTION
# ========================================
# CONCEPT: A router function is a PURE function that:
#   1. Reads the current state
#   2. Returns a STRING that maps to the next node
#   It does NOT modify state — it only decides the direction.
#
# EXPRESS PARALLEL: This is like a routing middleware that calls next()
#   differently based on the request:
#     function routeOrder(req, res, next) {
#         if (req.body.quantity > 0) return next('approved');
#         else return next('rejected');
#     }

def route_order(state: State) -> str:
    """Decide whether to approve or reject the order."""
    print(f"\n  🔀 ROUTER: Checking quantity = {state['quantity']}")
    if state["quantity"] > 0:
        print("  🔀 ROUTER: → Taking APPROVE path")
        return "approve"
    else:
        print("  🔀 ROUTER: → Taking REJECT path")
        return "reject"


# ========================================
# BUILD THE GRAPH WITH CONDITIONAL EDGES
# ========================================
print("\n" + "=" * 50)
print("ORDER PROCESSING WITH BRANCHING")
print("=" * 50)

graph = StateGraph(State)

# Add all nodes
graph.add_node("intake", intake)
graph.add_node("approve", approve)
graph.add_node("reject", reject)
graph.add_node("complete", complete)

# START → intake (always)
graph.add_edge(START, "intake")

# CONCEPT: add_conditional_edges() is the key!
# After "intake" runs:
#   1. Call route_order(state)
#   2. If it returns "approve" → run the "approve" node
#   3. If it returns "reject" → run the "reject" node
#
# GOTCHA: The strings returned by the router ("approve", "reject")
#   MUST match the keys in the routing map below.
graph.add_conditional_edges(
    "intake",           # After this node runs...
    route_order,        # Call this function to decide...
    {                   # Map return values to node names:
        "approve": "approve",   # "approve" → go to approve node
        "reject": "reject",     # "reject" → go to reject node
    }
)

# Both paths merge back into "complete"
graph.add_edge("approve", "complete")
graph.add_edge("reject", "complete")
graph.add_edge("complete", END)

app = graph.compile()

print("""
Graph structure:
  START → intake → ROUTER
                  ├── "approve" → approve → complete → END
                  └── "reject"  → reject  → complete → END
""")


# ========================================
# RUN: Valid Order (takes APPROVE path)
# ========================================
print("=" * 50)
print("TEST 1: Valid order (quantity = 3)")
print("=" * 50)

result1 = app.invoke({
    "order_id": "ORD-101",
    "item": "widget",
    "quantity": 3,
    "status": "",
    "total_price": 0.0,
    "message": "",
})


# ========================================
# RUN: Invalid Order (takes REJECT path)
# ========================================
print("\n" + "=" * 50)
print("TEST 2: Invalid order (quantity = 0)")
print("=" * 50)

result2 = app.invoke({
    "order_id": "ORD-102",
    "item": "gadget",
    "quantity": 0,
    "status": "",
    "total_price": 0.0,
    "message": "",
})


# ========================================
# RUN: Another valid order (takes APPROVE path)
# ========================================
print("\n" + "=" * 50)
print("TEST 3: Another valid order (quantity = 5)")
print("=" * 50)

result3 = app.invoke({
    "order_id": "ORD-103",
    "item": "doohickey",
    "quantity": 5,
    "status": "",
    "total_price": 0.0,
    "message": "",
})


# ========================================
# SUMMARY
# ========================================
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
print(f"""
Three orders, two different paths:

  ORD-101 (qty=3): intake → APPROVE → complete ✅  Total: ${result1['total_price']:.2f}
  ORD-102 (qty=0): intake → REJECT  → complete ❌  Total: ${result2['total_price']:.2f}
  ORD-103 (qty=5): intake → APPROVE → complete ✅  Total: ${result3['total_price']:.2f}

The SAME graph handled all three — but took DIFFERENT paths
based on the quantity. That's the power of conditional edges!
""")

# TRY THIS: Add a third path for "premium" orders (quantity > 10) that
# applies a 20% discount. You'll need a new node and a new router return value.


# ========================================
# WHAT YOU LEARNED
# ========================================
# 1. Conditional edges use a ROUTER FUNCTION to decide the next node
# 2. The router reads state and returns a STRING (not a node reference)
# 3. The routing map connects those strings to actual node names
# 4. Both paths can merge back into a single node (convergence)
#
# NEXT: 01_core_concepts/03_loops.py — The most important file: LOOPING!
# ========================================