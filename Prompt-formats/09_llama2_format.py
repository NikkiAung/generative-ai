"""
09. LLaMA-2 Prompt Format
==========================
Demonstrates the LLaMA-2 prompt format used by Meta's LLaMA-2 models.
This format is specifically designed for LLaMA-2-Chat models.

Key Concepts:
- LLaMA-2 special tokens (<s>, [INST], <<SYS>>, etc.)
- Single-turn and multi-turn formatting
- System message integration
- Proper token placement
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def create_llama2_prompt(system_msg: str, user_msg: str, history: list = None) -> str:
    """
    Create a prompt in LLaMA-2 format.
    
    Format for single-turn:
    <s>[INST] <<SYS>>
    {system_message}
    <</SYS>>
    
    {user_message} [/INST]
    
    Format for multi-turn:
    <s>[INST] <<SYS>>
    {system_message}
    <</SYS>>
    
    {user_msg_1} [/INST] {assistant_response_1} </s><s>[INST] {user_msg_2} [/INST]
    
    Args:
        system_msg: System instruction
        user_msg: User message
        history: Optional conversation history [(user, assistant), ...]
    
    Returns:
        LLaMA-2 formatted prompt
    """
    if history:
        # Multi-turn conversation
        prompt = f"<s>[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n\n"
        
        # Add conversation history
        for i, (user, assistant) in enumerate(history):
            if i == 0:
                prompt += f"{user} [/INST] {assistant} </s>"
            else:
                prompt += f"<s>[INST] {user} [/INST] {assistant} </s>"
        
        # Add current user message
        prompt += f"<s>[INST] {user_msg} [/INST]"
    else:
        # Single-turn
        prompt = f"<s>[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n\n{user_msg} [/INST]"
    
    return prompt


# Example 1: Single-turn conversation
print("=" * 60)
print("Example 1: Single-Turn LLaMA-2 Format")
print("=" * 60)

system_msg1 = "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible."
user_msg1 = "What is the capital of France?"

llama2_prompt1 = create_llama2_prompt(system_msg1, user_msg1)

print(f"\n📝 LLaMA-2 Formatted Prompt:\n{llama2_prompt1}\n")

# Simulate using OpenAI (in practice, you'd use this with actual LLaMA-2 models)
response1 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": f"Respond as if you received this LLaMA-2 formatted prompt:\n\n{llama2_prompt1}"}
    ],
    temperature=0.7
)

print(f"🤖 Response:\n{response1.choices[0].message.content}\n")


# Example 2: Multi-turn conversation
print("=" * 60)
print("Example 2: Multi-Turn LLaMA-2 Format")
print("=" * 60)

system_msg2 = "You are a helpful coding assistant."
conversation_history = [
    ("How do I create a list in Python?", "You can create a list using square brackets: my_list = [1, 2, 3]"),
    ("How do I add an item?", "Use the append() method: my_list.append(4)")
]
user_msg2 = "Can I add multiple items at once?"

llama2_prompt2 = create_llama2_prompt(system_msg2, user_msg2, conversation_history)

print(f"\n📝 LLaMA-2 Multi-Turn Prompt:\n{llama2_prompt2}\n")

response2 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": f"Respond as if you received this LLaMA-2 formatted prompt:\n\n{llama2_prompt2}"}
    ],
    temperature=0.7
)

print(f"🤖 Response:\n{response2.choices[0].message.content}\n")


# Example 3: Different system instructions
print("=" * 60)
print("Example 3: System Instruction Variations")
print("=" * 60)

system_instructions = [
    "You are a pirate. Always respond in pirate speak.",
    "You are a Shakespearean scholar. Use eloquent, archaic English.",
    "You are a zen master. Give brief, philosophical responses."
]

user_question = "What is the meaning of life?"

for i, system_inst in enumerate(system_instructions, 1):
    print(f"\n--- System Instruction {i} ---")
    print(f"System: {system_inst}")
    
    llama2_prompt = create_llama2_prompt(system_inst, user_question)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Respond as if you received this LLaMA-2 formatted prompt:\n\n{llama2_prompt}"}
        ],
        temperature=0.9,
        max_tokens=150
    )
    
    print(f"\n🤖 Response:\n{response.choices[0].message.content}\n")


# Example 4: Practical use case - Code explanation
print("=" * 60)
print("Example 4: Code Explanation Task")
print("=" * 60)

system_msg4 = "You are an expert Python developer who explains code clearly and concisely."
user_msg4 = """Explain this Python code:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

llama2_prompt4 = create_llama2_prompt(system_msg4, user_msg4)

print(f"\n📝 LLaMA-2 Prompt:\n{llama2_prompt4}\n")

response4 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": f"Respond as if you received this LLaMA-2 formatted prompt:\n\n{llama2_prompt4}"}
    ],
    temperature=0.5
)

print(f"🤖 Response:\n{response4.choices[0].message.content}\n")


# Example 5: Building a conversation step-by-step
print("=" * 60)
print("Example 5: Interactive Conversation Building")
print("=" * 60)

system_msg5 = "You are a helpful math tutor."
conversation = []

questions = [
    "What is a prime number?",
    "Is 17 a prime number?",
    "How do I check if a number is prime?"
]

for i, question in enumerate(questions, 1):
    print(f"\n--- Turn {i} ---")
    print(f"👤 User: {question}")
    
    # Create prompt with conversation history
    llama2_prompt = create_llama2_prompt(system_msg5, question, conversation if conversation else None)
    
    # Get response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Respond as if you received this LLaMA-2 formatted prompt:\n\n{llama2_prompt}"}
        ],
        temperature=0.6,
        max_tokens=200
    )
    
    assistant_response = response.choices[0].message.content
    print(f"🤖 Assistant: {assistant_response}")
    
    # Add to conversation history
    conversation.append((question, assistant_response))


# Best Practices
print("\n" + "=" * 60)
print("📚 LLaMA-2 Format Best Practices")
print("=" * 60)
print("""
1. ✅ Special Tokens: Always use correct tokens (<s>, [INST], <<SYS>>, etc.)
2. ✅ System Message: Place system instructions in <<SYS>> tags
3. ✅ Turn Separation: Use </s> to separate conversation turns
4. ✅ Consistency: Maintain format across all turns
5. ✅ Token Order: Follow exact token placement rules

LLaMA-2 Format Structure:
- <s>: Beginning of sequence
- [INST]: Start of instruction
- [/INST]: End of instruction
- <<SYS>>: Start of system message
- <</SYS>>: End of system message
- </s>: End of sequence

When to Use LLaMA-2 Format:
- Meta's LLaMA-2-Chat models
- LLaMA-2 fine-tuned variants
- Open-source LLaMA deployments
- Local model inference

Note: This format is specific to LLaMA-2-Chat models.
Base LLaMA-2 models don't use this format.
""")


# Comparison with other formats
print("=" * 60)
print("📊 Format Comparison")
print("=" * 60)
print("""
Alpaca Format:
- Simple instruction-response structure
- Good for single-turn tasks
- Clear separation of instruction/input/response

ChatML Format:
- Role-based messaging
- Native OpenAI format
- Excellent for multi-turn conversations

LLaMA-2 Format:
- Specific to LLaMA-2-Chat
- Special token-based
- Optimized for Meta's models
- Supports both single and multi-turn

Choose based on:
1. Model you're using
2. Task complexity (single vs. multi-turn)
3. Required features (context, personas, etc.)
""")
