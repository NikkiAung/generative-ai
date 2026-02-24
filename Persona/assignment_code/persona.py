"""
Persona-Based Prompting Assignment
====================================
Covers all four parts of the README task:

  Part 1 — No persona:  "Explain what an API is."
  Part 2 — 3 personas:  Teacher | Senior Backend Engineer | 10-Year-Old Child
  Part 3 — Output printed for manual comparison (see Comparison.md)
  Part 4 — Docker with: No persona | Teacher | DevOps Engineer
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ──────────────────────────────────────────────
# Persona definitions
# ──────────────────────────────────────────────

PERSONAS = {
    "No Persona": None,

    "Teacher": (
        "You are a friendly computer science teacher explaining concepts to beginners. "
        "Use simple language, relatable analogies, and an encouraging tone. "
        "Keep explanations concise and accessible."
    ),

    "Senior Backend Engineer": (
        "You are a senior backend engineer with 10 years of experience. "
        "You speak technically and precisely, using correct industry terminology. "
        "Assume the reader has a developer background."
    ),

    "10-Year-Old Child": (
        "You are explaining a concept to a 10-year-old child with no technical background. "
        "Use very simple words, fun analogies from everyday life, and a playful tone. "
        "Avoid any jargon."
    ),

    "DevOps Engineer": (
        "You are an experienced DevOps engineer who works with containers and infrastructure daily. "
        "Explain concepts from an operational and deployment perspective. "
        "Use technical but practical language — focus on real-world usage and benefits."
    ),
}


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────

def ask(system_prompt: str | None, user_prompt: str) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content.strip()


def section(title: str) -> None:
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def show(persona: str, prompt: str, reply: str) -> None:
    print(f"\n--- Persona: {persona} ---")
    print(f"Prompt : {prompt}")
    print(f"Reply  :\n{reply}")
    print()


# ──────────────────────────────────────────────
# Part 1 — No Persona
# ──────────────────────────────────────────────

API_PROMPT = "Explain what an API is."

section("PART 1 — No Persona: 'Explain what an API is.'")
reply = ask(None, API_PROMPT)
show("No Persona", API_PROMPT, reply)


# ──────────────────────────────────────────────
# Part 2 — Three Personas explaining "API"
# ──────────────────────────────────────────────

section("PART 2 — Three Personas: 'Explain what an API is.'")

for persona_name in ["Teacher", "Senior Backend Engineer", "10-Year-Old Child"]:
    reply = ask(PERSONAS[persona_name], API_PROMPT)
    show(persona_name, API_PROMPT, reply)


# ──────────────────────────────────────────────
# Part 4 — Three Personas explaining "Docker"
# ──────────────────────────────────────────────

DOCKER_PROMPT = "Explain what Docker is."

section("PART 4 — Three Personas: 'Explain what Docker is.'")

for persona_name in ["No Persona", "Teacher", "DevOps Engineer"]:
    reply = ask(PERSONAS[persona_name], DOCKER_PROMPT)
    show(persona_name, DOCKER_PROMPT, reply)


print("=" * 65)
print("  Done — see Comparison.md for Part 3 & 4 analysis.")
print("=" * 65 + "\n")
