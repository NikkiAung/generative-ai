from openai import OpenAI
import requests
from dotenv import load_dotenv
import json

# Load environment variables (OPENAI_API_KEY from .env)
load_dotenv()
client = OpenAI()


# ─────────────────────────────────────────────
#  TOOL: Fetch real weather data from wttr.in
# ─────────────────────────────────────────────
def get_weather(city: str) -> str:
    """Fetch real-time weather using the free wttr.in API."""
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text.strip()}"
    return "Weather not available"


# ─────────────────────────────────────────────
#  AGENT: Think → Act → Observe loop
# ─────────────────────────────────────────────
def run_agent(user_query: str) -> str:
    """
    A simple Chain-of-Thought agent.

    The LLM responds with ONE JSON step at a time:
        {"step": "PLAN",   "content": "..."}        → Agent is thinking
        {"step": "TOOL",   "tool": "...", "input": "..."}  → Agent calls a tool
        {"step": "OUTPUT", "content": "..."}        → Agent is done
    """

    system_prompt = """\
You are a helpful assistant that thinks step by step before answering.

Available tools:
- get_weather: Gets current weather for a city. Input: city name (string)

Always respond with ONE JSON object at a time using this exact format:
  {"step": "PLAN",   "content": "<your reasoning>"}
  {"step": "TOOL",   "tool": "get_weather", "input": "<city name>"}
  {"step": "OUTPUT", "content": "<final answer for the user>"}

Do NOT skip steps. Think first, then use a tool if needed, then give the OUTPUT."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_query},
    ]

    print(f"\n🧠 Agent started for query: '{user_query}'\n")

    for iteration in range(1, 11):  # max 10 steps
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,   # lower temp → more predictable/structured output
        )

        raw = response.choices[0].message.content.strip()

        # ── Try to parse the LLM reply as JSON ──────────────────────────────
        try:
            step = json.loads(raw)
        except json.JSONDecodeError:   # ✅ Fix 5: specific exception, not bare except
            # LLM didn't follow format — treat it as a planning thought
            print(f"💭 PLAN  → {raw}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user",      "content": "Continue"})
            continue

        step_type = step.get("step", "").upper()

        # ── PLAN: agent is reasoning ─────────────────────────────────────────
        if step_type == "PLAN":
            print(f"💭 PLAN  → {step.get('content')}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user",      "content": "Continue"})

        # ── TOOL: agent calls a tool ─────────────────────────────────────────
        elif step_type == "TOOL":
            tool_name  = step.get("tool")
            tool_input = step.get("input")
            print(f"🔧 TOOL  → {tool_name}('{tool_input}')")  # ✅ Fix 4: correct TOOL label

            # Execute the tool
            tool_output = get_weather(tool_input)
            print(f"📡 OBSERVE → {tool_output}")              # ✅ Fix 4: correct OBSERVE label

            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"Tool result: {tool_output}. Continue."})

        # ── OUTPUT: agent has a final answer ─────────────────────────────────
        elif step_type == "OUTPUT":
            answer = step.get("content")
            print(f"✅ OUTPUT → {answer}\n")
            return answer

        else:
            # Unknown step type — just push it back and let the agent continue
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user",      "content": "Continue"})

    return "⚠️ Agent reached the maximum number of steps without a final answer."


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    print("=" * 55)
    print("   🌤  Chain-of-Thought Weather Agent")
    print("=" * 55)

    user_query = input("\nEnter your weather question: ").strip()
    if not user_query:
        print("No query entered. Exiting.")
        return

    result = run_agent(user_query)

    print("=" * 55)
    print(f"Final Answer: {result}")
    print("=" * 55)


if __name__ == "__main__":
    main()
