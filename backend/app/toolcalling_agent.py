import os
from dotenv import load_dotenv, find_dotenv
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langchain_community.tools import WikipediaQueryRun, TavilySearchResults
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict, Annotated

# === Load env ===

load_dotenv(find_dotenv())
groq_api_key = os.getenv("GROQ_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

# === Init LLM ===
if groq_api_key is None:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

llm = ChatGroq(
    api_key=SecretStr(groq_api_key),
    model="llama-3.1-8b-instant",
    temperature=0.6
)

# === Define Tools ===
wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(wiki_client=None, top_k_results=1, doc_content_chars_max=300)
)
tavily_web_tool = TavilySearchResults(
    tavily_api_key=tavily_api_key,
    name="tavily_web_tool"  # ✅ Required
)

# For YouTube search only
tavily_youtube_tool = TavilySearchResults(
    tavily_api_key=tavily_api_key,
    include_domains=["youtube.com"],
    name="tavily_youtube_tool" 
)

tools = [wiki_tool, tavily_web_tool, tavily_youtube_tool]

# === Bind LLM with tool use capability ===
llm_with_tools = llm.bind_tools(tools=tools)

# === LangGraph State ===
class ToolAgentState(TypedDict):
    messages: Annotated[list, add_messages]

# === Node: chatbot step ===
def run_chatbot(state: ToolAgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# === Build LangGraph ===
graph_builder = StateGraph(ToolAgentState)
graph_builder.add_node("chatbot", run_chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

# Edges
graph_builder.set_entry_point("chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_finish_point("chatbot")

tool_graph = graph_builder.compile()

# === Wrapper function ===
def run_tool_calling_agent_with_langgraph(user_input: str) -> str:
    system_prompt = (
        "You are a helpful tutor. Use Wikipedia for facts, Tavily for web results, and Tavily (YouTube) for tutorials."
    )


    events = tool_graph.stream(
        {
            "messages": [
                ("system", system_prompt),
                ("user", user_input)
            ]
        },
        stream_mode="values"
    )

    final_msg = None
    for event in events:
        for msg in event["messages"]:
            if isinstance(msg, AIMessage) and not getattr(msg.content, "startswith", lambda _: False)("<tool>"):
                final_msg = msg

    if not final_msg:
        return "Sorry, I couldn't find an answer."

    # === Step 2: Summarize multiple video results if available ===
    if isinstance(final_msg.content, list):
        summarized_videos = []
        for item in final_msg.content:
            if isinstance(item, dict) and "title" in item and "url" in item:
                summarized_videos.append(f"- [{item['title']}]({item['url']})")
        if summarized_videos:
            return "Here are some useful videos you can watch:\n" + "\n".join(summarized_videos)

    # === Step 3: If string content, return it as is that already summarized by LLM ===
    if isinstance(final_msg.content, str) and final_msg.content.strip():
        return final_msg.content

    # === Step 4: Fallback message ===
    return "I couldn't find any good video tutorials, but you can try searching YouTube or ask me another question!"