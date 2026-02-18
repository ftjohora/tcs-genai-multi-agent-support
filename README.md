# GenAI Multi-Agent Support Assistant

## 📌 Overview

This project is a **Generative AI–powered Multi-Agent Support Assistant** designed to help customer support executives quickly retrieve information from both **structured customer data** and **unstructured company policy documents** using natural language.

The system demonstrates how modern GenAI architectures can combine:

- Retrieval-Augmented Generation (RAG)
- SQL-based structured data querying
- Multi-agent routing using LangGraph
- A simple Streamlit UI

---

## 🎯 Problem Statement

Customer support agents often need to:

- Search policy documents (PDFs) for answers
- Retrieve customer profiles and past support tickets from databases

These data sources are usually disconnected.  
This project unifies them into **one conversational AI system**.

---

## 🧠 How It Works (High-Level)

1. **User asks a question in the chat UI**
2. A **LangGraph Router Agent** analyzes the question intent:
   - Policy-related → PDF Agent
   - Customer-related → SQL Agent
3. The appropriate agent is invoked:
   - **PDF Agent** retrieves relevant document chunks from Pinecone
   - **SQL Agent** queries customer & ticket data from SQLite
4. A language model generates a **clear, user-friendly response**
5. The UI displays both the answer and which agent was used

---

## 🚀 Setup Instructions Clone the Repository

On command prompt or terminal :

```bash
git clone <your-github-repo-url> (for example:  git clone https://github.com/ftjohora/tcs-genai-multi-agent-support.git )
cd tcs-genai-multi-agent-support
python -m venv .venv

windows-> .venv\Scripts\activate
mac/linux -> source .venv/bin/activate
Install Dependencies -> pip install -r requirements.txt

Seed the SQL Database-> python scripts/seed_sqlite.py
Run the App -> streamlit run app.py


Example Queries : Policy Questions (PDF Agent)

What is the refund policy?
What is the warranty policy?

Customer Questions (SQL Agent) :
Give me a quick overview of customer Ema’s profile and past support ticket details.
Show customer Sara’s recent tickets.


The UI will indicate which agent handled the request.


================================

.env ->
OPENAI_API_KEY=your_api_key_here
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=langchainvector
PINECONE_HOST=https://your-index-host.pinecone.io
------------------------------------------------------------------------------------------------------------------------------

## 📂 Project Structure

TCS/
│
├── agents/
│ ├── pdf_agent.py # Policy PDF RAG logic
│ ├── sql_agent.py # SQL customer logic
│ └── router_graph.py # LangGraph router
│
├── data/
│ └── customers.db # SQLite DB
│
├── documents/
│ └── company_policy.pdf # Sample policy document
│
├── scripts/
│ └── seed_sqlite.py # Seeds dummy SQL data
│
├── utils/
│ └── local_llm.py # HuggingFace helper
│
├── app.py # Streamlit entry point
├── mcp_server.py # MCP tool server
├── requirements.txt
├── .env.example
└── README.md


------------------------------------------------------------------------------------------------------------------------------
## 🏗️ Architecture

User (Streamlit UI)
|
v
LangGraph Router Agent
├── PDF Agent (RAG)
│ ├── PDF Loader
│ ├── Text Splitter
│ ├── Pinecone Vector DB
│ └── LLM Response
|
└── SQL Agent
├── SQLite DB
├── Customer & Ticket Query
└── LLM Summary


------------------------------------------------------------------------------------------------------------------------------
## 🛠️ Tech Stack

| Component | Technology |
|------------|------------|
| UI | Streamlit |
| Multi-Agent Routing | LangGraph |
| Vector Database | Pinecone |
| Structured Database | SQLite |
| Embeddings | Sentence Transformers |
| LLM | OpenAI / HuggingFace |
| Document Parsing | PyPDF |
| Tools API | MCP |

------------------------------------------------------------------------------------------------------------------------------

