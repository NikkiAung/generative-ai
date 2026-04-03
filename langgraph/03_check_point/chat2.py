from dotenv import load_dotenv
from typing_extensions import TypedDict
from openai import OpenAI
from typing import Optional, Literal
from langgraph.graph import StateGraph, START, END

load_dotenv()

client = OpenAI()


class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]


def chatbot(state: State):
    # First LLM pass — answers the user query
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": state.get("user_query")}]
    )
    state["llm_output"] = response.choices[0].message.content
    return state


def chatbot_gemini(state: State):
    # Fallback node for weak responses — swap client here for actual Gemini when needed
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Give a more detailed and thorough answer."},
            {"role": "user", "content": state.get("user_query")}
        ]
    )
    state["llm_output"] = response.choices[0].message.content
    return state


def endnode(state: State):
    # Terminal node — just prints and passes state through
    print("\nFinal answer:", state.get("llm_output"))
    return state


def evaluate_response(state: State) -> Literal["chatbot_gemini", "endnode"]:
    # If the response is too short, ask Gemini to try again — else we're done
    output = state.get("llm_output") or ""
    if len(output) < 100:
        return "chatbot_gemini"
    return "endnode"


# Build the graph
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("chatbot_gemini", chatbot_gemini)
graph_builder.add_node("endnode", endnode)

# START → chatbot, then decide based on evaluate_response
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", evaluate_response)  # routes to chatbot_gemini or endnode
graph_builder.add_edge("chatbot_gemini", "endnode")
graph_builder.add_edge("endnode", END)

graph = graph_builder.compile()

# Run it
result = graph.invoke({"user_query": "What is LangGraph?", "llm_output": None, "is_good": None})
print("\nFinal state:", result)

# Flow: START → chatbot → [evaluate_response] → chatbot_gemini → endnode → END
#                                              ↘ endnode → END