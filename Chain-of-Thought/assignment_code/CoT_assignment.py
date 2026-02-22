"""
Chain-of-Thought Assignment — Part 1 & 2
=========================================
Runs three questions through the START → PLAN → OUTPUT reasoning pipeline
and displays the full chain-of-thought for each.

Questions:
  Q1. Shopkeeper change problem
  Q2. Rectangle area
  Q3. Python even/odd function
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You're an expert AI Assistant that solves problems using chain-of-thought reasoning.
You work in three phases: START, PLAN, and OUTPUT.

Process:
1. START: Receive and understand the user's input
2. PLAN: Break down the problem into steps (show multiple PLAN steps)
3. OUTPUT: Provide the final answer

Rules:
- Strictly follow the JSON output format
- Show ALL your reasoning steps
- Each response should contain ALL steps from START to OUTPUT

Output JSON Format:
{
  "steps": [
    {"step": "START", "content": "..."},
    {"step": "PLAN",  "content": "..."},
    {"step": "PLAN",  "content": "..."},
    {"step": "OUTPUT","content": "..."}
  ]
}

Example:
User: Solve 2 + 3 * 5 / 10

Response:
{
  "steps": [
    {"step": "START",  "content": "User wants to solve: 2 + 3 * 5 / 10"},
    {"step": "PLAN",   "content": "Apply order of operations (BODMAS/PEMDAS)"},
    {"step": "PLAN",   "content": "Multiply first: 3 * 5 = 15"},
    {"step": "PLAN",   "content": "Divide next: 15 / 10 = 1.5"},
    {"step": "PLAN",   "content": "Add finally: 2 + 1.5 = 3.5"},
    {"step": "OUTPUT", "content": "3.5"}
  ]
}
"""

QUESTIONS = [
    "A shopkeeper sells notebooks at $3 each. If someone buys 8 notebooks and pays $30, how much change should they get?",
    "A rectangle has length 12 and width 5. What is its area?",
    "Write a Python function to check if a number is even or odd.",
]


def run_cot(question: str) -> dict:
    response = client.chat.completions.create(
        response_format={"type": "json_object"},
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": question},
        ],
    )
    return json.loads(response.choices[0].message.content)


def display_result(question: str, result: dict) -> None:
    steps = result.get("steps", [])
    plan_count = sum(1 for s in steps if s["step"] == "PLAN")

    print("\n" + "=" * 65)
    print(f"QUESTION: {question}")
    print("=" * 65)

    for item in steps:
        step_type = item["step"]
        content   = item["content"]
        if step_type == "START":
            print(f"\n🎯 START : {content}")
        elif step_type == "PLAN":
            print(f"💡 PLAN  : {content}")
        elif step_type == "OUTPUT":
            print(f"\n✅ OUTPUT:\n{content}")

    print(f"\n   [PLAN steps generated: {plan_count}]")
    print("=" * 65)


if __name__ == "__main__":
    print("\n" + "#" * 65)
    print("  CHAIN-OF-THOUGHT ASSIGNMENT — Part 1 (CoT Full Version)")
    print("#" * 65)

    for q in QUESTIONS:
        result = run_cot(q)
        display_result(q, result)
