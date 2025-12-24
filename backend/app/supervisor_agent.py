import os
from dotenv import load_dotenv, find_dotenv
from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from pydantic import SecretStr

from .toolcalling_agent import run_tool_calling_agent_with_langgraph
from .rag_agent import generate_response as run_rag_agent

# Ensure load the repository .env
load_dotenv(find_dotenv())
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("Missing GROQ_API_KEY")

# final summarizer llm
supervisor_llm = ChatGroq(
    api_key=SecretStr(groq_api_key),
    model="groq/compound-mini",  
    temperature=0.5
)

# === LangGraph State ===
class SupervisorState(TypedDict):
    question: str
    rag_output: str
    tool_output: str
    messages: Annotated[list, add_messages]

# === RAG Agent Node ===
def rag_agent_node(state: SupervisorState) -> dict:
    question = state["question"]
    rag_output = run_rag_agent(question)
    return {"rag_output": rag_output}

# === Tool Agent Node ===
def tool_agent_node(state: SupervisorState) -> dict:
    question = state["question"]
    tool_output = run_tool_calling_agent_with_langgraph(question)
    return {"tool_output": tool_output}

# === Summary Node ===
def summary_node(state: SupervisorState) -> dict:
    question = state["question"]
    rag = state.get("rag_output", "Not available")
    tool = state.get("tool_output", "Not available")

    system_prompt = (
        "You are a helpful tutor. Based on the following materials and extra sources, give a simple and clear answer to the question."
        " Include helpful links if available, and explain things like you're teaching a beginner."
        "\n\n"
        f"QUESTION: {question}\n\n"
        f"Materials:\n{rag}\n\n"
        f"Extra Info:\n{tool}\n\n"
        "Answer:"
    )

    final = supervisor_llm.invoke(system_prompt)
    return {"messages": [AIMessage(content=final.content)]}

# === Build LangGraph ===
graph = StateGraph(SupervisorState)

graph.add_node("run_rag", rag_agent_node)
graph.add_node("run_tool", tool_agent_node)
graph.add_node("summarize", summary_node)

# Define flow
graph.set_entry_point("run_rag")
graph.add_edge("run_rag", "run_tool")
graph.add_edge("run_tool", "summarize")
graph.set_finish_point("summarize")

# Compile
supervisor_graph = graph.compile()

# Wrapper
def supervisor_agent(question: str):
    events = supervisor_graph.stream(
        {"question": question},
        stream_mode="values"
    )

    rag_output = None
    tool_output = None
    final_msg = None

    for event in events:
        if "rag_output" in event:
            rag_output = event["rag_output"]
        if "tool_output" in event:
            tool_output = event["tool_output"]
        for msg in event.get("messages", []):
            if isinstance(msg, AIMessage):
                final_msg = msg.content

    #Check if the user asked about videos/tutorials
    if any(kw in question.lower() for kw in ["video", "youtube", "tutorial", "watch", "channel"]):
        return tool_output or "Sorry, couldn't find any relevant videos."

    return final_msg or "Sorry, no final answer was generated."

# Test
if __name__ == "__main__":
    question = "What is IP address?"
    result = supervisor_agent(question)
    print(" Final Answer:\n", result)