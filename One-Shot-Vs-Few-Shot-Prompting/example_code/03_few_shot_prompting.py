"""
03. Few-Shot Prompting
======================
Few-shot prompting means providing examples to guide the model's responses.
The model learns the pattern from your examples and applies it to new inputs.

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

# Initialize OpenAI client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# FEW-SHOT PROMPT: Instructions with examples
# The examples show the model exactly what format we want
SYSTEM_PROMPT = """
You will answer only coding questions. If the user asks something else, do not answer it.

Rules:
- Strictly follow the output in JSON format

Output Format:
{
    "code": "string" or null,
    "isCodingQuestion": boolean   
}

Examples:
Q: Can you explain the (a+b) whole square formula?
A: { "code": null, "isCodingQuestion": false }

Q: Write a code in Python for adding two numbers
A: { "code": "def add(a, b):\\n    return a + b", "isCodingQuestion": true }

Q: What is the capital of France?
A: { "code": null, "isCodingQuestion": false }
"""

# User's question
USER_PROMPT = "Write a Python function to multiply two numbers"

# Make the API call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ]
)

# Display the response
print(response.choices[0].message.content)
