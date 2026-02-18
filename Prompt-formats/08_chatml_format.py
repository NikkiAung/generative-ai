"""
08. ChatML Prompt Format
=========================
Demonstrates the ChatML format used by OpenAI models (GPT-3.5, GPT-4).
ChatML is designed for multi-turn conversations with clear role separation.

Key Concepts:
- ChatML structure with special tokens
- Role-based messaging (system, user, assistant)
- Multi-turn conversation handling
- OpenAI's native message format
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def create_chatml_prompt(system_msg: str, user_msg: str, history: list = None) -> str:
    """
    Create a prompt in ChatML format (for visualization).
    Note: OpenAI API uses JSON format, but this shows the underlying structure.
    
    Args:
        system_msg: System role message
        user_msg: User message
        history: Optional conversation history
    
    Returns:
        ChatML formatted string
    """
    chatml = f"<|im_start|>system\n{system_msg}<|im_end|>\n"
    
    if history:
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            chatml += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    
    chatml += f"<|im_start|>user\n{user_msg}<|im_end|>\n"
    chatml += "<|im_start|>assistant\n"
    
    return chatml


# Example 1: Simple single-turn conversation
print("=" * 60)
print("Example 1: Single-Turn Conversation")
print("=" * 60)

system_msg1 = "You are a helpful Python programming assistant."
user_msg1 = "How do I read a CSV file in Python?"

# Show ChatML format (for educational purposes)
chatml_format = create_chatml_prompt(system_msg1, user_msg1)
print(f"\n📝 ChatML Format (Conceptual):\n{chatml_format}")

# OpenAI API uses JSON message format (which is based on ChatML)
messages1 = [
    {"role": "system", "content": system_msg1},
    {"role": "user", "content": user_msg1}
]

print(f"\n📋 OpenAI Message Format:\n{messages1}\n")

response1 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages1,
    temperature=0.7
)

print(f"🤖 Response:\n{response1.choices[0].message.content}\n")


# Example 2: Multi-turn conversation
print("=" * 60)
print("Example 2: Multi-Turn Conversation")
print("=" * 60)

conversation = [
    {"role": "system", "content": "You are a helpful math tutor."},
    {"role": "user", "content": "What is the Pythagorean theorem?"},
    {"role": "assistant", "content": "The Pythagorean theorem states that in a right triangle, a² + b² = c², where c is the hypotenuse."},
    {"role": "user", "content": "Can you give me an example with numbers?"}
]

print(f"\n📋 Conversation History:\n")
for i, msg in enumerate(conversation, 1):
    print(f"{i}. [{msg['role'].upper()}]: {msg['content']}")

response2 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=conversation,
    temperature=0.5
)

print(f"\n🤖 Assistant Response:\n{response2.choices[0].message.content}\n")


# Example 3: System message variations
print("=" * 60)
print("Example 3: Different System Personas")
print("=" * 60)

user_question = "Explain quantum computing."

personas = [
    "You are a university professor explaining to graduate students.",
    "You are explaining to a 10-year-old child.",
    "You are a comedian making jokes about technology."
]

for i, persona in enumerate(personas, 1):
    print(f"\n--- Persona {i}: {persona} ---")
    
    messages = [
        {"role": "system", "content": persona},
        {"role": "user", "content": user_question}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.8,
        max_tokens=150
    )
    
    print(f"\n🤖 Response:\n{response.choices[0].message.content}\n")


# Example 4: Conversation with context retention
print("=" * 60)
print("Example 4: Building a Conversation")
print("=" * 60)

# Simulate a chatbot conversation
conversation_history = [
    {"role": "system", "content": "You are a helpful travel assistant."}
]

user_inputs = [
    "I want to plan a trip to Japan.",
    "What's the best time to visit?",
    "What about cherry blossom season?"
]

for user_input in user_inputs:
    print(f"\n👤 User: {user_input}")
    
    # Add user message to history
    conversation_history.append({"role": "user", "content": user_input})
    
    # Get response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        temperature=0.7,
        max_tokens=200
    )
    
    assistant_message = response.choices[0].message.content
    print(f"🤖 Assistant: {assistant_message}")
    
    # Add assistant response to history
    conversation_history.append({"role": "assistant", "content": assistant_message})


# Example 5: Function calling with ChatML
print("\n" + "=" * 60)
print("Example 5: Structured Output Request")
print("=" * 60)

messages5 = [
    {"role": "system", "content": "You are a data extraction assistant. Always respond in JSON format."},
    {"role": "user", "content": "Extract information: John Doe, age 30, lives in New York, works as a Data Scientist."}
]

response5 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages5,
    temperature=0.1,
    response_format={"type": "json_object"}  # Force JSON output
)

print(f"\n🤖 Structured Response:\n{response5.choices[0].message.content}\n")


# Best Practices
print("=" * 60)
print("📚 ChatML Format Best Practices")
print("=" * 60)
print("""
1. ✅ System Message: Define behavior/persona at the start
2. ✅ Role Clarity: Use system, user, assistant roles correctly
3. ✅ Context Management: Include relevant conversation history
4. ✅ Token Limits: Be mindful of context window limits
5. ✅ Temperature: Adjust for creativity vs. consistency

ChatML Advantages:
- Clear role separation
- Multi-turn conversation support
- Easy to implement context retention
- Native OpenAI format
- Supports function calling

When to Use ChatML:
- OpenAI models (GPT-3.5, GPT-4)
- Multi-turn conversations
- Chatbot applications
- Role-based interactions
""")
