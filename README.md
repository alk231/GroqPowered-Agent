GroqPowered-Agent

GroqPowered-Agent is a fully local, persistent, tool-using AI assistant built with:

LangGraph for stateful agent workflows

Groq LLMs for ultra-fast inference

Streamlit for a clean chat UI

SQLite for chat persistence

MCP (Model Context Protocol) to connect external tools

Weather, Expense Tracker, Search, Stocks and Custom Tools

This project demonstrates how to build a production-grade multimodal assistant that can think, call tools, wait for results, and reply naturally — similar to ChatGPT tool-calling architecture.

📸 Screenshot
<img width="1777" height="859" alt="image" src="https://github.com/user-attachments/assets/88cb49be-ba9e-4362-8ef2-87f7fc62944b" />


🚀 Features
✅ 1. Real Chat-Like UI (Streamlit)

Clean and minimal chat layout

User & Assistant bubbles

Automatic conversation titles

Sidebar for saved threads

Persistent chat history

✅ 2. Fast Groq-Powered LLM

Uses openai/gpt-oss-120b via Groq's blazing-fast inference engine.

✅ 3. Tool Calling (LangChain + MCP)

The agent can call tools only when needed, get the results, then continue reasoning.

Integrated tools include:

Category	Tool	Description
Local	Calculator	Add/Subtract/Multiply/Divide
Local	DuckDuckGo Search	General web lookup
Local	Stock Price	Fetch real-time stock quotes
MCP	Weather (adhikasp)	Hourly & daily weather forecast
MCP	ExpenseTracker	Add/List expenses
MCP	Remote Simple Server	Custom endpoints
✅ 4. Tool Execution with Safe Threaded Async

Handles async MCP tools on Windows correctly using:

ThreadPoolExecutor

Per-thread event loops

Timeouts

Clean failure messages

No recursion loops

✅ 5. SQLite Checkpointing

Every conversation is saved into:

chatbot.db


You never lose any messages even after restarting the app.

📁 Project Structure
GroqPowered-Agent/
│
├── langgraph_sqlite_chatbot_backend.py   # Core LangGraph agent + MCP
├── langgraph_sqlite_chatbot_frontend.py  # Streamlit UI
├── chatbot.db                            # SQLite conversation history
├── .env                                  # API keys
├── requirements.txt
└── README.md

⚙️ Architecture
User → Streamlit UI
       → LangGraph
           → Groq LLM (ChatGroq)
           → Tool Router
               → Local Tools
               → MCP Servers
           ← Tool Results
       ← Final AI Response


This creates a feedback loop:

LLM decides to call a tool

Tool executes (using async or HTTP)

ToolMessage returned

LLM continues reasoning with the tool output

Result shown to user

🛠️ Installation
1. Clone repository
git clone https://github.com/youruser/GroqPowered-Agent.git
cd GroqPowered-Agent

2. Install dependencies
pip install -r requirements.txt

3. Create .env
CHAT_MODEL=openai/gpt-oss-120b
ACCUWEATHER_API_KEY=your_key_here
ALPHA_VANTAGE_KEY=your_stock_api_key

4. Run the app
streamlit run langgraph_sqlite_chatbot_frontend.py

5. Optional: Make MCP tools work on Windows

Install uvx:

pip install uv


Set full path (Windows requirement):

UVX_PATH="C:/Users/DELL/AppData/Local/Programs/Python/Python311/Scripts/uvx.exe"

🧠 How the Agent Works
1. Chat node

Runs Groq LLM, optionally producing tool_calls.

2. Tool node

Executes all tool calls:

Async supported (ainvoke)

Sync supported (invoke, callables)

Thread executor (safe for Windows)

Automatic JSON wrapping

Error-safe fallback into SystemMessage (prevents infinite graph loops)

3. Recursion-safe logic

Stops tool loops using:

Proper END routing

Avoids storing tool messages in chat history

Filters out tool-related messages on UI load

🧰 Available Tools
Local Tools

Calculator

DuckDuckGo Search

Stock Price Lookup

MCP Tools

Weather (adhikasp)

ExpenseTracker

Remote Simple Server

Add any MCP server:

MCP_SERVERS["my-server"] = {
    "transport": "streamable_http",
    "url": "https://my-server.com/mcp"
}

📝 Example Commands

Try:

What is the weather in Jamshedpur?

Add an expense of 200 rupees in food today.

Show my expenses this month.

What's the stock price of Tesla and write a short analysis?

🎯 Goals of This Project

Show a real production-ready LangGraph agent

Handle MCP tools properly on Windows

Stream responses like ChatGPT

Store conversation history

Provide clean developer experience

👨‍💻 Contributing

Pull requests are welcome.
You can add new tools, MCP servers, or improve UI.
