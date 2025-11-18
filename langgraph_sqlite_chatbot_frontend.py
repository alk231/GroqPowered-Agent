import streamlit as st
from langgraph_sqlite_chatbot_backend import chatbot, llm, retain_previous_chat
from langchain_core.messages import HumanMessage, AIMessage
import uuid
import re
import time


# -----------------------------------------
# STRICT GPT-STYLE TITLE GENERATOR
# -----------------------------------------
def generate_conversation_title(user_message: str):
    prompt = f"""
You are a title generator.

Task:
- Read the user's message.
- Produce ONLY a short 2–4 word title.
- No punctuation.
- No explanation.
- No chain-of-thought.
- Absolutely DO NOT output <think> or any hidden reasoning.
- ONLY output the title text.

Examples:
User: "what is 2+2"
Title: Basic Math

User: "how to debug my python code"
Title: Python Debugging

User: "tell me apple stock price"
Title: Stock Query

User: "how to create a chatbot using langgraph"
Title: LangGraph Chatbot

User: "how can I lose weight"
Title: Fitness Tips

Now generate a title.
User message: {user_message}
Title:
"""

    raw = llm.invoke([HumanMessage(content=prompt)]).content.strip()

    # clean: take first line only
    raw = raw.split("\n")[0]

    # remove leaked chain of thought markers
    raw = raw.replace("<think>", "").replace("</think>", "")

    # remove special characters
    raw = re.sub(r"[^A-Za-z0-9\s]", "", raw)

    # collapse extra spaces
    raw = " ".join(raw.split())

    # limit to 4 words max
    raw = " ".join(raw.split()[:4])

    if not raw:
        return "Conversation"

    return raw[:40]


# UUID check
def looks_like_uuid(val):
    if isinstance(val, uuid.UUID):
        return True
    if isinstance(val, str) and re.fullmatch(r"[0-9a-fA-F\-]{36}", val):
        return True
    return False


# -----------------------------------------
# THREAD HELPERS
# -----------------------------------------
def generate_thread_id():
    return uuid.uuid4()


def add_thread(thread_id):
    st.session_state["chat_thread"].append(thread_id)


def reset_chat():
    tid = generate_thread_id()
    st.session_state["thread_id"] = tid
    add_thread(tid)
    st.session_state["manage_history"] = []


def load_message(thread_id):
    state = chatbot.get_state({"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])


# -----------------------------------------
# SESSION STATE INIT
# -----------------------------------------
if "manage_history" not in st.session_state:
    st.session_state["manage_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_thread" not in st.session_state:
    st.session_state["chat_thread"] = retain_previous_chat()
    add_thread(st.session_state["thread_id"])


# -----------------------------------------
# SIDEBAR
# -----------------------------------------
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

if st.sidebar.button("Clear all chats (delete DB)"):
    st.session_state["chat_thread"] = []
    st.session_state["manage_history"] = []
    st.session_state["thread_id"] = generate_thread_id()
    st.rerun()

st.sidebar.title("My Conversations")

for idx, thread_id in enumerate(st.session_state["chat_thread"][::-1]):
    if st.sidebar.button(str(thread_id), key=f"chat-{idx}"):
        st.session_state["thread_id"] = thread_id
        messages = load_message(thread_id)

        temp = []
        for m in messages:
            role = "user" if isinstance(m, HumanMessage) else "assistant"
            temp.append({"role": role, "content": m.content})

        st.session_state["manage_history"] = temp


# -----------------------------------------
# SHOW HISTORY
# -----------------------------------------
for m in st.session_state["manage_history"]:
    with st.chat_message(m["role"]):
        st.write(m["content"])


# -----------------------------------------
# INPUT + STREAMING
# -----------------------------------------
user = st.chat_input("Type here")

if user:

    # rename UUID thread only on first message
    if looks_like_uuid(st.session_state["thread_id"]):
        title = generate_conversation_title(user)
        old = st.session_state["thread_id"]

        st.session_state["thread_id"] = title

        st.session_state["chat_thread"] = [
            title if t == old else t for t in st.session_state["chat_thread"]
        ]

    config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

    st.session_state["manage_history"].append({"role": "user", "content": user})
    with st.chat_message("user"):
        st.write(user)

    # ASSISTANT STREAM
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        for message_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user)]},
            config=config,
            stream_mode="messages",
        ):
            if isinstance(message_chunk, AIMessage):
                full_reply += message_chunk.content
                placeholder.markdown(full_reply)

    st.session_state["manage_history"].append(
        {"role": "assistant", "content": full_reply}
    )
