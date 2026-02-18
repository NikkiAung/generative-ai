"""
Assignment: Zero-Shot Prompting
================================
Zero-shot prompting means giving the model instructions without any examples.
The model relies solely on its training to understand and respond.

Task:
Extract from customer feedback:
- sentiment (positive/negative/neutral)
- product
- issue_type
- urgency_level (low/medium/high)

Solve:
Write a single instruction (no examples) and test it on:
"I ordered the X200 router. It disconnects every 10 minutes. Fix ASAP."
Evaluate accuracy, JSON format correctness, hallucination, and consistency.

Key Concepts:
- Direct instructions without examples
- The model uses its training knowledge to infer format and intent
- Simplest approach but may be less consistent

Use Cases:
- When you need quick answers
- When the task is straightforward
- When you don't have examples to provide
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Validate API key is present
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set. Add it to environment or .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# ZERO-SHOT PROMPT: Instructions only, no examples
# The model must figure out the output purely from the description
SYSTEM_PROMPT = """
You are a customer feedback analyzer. Extract structured data from customer feedback.

Output strictly in JSON format with these fields:
- sentiment: "positive", "negative", or "neutral"
- product: the product name mentioned
- issue_type: short description of the problem category
- urgency_level: "low", "medium", or "high"
"""

# Customer feedback to analyze
USER_PROMPT = "I ordered the X200 router. It disconnects every 10 minutes. Fix ASAP."

# Make the API call
response = client.chat.completions.create(
    model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ]
)

# Display the response
print(response.choices[0].message.content)
