# langgraph_sqlite_chatbot_backend.py
import asyncio
import os
import sqlite3
import traceback
from typing import Annotated, Any, Dict, TypedDict

import requests
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.tools import StructuredTool, tool
from langchain_groq import ChatGroq

# MCP
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# -----------------------
# LLM
# -----------------------
llm = ChatGroq(model=os.getenv("CHAT_MODEL", "openai/gpt-oss-120b"))


# -----------------------
# History trimming
# -----------------------
def trim_history(messages, max_chars=3000):
    trimmed = []
    total = 0
    for m in reversed(messages):
        l = len(m.content)
        if total + l > max_chars:
            break
        trimmed.append(m)
        total += l
    return list(reversed(trimmed))


# -----------------------
# State typedef
# -----------------------
class ChatbotState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# -----------------------
# Local tools
# -----------------------
search_tool = DuckDuckGoSearchRun()


@tool
def calculator(a: float, b: float, operation: str) -> dict:
    """Basic calculator"""
    ops = {
        "add": a + b,
        "sub": a - b,
        "mul": a * b,
        "div": a / b if b != 0 else "error: divide by zero",
    }
    return {"result": ops.get(operation, "Invalid operation")}


@tool
def get_stock_price(symbol: str) -> dict:
    """Get latest stock price using Alpha Vantage (free tier)"""
    api_key = os.getenv("ALPHA_VANTAGE_KEY", "K3K571E7USH1KRBF")
    url = (
        "https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_INTRADAY&symbol={symbol}"
        f"&interval=5min&apikey={api_key}"
    )
    try:
        data = requests.get(url, timeout=10).json()
        last = list(data["Time Series (5min)"].keys())[0]
        price = data["Time Series (5min)"][last]["4. close"]
        return {"symbol": symbol, "price": price}
    except Exception as e:
        return {"error": f"Unable to fetch price: {str(e)}"}


local_tools = [get_stock_price, search_tool, calculator]


# -----------------------
# MCP server configs
# -----------------------
MCP_SERVERS = {
    # "weather": {
    #     "transport": "stdio",
    #     "command": "uvx",
    #     "args": [
    #         "--from",
    #         "git+https://github.com/adhikasp/mcp-weather.git",
    #         "mcp-weather",
    #     ],
    #     "env": {
    #         "ACCUWEATHER_API_KEY": os.getenv(
    #             "ACCUWEATHER_API_KEY",
    #             "zpka_14ae922f8e154d15aa6dc94f6c4a2239_6a843a24",
    #         )
    #     },
    # },
    "ExpenseTracker": {
        "transport": "streamable_http",
        "url": "https://successive-harlequin-coyote.fastmcp.app/mcp",
    },
    "remote-simple-server": {
        "transport": "streamable_http",
        "url": os.getenv(
            "REMOTE_MCP_URL", "https://test-remote-server-1.onrender.com/mcp"
        ),
    },
    
}


# -----------------------
# Helper: load MCP tools safely (works in Streamlit thread)
# -----------------------
def load_mcp_tools_sync():
    """Create a new event loop and fetch MCP tools synchronously (thread-safe)."""
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
    except Exception:
        pass

    all_tools = []

    # Load each server independently
    for server_name, server_config in MCP_SERVERS.items():
        try:
            print(f"Loading MCP server: {server_name}")
            client = MultiServerMCPClient({server_name: server_config})
            tools = loop.run_until_complete(client.get_tools())
            print(f"✓ Successfully loaded {len(tools)} tools from {server_name}")
            all_tools.extend(tools)
        except Exception as e:
            print(f"✗ Failed to load {server_name}: {str(e)}")
            continue

    try:
        loop.close()
    except Exception:
        pass

    return all_tools


# -----------------------
# Helper: wrap async tools so older LangGraph can call them synchronously
# -----------------------
def wrap_async_tool(tool_obj):
    """
    Return a StructuredTool that calls the underlying tool's `ainvoke`.
    This wrapper is synchronous (invoke will run a new event loop) so
    older LangGraph can call it via .invoke().
    """

    async def _async_call(args: Any = None):
        # Some tools expect dict args, some expect positional args.
        # We try to call ainvoke flexibly.
        try:
            if args is None:
                return await tool_obj.ainvoke({})
            # If args is a dict-like
            if isinstance(args, dict):
                return await tool_obj.ainvoke(args)
            # If args is a list/tuple, pass it as positional via kwargs if names not known.
            return await tool_obj.ainvoke(args)
        except Exception as e:
            # bubble up as str to avoid crashing
            return {"error": f"Tool execution error: {str(e)}"}

    # Make a sync-compatible callable that runs the async function
    def _sync_wrapper(tool_input: Any = None):
        # create a fresh loop for this call (safe in thread)
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
        except Exception:
            pass
        try:
            result = loop.run_until_complete(_async_call(tool_input))
        finally:
            try:
                loop.close()
            except Exception:
                pass
        return result

    # Use StructuredTool.from_function for metadata and consistent interface
    try:
        return StructuredTool.from_function(
            name=getattr(tool_obj, "name", "mcp_tool"),
            description=getattr(tool_obj, "description", "MCP tool"),
            func=_sync_wrapper,
        )
    except Exception:
        # Fallback: construct a minimal StructuredTool
        return StructuredTool.from_function(func=_sync_wrapper)


# -----------------------
# Load and prepare MCP tools
# -----------------------
_raw_mcp_tools = []
try:
    _raw_mcp_tools = load_mcp_tools_sync()
