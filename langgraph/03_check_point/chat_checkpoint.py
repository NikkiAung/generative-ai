from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()

llm = init_chat_model(model="gpt-4.1-mini", model_provider="openai")


class State(TypedDict):
    # add_messages appends to the list instead of overwriting it
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    # Call LLM with full message history and return only the new response
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

# Flow: START → chatbot → END
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Compile without persistence (for quick testing)
graph = graph_builder.compile()


DB_URI = "mongodb://admin:admin@localhost:27017"

with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    # Compile again with MongoDB — same graph, now with memory
    graph_with_checkpoint = graph_builder.compile(checkpointer=checkpointer)

    # thread_id is like a session ID — same ID picks up where the last run left off
    config = {"configurable": {"thread_id": "Aung"}}

    last_chunk = None
    for chunk in graph_with_checkpoint.stream(
        {"messages": ["My name is Aung Nanda Oo"]},
        config,
        stream_mode="values"  # yields state snapshot after each node
    ):
        chunk = chunk["messages"][-1]
        last_chunk = chunk

    # Final state after all nodes ran
    print("\nupdated_state:", last_chunk)

# Flow: START → chatbot → END  (with checkpoint saved to MongoDB per thread_id)