"""
04. Chain-of-Thought (CoT) Prompting
====================================
Chain-of-Thought prompting encourages the model to break down complex problems
into step-by-step reasoning before providing the final answer.

Key Concepts:
- Model shows its reasoning process
- Breaks complex tasks into smaller steps
- Improves accuracy on complex problems
- Uses intermediate steps (PLAN) before final output

Use Cases:
- Math problems requiring multiple steps
- Complex reasoning tasks
- When you need to verify the logic
- Debugging and problem-solving
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# CHAIN-OF-THOUGHT PROMPT: Encourages step-by-step reasoning
SYSTEM_PROMPT = """
You're an expert AI Assistant that solves problems using chain-of-thought reasoning.
You work in three phases: START, PLAN, and OUTPUT.

Process:
1. START: Receive the user's input
2. PLAN: Break down the problem into steps (can be multiple PLAN steps)
3. OUTPUT: Provide the final answer

Rules:
- Strictly follow the JSON output format
- Only run one step at a time
- Show your reasoning in PLAN steps
- Give final answer in OUTPUT step

Output JSON Format:
{ "step": "START" | "PLAN" | "OUTPUT", "content": "string" }

Example:
User: Solve 2 + 3 * 5 / 10

START: { "step": "START", "content": "User wants to solve: 2 + 3 * 5 / 10" }
PLAN: { "step": "PLAN", "content": "This is a math problem requiring order of operations (BODMAS/PEMDAS)" }
PLAN: { "step": "PLAN", "content": "First, multiply: 3 * 5 = 15" }
PLAN: { "step": "PLAN", "content": "Now the equation is: 2 + 15 / 10" }
PLAN: { "step": "PLAN", "content": "Next, divide: 15 / 10 = 1.5" }
PLAN: { "step": "PLAN", "content": "Now the equation is: 2 + 1.5" }
PLAN: { "step": "PLAN", "content": "Finally, add: 2 + 1.5 = 3.5" }
OUTPUT: { "step": "OUTPUT", "content": "3.5" }
"""

# User's question
USER_PROMPT = "Write a JavaScript function to print the first n numbers"

# Make the API call with conversation history showing the reasoning process
response = client.chat.completions.create(
    response_format={"type": "json_object"},  # Enforce JSON output
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT},
        
        # Assistant's reasoning steps (simulating the chain-of-thought process)
        {
            "role": "assistant",
            "content": json.dumps({
                "step": "START",
                "content": "User wants a JavaScript function to print the first n numbers"
            })
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "step": "PLAN",
                "content": "I need to create a function that takes 'n' as a parameter and prints numbers from 1 to n"
            })
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "step": "PLAN",
                "content": "I should use a for loop to iterate from 1 to n and use console.log to print each number"
            })
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "step": "PLAN",
                "content": "I should also handle edge cases like negative numbers or non-numeric input"
            })
        }
    ]
)

# Display the response
print(response.choices[0].message.content)