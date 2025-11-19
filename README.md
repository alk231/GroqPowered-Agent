🚀 GroqPowered-Agent
A Fast, Tool-Using AI Agent Built with Groq + LangGraph + MCP
<p align="center"> <img width="1246" height="850" alt="image" src="https://github.com/user-attachments/assets/294e376f-843b-4fd8-b41a-425074c7b79b" /> </p> <p align="center"> <b>Ultra-fast. Persistent. MCP-powered. Fully customizable.</b><br> Build AI assistants that use tools like weather, expenses, search, and more. </p>
✨ Highlights
🔥 Blazing Fast Groq LLM

Powered by the openai/gpt-oss-120b model running on Groq’s ultra-fast inference engine.

🧩 Tool-Calling Like ChatGPT

Uses LangChain + MCP to run tools safely:

Weather (adhikasp)

Real-time Stock Prices

Expense Tracker

DuckDuckGo Search

Custom MCP servers

💾 Persistent Chat (SQLite)

All conversations are stored in chatbot.db, restored elegantly through the UI.

🖥️ Streamlit UI

Smooth chat experience

Auto conversation titles

Sidebar for browsing old chats

Live streaming responses

Loading indicators for tool execution

Clean assistant/user message bubbles

🛠️ Production-Grade Architecture

Thread-safe async tool execution

Safe timeouts

No recursion loops

Automatic error handling

Multi-server MCP support

Custom agent workflow using LangGraph

📁 Folder Structure
GroqPowered-Agent/
│
├── langgraph_sqlite_chatbot_backend.py     # Backend: LangGraph + Groq + MCP
├── langgraph_sqlite_chatbot_frontend.py    # Frontend: Streamlit UI
├── chatbot.db                               # Persistent history
├── .env                                     # API Keys
├── requirements.txt
└── README.md

⚙️ Architecture Overview
               ┌───────────────────────────┐
               │        Streamlit UI       │
               └──────────────▲────────────┘
                              │
                              │ User Input
                              │
               ┌──────────────┴────────────┐
               │        LangGraph Agent     │
               └──────────────▲────────────┘
                              │
                         LLM Decides
                 (call tool or answer directly)
                              │
           ┌─────────────────┴──────────────────┐
           │                                    │
     ┌─────▼──────┐                    ┌────────▼────────┐
     │   Tools     │                    │    MCP Servers  │
     │ Calculator  │                    │ Weather         │
     │ DDG Search  │                    │ ExpenseTracker  │
     │ StockPrice  │                    │ Remote Server   │
     └─────▲───────┘                    └────────▲────────┘
           │ Tool Output                        │
           └────────────────────────────────────┘
                              │
                        Final AI Reply

🧰 Available Tools
🔧 Local Tools

Calculator

DuckDuckGo Search

Stock Price Lookup

🌐 MCP Tools

Weather (hourly forecast)

ExpenseTracker (add/list expenses)

Remote Simple Server

Add unlimited external MCP servers

MCP_SERVERS["my-server"] = {
    "transport": "streamable_http",
    "url": "https://my-server.com/mcp"
}

📦 Installation
1. Clone the repository
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

5. Optional (Windows MCP Support)

Install uvx to run weather server:

pip install uv


Set path:

UVX_PATH="C:/Users/DELL/AppData/Local/Programs/Python/Python311/Scripts/uvx.exe"

🧠 How It Works
1. Chat Node

Sends messages + history to Groq LLM

LLM decides whether to call a tool

2. Tool Node

Executes tools in safe thread pool

Supports async .ainvoke()

Supports sync .invoke()

Graceful timeout handling

3. Recursion Safety

No infinite loops

ToolMessages are not restored into history

System messages filtered out

4. Smooth UI

Loader indicators while tools run

Streaming assistant replies

Beautiful UI flow like ChatGPT

📝 Example Commands

Try these:

What’s the weather in Korba for the next few hours?

Add an expense of ₹150 in travel.

Show my expenses this month.

What is the stock price of Tesla and give a short analysis?

Search latest news about Indian Space Research.

🎯 Goals of This Project

Build a real-world LangGraph agent

Show how MCP tools integrate with Groq

Provide a template for production AI chatbots

Make the tool execution rock-solid even on Windows

Deliver a fast and clean user experience

🤝 Contributing

Pull requests are welcome!
You can contribute by:

Adding new MCP servers

Creating new tools

Improving UI

Enhancing the agent logic
