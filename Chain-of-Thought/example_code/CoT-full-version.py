"""
04. Chain-of-Thought (CoT) Prompting - FULL VERSION
====================================================
This version shows the AI generating ALL steps (START, PLAN, OUTPUT) in real-time.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# SYSTEM PROMPT
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
    {"step": "PLAN", "content": "..."},
    {"step": "PLAN", "content": "..."},
    {"step": "OUTPUT", "content": "..."}
  ]
}

Example:
User: Solve 2 + 3 * 5 / 10

Response:
{
  "steps": [
    {"step": "START", "content": "User wants to solve: 2 + 3 * 5 / 10"},
    {"step": "PLAN", "content": "This requires order of operations (BODMAS/PEMDAS)"},
    {"step": "PLAN", "content": "First, multiply: 3 * 5 = 15"},
    {"step": "PLAN", "content": "Now: 2 + 15 / 10"},
    {"step": "PLAN", "content": "Next, divide: 15 / 10 = 1.5"},
    {"step": "PLAN", "content": "Finally, add: 2 + 1.5 = 3.5"},
    {"step": "OUTPUT", "content": "3.5"}
  ]
}
"""

# User's question
USER_PROMPT = "Write a JavaScript function to print the first n numbers"

# Make the API call
response = client.chat.completions.create(
    response_format={"type": "json_object"},
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ]
)

# Parse and display the response
result = json.loads(response.choices[0].message.content)

print("\n" + "="*60)
print("CHAIN-OF-THOUGHT REASONING PROCESS")
print("="*60 + "\n")

for item in result.get("steps", []):
    step_type = item["step"]
    content = item["content"]
    
    # Color coding for different steps
    if step_type == "START":
        print(f"🎯 {step_type}: {content}\n")
    elif step_type == "PLAN":
        print(f"💡 {step_type}: {content}\n")
    elif step_type == "OUTPUT":
        print(f"✅ {step_type}:\n{content}\n")

print("="*60)