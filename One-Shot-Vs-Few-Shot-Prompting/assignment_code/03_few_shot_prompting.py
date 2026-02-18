"""
Assignment: Few-Shot Prompting
======================
Few-shot prompting means providing examples to guide the model's responses.
The model learns the pattern from your examples and applies it to new inputs.

Task:
Extract from customer feedback:
- sentiment (positive/negative/neutral)
- product
- issue_type
- urgency_level (low/medium/high)

Solve:
Provide 3 examples and test it on:
"I ordered the X200 router. It disconnects every 10 minutes. Fix ASAP."
Evaluate accuracy, JSON format correctness, hallucination, and consistency.

Key Concepts:
- Provide 2-5 examples of input-output pairs
- Examples teach the model the desired format and style
- More effective for specific formats (like JSON)

Use Cases:
- When you need consistent output format
- When the task requires specific style
- When zero-shot results are inconsistent
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

# FEW-SHOT PROMPT: Instructions with multiple examples
# Multiple examples help the model handle varied sentiments and urgency levels
SYSTEM_PROMPT = """
You are a customer feedback analyzer. Extract structured data from customer feedback.

Output strictly in JSON format with these fields:
- sentiment: "positive", "negative", or "neutral"
- product: the product name mentioned
- issue_type: short description of the problem category
- urgency_level: "low", "medium", or "high"

Examples:
Feedback: "My Z100 laptop won't turn on after the update. Please help me urgently."
Output: { "sentiment": "negative", "product": "Z100 laptop", "issue_type": "device not powering on", "urgency_level": "high" }

Feedback: "The A5 headphones sound amazing! Best purchase I've made this year."
Output: { "sentiment": "positive", "product": "A5 headphones", "issue_type": "none", "urgency_level": "low" }

Feedback: "My B3 keyboard sometimes skips letters. Not a big deal but would like it fixed."
Output: { "sentiment": "neutral", "product": "B3 keyboard", "issue_type": "intermittent key input failure", "urgency_level": "medium" }
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
