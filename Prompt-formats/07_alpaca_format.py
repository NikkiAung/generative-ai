"""
07. Alpaca Prompt Format
========================
Demonstrates the Alpaca prompt format used by Stanford's Alpaca model
and other instruction-tuned models.

Key Concepts:
- Alpaca format structure (Instruction, Input, Response)
- When to use Alpaca format
- Formatting prompts for instruction-following models
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def create_alpaca_prompt(instruction: str, input_text: str = "") -> str:
    """
    Create a prompt in Alpaca format.
    
    Args:
        instruction: The task instruction
        input_text: Optional input context for the task
    
    Returns:
        Formatted Alpaca prompt
    """
    prompt = "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n"
    prompt += f"### Instruction:\n{instruction}\n\n"
    
    if input_text:
        prompt += f"### Input:\n{input_text}\n\n"
    
    prompt += "### Response:\n"
    
    return prompt


# Example 1: Simple instruction without input
print("=" * 60)
print("Example 1: Simple Instruction (No Input)")
print("=" * 60)

instruction1 = "Write a haiku about artificial intelligence."
alpaca_prompt1 = create_alpaca_prompt(instruction1)

print(f"\n📝 Alpaca Prompt:\n{alpaca_prompt1}")

response1 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": alpaca_prompt1}
    ],
    temperature=0.7
)

print(f"\n🤖 Response:\n{response1.choices[0].message.content}\n")


# Example 2: Instruction with input context
print("=" * 60)
print("Example 2: Instruction with Input Context")
print("=" * 60)

instruction2 = "Summarize the following text in one sentence."
input_text2 = """
Artificial intelligence is rapidly transforming industries worldwide. 
From healthcare diagnostics to financial fraud detection, AI systems 
are becoming increasingly sophisticated. Machine learning algorithms 
can now process vast amounts of data and identify patterns that humans 
might miss. However, ethical considerations around AI deployment remain 
a critical concern for researchers and policymakers.
"""

alpaca_prompt2 = create_alpaca_prompt(instruction2, input_text2)

print(f"\n📝 Alpaca Prompt:\n{alpaca_prompt2}")

response2 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": alpaca_prompt2}
    ],
    temperature=0.3
)

print(f"\n🤖 Response:\n{response2.choices[0].message.content}\n")


# Example 3: Data extraction task
print("=" * 60)
print("Example 3: Data Extraction Task")
print("=" * 60)

instruction3 = "Extract the person's name, age, and occupation from the text."
input_text3 = "My name is Sarah Johnson, I'm 32 years old, and I work as a software engineer at Tech Corp."

alpaca_prompt3 = create_alpaca_prompt(instruction3, input_text3)

print(f"\n📝 Alpaca Prompt:\n{alpaca_prompt3}")

response3 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": alpaca_prompt3}
    ],
    temperature=0.1
)

print(f"\n🤖 Response:\n{response3.choices[0].message.content}\n")


# Example 4: Code generation
print("=" * 60)
print("Example 4: Code Generation")
print("=" * 60)

instruction4 = "Write a Python function that calculates the factorial of a number using recursion."

alpaca_prompt4 = create_alpaca_prompt(instruction4)

print(f"\n📝 Alpaca Prompt:\n{alpaca_prompt4}")

response4 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": alpaca_prompt4}
    ],
    temperature=0.2
)

print(f"\n🤖 Response:\n{response4.choices[0].message.content}\n")


# Best Practices
print("=" * 60)
print("📚 Alpaca Format Best Practices")
print("=" * 60)
print("""
1. ✅ Clear Instructions: Be specific about what you want
2. ✅ Separate Input: Use the Input field for context/data
3. ✅ Consistent Format: Always follow the template structure
4. ✅ Single Task: One instruction per prompt
5. ✅ Examples: Provide examples in the instruction if needed

When to Use Alpaca Format:
- Instruction-following models (Alpaca, Vicuna, etc.)
- Single-turn tasks
- Clear input/output scenarios
- Fine-tuning datasets
""")