except Exception as e:
    # If MCP loading fails, continue with local tools only but log
    print("Warning: failed to load MCP tools:", str(e))
    traceback.print_exc()

# Wrap MCP tools so they expose a sync callable via StructuredTool
wrapped_mcp_tools = []
for t in _raw_mcp_tools:
    try:
        wrapped = wrap_async_tool(t)
        # ensure it has a .name attribute for mapping
        if not getattr(wrapped, "name", None):
            try:
                wrapped.name = t.name
            except Exception:
                wrapped.name = "mcp_tool"
        wrapped_mcp_tools.append(wrapped)
    except Exception as e:
        print("Failed to wrap tool:", getattr(t, "name", "<unknown>"), str(e))
        traceback.print_exc()

# Merge all tools
all_tools = local_tools + wrapped_mcp_tools

# Create a name->tool mapping for lookup
all_tools_map: Dict[str, Any] = {}
for tt in all_tools:
    name = getattr(tt, "name", None)
    if not name:
        # try to create a name
        name = f"tool_{len(all_tools_map)+1}"
        tt.name = name
    all_tools_map[name] = tt

# Bind tools into LLM (so LLM can choose tool calls)
llm_with_tools = llm.bind_tools(all_tools)


# -----------------------
# Chat node (keeps same behavior)
# -----------------------
def chat_node(state: ChatbotState):
    messages = trim_history(state["messages"])
    response = llm_with_tools.invoke(messages)
    return {"messages": response}


# -----------------------
# Tool node implementation (custom, stops recursion)
# -----------------------
def tool_node_func(state: ChatbotState):
    """
    This custom tool node:
    - reads the most recent message (should be the LLM output)
    - if it contains tool_calls, executes the first tool exactly once
    - wraps the result into a ToolMessage (so LangGraph knows a tool ran)
    - returns {"messages": [ToolMessage(...)]}
    """
    try:
        last = state["messages"][-1]
    except Exception:
        return {"messages": []}

    # No tool call requested
    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return {"messages": []}

    # Take the first tool call only
    tool_call = last.tool_calls[0]
    tool_name = tool_call.get("name")
    tool_args = tool_call.get("args", {})  # typically a dict
    tool_call_id = tool_call.get("id", None)

    if not tool_name or tool_name not in all_tools_map:
        # return an error ToolMessage so the LLM receives failure and can reply
        msg = ToolMessage(
            content=f"Error: requested tool '{tool_name}' not found.",
            tool_call_id=tool_call_id,
        )
        return {"messages": [msg]}

    tool_obj = all_tools_map[tool_name]

    # Execute tool safely
    try:
        # Some StructuredTool implementations expect a single arg (like dict)
        # We'll pass the args through directly.
        # If tool_obj has .invoke we call it (sync). Otherwise try .run or call it.
        result = None
        if hasattr(tool_obj, "invoke"):
            result = tool_obj.invoke(tool_args)
        elif hasattr(tool_obj, "__call__"):
            result = tool_obj(tool_args)
        else:
            # Last resort: try attribute ainvoke (async)
            if hasattr(tool_obj, "ainvoke"):
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                except Exception:
                    pass
                try:
                    result = loop.run_until_complete(tool_obj.ainvoke(tool_args))
                finally:
                    try:
                        loop.close()
                    except Exception:
                        pass
            else:
                result = {"error": "Tool has no callable invoke/ainvoke interface."}
    except Exception as e:
        result = {"error": f"Tool execution failed: {str(e)}"}

    # Wrap result into ToolMessage — this tells the LLM "tool finished with this content"
    try:
        content_str = result if isinstance(result, (str, dict)) else str(result)
    except Exception:
        content_str = str(result)

    tool_msg = ToolMessage(content=content_str, tool_call_id=tool_call_id)
    return {"messages": [tool_msg]}


# -----------------------
# Graph and ToolNode insertion
# -----------------------
# Use the custom tool node function (older LangGraph works fine with a function)
graph = StateGraph(ChatbotState)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node_func)  # use function node

graph.add_edge(START, "chat_node")


# Conditional edge: only go to tools when LLM produced a tool call
def should_call_tools(state: ChatbotState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "__end__"


graph.add_conditional_edges(
    "chat_node", should_call_tools, {"tools": "tools", "__end__": "__end__"}
)

graph.add_edge("tools", "chat_node")

# Compile graph (no special compile args for maximum compatibility)
chatbot = graph.compile(
    checkpointer=None
)  # we'll set checkpointer below after creation

# -----------------------
# SQLite checkpointer (attach after compile to avoid compile-time DB I/O)
# -----------------------
conn = sqlite3.connect("chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# Re-compile or attach checkpointer using graph.compile if backend requires it.
# Some versions expect checkpointer at compile-time. If so, recompile.
try:
    chatbot = graph.compile(checkpointer=checkpointer)
except TypeError:
    # older versions may not accept checkpointer here — assign manually if possible
    try:
        chatbot.checkpointer = checkpointer  # best-effort attach
    except Exception:
        pass


# -----------------------
# Helper to list previous conversations
# -----------------------
def retain_previous_chat():
    seen = set()
    chats = []
    try:
        for entry in checkpointer.list(None):
            tid = entry.config["configurable"]["thread_id"]
            if tid not in seen:
                seen.add(tid)
                chats.append(tid)
    except Exception:
        pass
    return chats


# Exports
__all__ = ["chatbot", "llm", "retain_previous_chat", "all_tools_map"]
