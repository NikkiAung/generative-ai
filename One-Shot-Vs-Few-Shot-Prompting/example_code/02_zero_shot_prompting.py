"""
02. Zero-Shot Prompting
=======================
Zero-shot prompting means giving the model instructions without any examples.
The model relies solely on its training to understand and respond.

Key Concepts:
- Direct instructions without examples
- System prompts to define behavior
- Clear, specific instructions work best

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

# ZERO-SHOT PROMPT: Direct instructions without examples
# The model must understand the task from the description alone
SYSTEM_PROMPT = """You will answer coding questions only. 
If the user asks anything else, reply 'Sorry, I can only help with coding questions.' and do not answer."""

# User's question
USER_PROMPT = "int a = 10, int b = 20, int c = a + b;"

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
