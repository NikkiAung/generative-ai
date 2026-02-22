Chain-of-Thought (Structured JSON) Assignment
Objective
Understand how structured Chain-of-Thought reasoning works using START → PLAN → OUTPUT
format.
Part 1 — Run the Code
• A shopkeeper sells notebooks at $3 each. If someone buys 8 notebooks and pays $30, how
much change should they get?
• A rectangle has length 12 and width 5. What is its area?
• Write a Python function to check if a number is even or odd.
Part 2 — Observe the Output
• How many PLAN steps were generated?
• Was the reasoning clear?
• Was the final answer correct?
• Did the model over-explain anything?
Part 3 — Remove Chain-of-Thought
Modify the SYSTEM_PROMPT to remove START and PLAN. Ask the model to return only the final
answer in JSON format:
{ "answer": "..." }
Part 4 — Compare
• Which version was clearer?
• Which version was shorter?
• Did showing reasoning improve trust?
• When would exposing reasoning be unnecessary?
