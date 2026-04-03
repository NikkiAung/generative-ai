from dotenv import load_dotenv
import os
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model

load_dotenv()

openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    raise RuntimeError("Missing OPENAI_API_KEY in .env")

llm = init_chat_model(model="gpt-4.1-mini", model_provider="openai")


class State(TypedDict):
    # add_messages tells LangGraph to append new messages instead of replacing the list
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    # Call the LLM with all messages so far and return its reply
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def Samplenode(state: State):
    # Shows that any node can push messages into state — not just the LLM
    print("\nInside SampleNode:", state)
    return {"messages": ["Hi, this is a message from SampleNode"]}


# Build the graph
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("Samplenode", Samplenode)

# Flow: START → chatbot → Samplenode → END
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "Samplenode")
graph_builder.add_edge("Samplenode", END)

graph = graph_builder.compile()

# invoke() runs the full graph and returns the final state
updated_state = graph.invoke({"messages": ["what is my name?"]})
print("\nupdated_state:", updated_state)