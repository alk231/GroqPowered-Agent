# 🚀 GroqPowered-Agent

<div align="center">

![Banner](https://private-user-images.githubusercontent.com/123632977/516215361-294e376f-843b-4fd8-b41a-425074c7b79b.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjM1NDkzNjMsIm5iZiI6MTc2MzU0OTA2MywicGF0aCI6Ii8xMjM2MzI5NzcvNTE2MjE1MzYxLTI5NGUzNzZmLTg0M2ItNGZkOC1iNDFhLTQyNTA3NGM3Yjc5Yi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMTE5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTExOVQxMDQ0MjNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05OWJjMjk2MGFkMzIwMWExY2U3NmIwZGMwNjQyYTNlM2JmNDhiM2ZjODFkM2UxODk4MDQ3NWY3MDkwNGRkNjEzJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.53hNRsJSYNbTf0VAbYs9oCJH3kHkzp9hAVM-pXqUwEM)

**A blazing-fast, tool-using AI agent powered by Groq + LangGraph + MCP**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Enabled-green.svg)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/Groq-Powered-orange.svg)](https://groq.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**GroqPowered-Agent** is a production-ready AI chatbot that combines the ultra-fast inference of **Groq LLMs** with the powerful agentic workflows of **LangGraph** and the extensibility of **MCP (Model Context Protocol)**. Build intelligent assistants that can use tools, maintain conversation history, and provide a ChatGPT-like experience.

### 🎯 Key Highlights

- ⚡ **Blazing Fast** - Powered by Groq's ultra-fast LLM inference engine
- 🛠️ **Tool-Calling** - Execute tools like ChatGPT (weather, stocks, search, expenses)
- 💾 **Persistent Memory** - SQLite-backed conversation history
- 🎨 **Beautiful UI** - Smooth Streamlit interface with streaming responses
- 🏗️ **Production-Ready** - Thread-safe, error-handling, timeout protection
- 🔌 **Extensible** - Easy to add custom MCP servers and tools

---

## ✨ Features

### 🔥 Blazing Fast Groq LLM
Powered by `openai/gpt-oss-120b` running on Groq's ultra-fast inference engine for near-instant responses.

### 🧩 Tool-Calling Like ChatGPT
Uses LangChain + MCP to safely execute tools:
- 🌤️ **Weather** - Real-time hourly forecasts
- 📈 **Stock Prices** - Live market data
- 💰 **Expense Tracker** - Add and view expenses
- 🔍 **DuckDuckGo Search** - Web search capabilities
- ➕ **Custom MCP Servers** - Easily integrate your own tools

### 💾 Persistent Chat History
All conversations stored in `chatbot.db` with automatic restoration and elegant UI management.

### 🖥️ Streamlit UI
- ✅ Smooth chat experience with streaming responses
- ✅ Auto-generated conversation titles
- ✅ Sidebar for browsing chat history
- ✅ Loading indicators during tool execution
- ✅ Clean message bubbles (user/assistant)

### 🛠️ Production-Grade Architecture
- Thread-safe async tool execution
- Safe timeout handling
- No recursion loops
- Automatic error recovery
- Multi-server MCP support
- Custom LangGraph workflow

---

## 📁 Project Structure

```
GroqPowered-Agent/
│
├── langgraph_sqlite_chatbot_backend.py   # Backend: LangGraph + Groq + MCP
├── langgraph_sqlite_chatbot_frontend.py  # Frontend: Streamlit UI
├── chatbot.db                             # SQLite conversation history
├── .env                                   # API Keys (create this)
├── requirements.txt                       # Python dependencies
└── README.md                              # This file
```

---

## ⚙️ Architecture

```
┌───────────────────────────┐
│     Streamlit UI          │
└──────────────▲────────────┘
               │
         User Input
               │
┌──────────────┴────────────┐
│    LangGraph Agent        │
└──────────────▲────────────┘
               │
    LLM Decides (call tool or answer)
               │
┌──────────────┴─────────────────────┐
│                                     │
┌─────▼──────┐         ┌────────▼────────┐
│   Tools    │         │   MCP Servers   │
│Calculator  │         │   Weather       │
│DDG Search  │         │ExpenseTracker   │
│StockPrice  │         │Remote Server    │
└─────▲──────┘         └────────▲────────┘
      │                         │
      └─────────────┬───────────┘
                    │
              Tool Output
                    │
              Final AI Reply
```

---

## 🧰 Available Tools

### 🔧 Local Tools
- **Calculator** - Perform mathematical calculations
- **DuckDuckGo Search** - Search the web
- **Stock Price Lookup** - Get real-time stock data

### 🌐 MCP Tools
- **Weather** - Hourly weather forecasts
- **Expense Tracker** - Add and list expenses
- **Remote Simple Server** - Example remote MCP server

### ➕ Add Your Own MCP Servers

```python
MCP_SERVERS["my-server"] = {
    "transport": "streamable_http",
    "url": "https://my-server.com/mcp"
}
```

---

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- API keys (AccuWeather, Alpha Vantage)

### Step 1: Clone the Repository

```bash
git clone https://github.com/alk231/GroqPowered-Agent.git
cd GroqPowered-Agent
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```env
CHAT_MODEL=openai/gpt-oss-120b
ACCUWEATHER_API_KEY=your_key_here
ALPHA_VANTAGE_KEY=your_stock_api_key
```

### Step 4: (Optional) Windows MCP Support

For weather MCP server on Windows:

```bash
pip install uv
```

Set the UVX path in your code:
```python
UVX_PATH = "C:/Users/DELL/AppData/Local/Programs/Python/Python311/Scripts/uvx.exe"
```

---

## 🚀 Usage

### Start the Application

```bash
streamlit run langgraph_sqlite_chatbot_frontend.py
```

The app will open in your browser at `http://localhost:8501`

### Example Commands

Try these commands to test the agent:

```
💬 What's the weather in Korba for the next few hours?

💬 Add an expense of ₹150 in travel category

💬 Show my expenses this month

💬 What is the stock price of Tesla? Give a short analysis

💬 Search latest news about Indian Space Research
```

---

## 🧠 How It Works

### 1. Chat Node
- Sends messages + conversation history to Groq LLM
- LLM decides whether to call a tool or respond directly

### 2. Tool Node
- Executes tools in a safe thread pool
- Supports both async `.ainvoke()` and sync `.invoke()`
- Graceful timeout and error handling

### 3. Recursion Safety
- Prevents infinite loops
- Tool messages are not restored into history
- System messages filtered appropriately

### 4. Smooth UI
- Loading indicators during tool execution
- Streaming assistant responses
- ChatGPT-like user experience

---

## 🎯 Project Goals

- ✅ Build a real-world LangGraph agentic workflow
- ✅ Demonstrate MCP tool integration with Groq
- ✅ Provide a template for production AI chatbots
- ✅ Rock-solid tool execution (even on Windows)
- ✅ Fast, clean, and intuitive user experience

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

- 🆕 Add new MCP servers
- 🔧 Create new tools
- 🎨 Improve the UI/UX
- 🧠 Enhance agent logic
- 📝 Improve documentation
- 🐛 Report bugs and issues

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - Ultra-fast LLM inference
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent workflow engine
- [Streamlit](https://streamlit.io/) - Beautiful web UI
- [MCP](https://github.com/anthropics/mcp) - Model Context Protocol

---

## 📬 Contact

**Author:** alk231  
**GitHub:** [@alk231](https://github.com/alk231)  
**Repository:** [GroqPowered-Agent](https://github.com/alk231/GroqPowered-Agent)

---

<div align="center">

**If you find this project useful, please consider giving it a ⭐!**

[![Star this repo](https://img.shields.io/github/stars/alk231/GroqPowered-Agent?style=social)](https://github.com/alk231/GroqPowered-Agent)

</div>
