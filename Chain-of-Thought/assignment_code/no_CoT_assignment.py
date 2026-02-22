"""
Chain-of-Thought Assignment — Part 3
======================================
Modified SYSTEM_PROMPT: START and PLAN steps removed.
The model returns ONLY the final answer in JSON format:
  { "answer": "..." }

Same three questions are asked so results are directly comparable
to the CoT version in CoT_assignment.py.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Part 3: No chain-of-thought — answer only
SYSTEM_PROMPT = """
You are a helpful AI assistant.
Answer the user's question directly and concisely.
Return your response in the following JSON format only:
{ "answer": "..." }
Do NOT include any reasoning, steps, or explanation — just the final answer.
"""

QUESTIONS = [
    "A shopkeeper sells notebooks at $3 each. If someone buys 8 notebooks and pays $30, how much change should they get?",
    "A rectangle has length 12 and width 5. What is its area?",
    "Write a Python function to check if a number is even or odd.",
]


def run_no_cot(question: str) -> dict:
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
    print("\n" + "=" * 65)
    print(f"QUESTION: {question}")
    print("=" * 65)
    print(f"\n✅ ANSWER: {result.get('answer', '[no answer]')}")
    print("=" * 65)


if __name__ == "__main__":
    print("\n" + "#" * 65)
    print("  CHAIN-OF-THOUGHT ASSIGNMENT — Part 3 (No CoT / Answer Only)")
    print("#" * 65)

    for q in QUESTIONS:
        result = run_no_cot(q)
        display_result(q, result)
