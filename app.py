import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

from agents.pdf_agent import index_pdfs
from agents.router_graph import build_graph

load_dotenv()

st.set_page_config(page_title="TCS GenAI Multi-Agent Assistant", layout="wide")
st.title("📌 GenAI Multi-Agent Support Assistant")

graph = build_graph()

# Session state
if "chat" not in st.session_state:
    st.session_state.chat = []
if "indexed" not in st.session_state:
    st.session_state.indexed = False
if "uploaded_paths" not in st.session_state:
    st.session_state.uploaded_paths = []

with st.sidebar:
    st.header("📄 Policy Documents")
    uploaded = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)

    if uploaded:
        st.session_state.uploaded_paths = []
        for f in uploaded:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp.write(f.read())
            tmp.close()
            st.session_state.uploaded_paths.append(tmp.name)
        st.info(f"{len(st.session_state.uploaded_paths)} PDF(s) ready.")

    if st.button("Index Uploaded PDFs"):

        if not st.session_state.uploaded_paths:
            st.warning("Upload at least 1 PDF first.")
        else:
            with st.spinner("Indexing PDFs (chunking + upserting to Pinecone)..."):
                chunks = index_pdfs(st.session_state.uploaded_paths)
            st.session_state.indexed = True
            st.success(f"✅ Indexed {chunks} chunks into Pinecone!")

    st.divider()
    st.header("🗄️ Structured Data")
    st.write("SQLite DB: `data/customers.db`")
    st.caption("Run: `python scripts/seed_sqlite.py` to seed dummy customers/tickets.")

st.subheader("💬 Chat")

# Show chat history
for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.write(msg)

question = st.chat_input("Ask about policy OR customer/tickets (e.g., 'refund policy' or 'customer Ema tickets')")

if question:
    st.session_state.chat.append(("user", question))
    with st.chat_message("user"):
        st.write(question)

    if not st.session_state.indexed:
        # still allow SQL questions without indexing PDFs
        pass

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = graph.invoke({"question": question, "route": None, "answer": None})
            answer = result.get("answer", "No answer.")
            route = result.get("route", "unknown")

        st.write(answer)
        st.caption(f"Agent used: **{route.upper()}**")

    st.session_state.chat.append(("assistant", answer))
