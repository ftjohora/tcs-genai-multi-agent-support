import os
from pathlib import Path
from typing import List, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

# Optional backends
from langchain_pinecone import PineconeVectorStore
from langchain_community.vectorstores import FAISS

# Embeddings (384-dim)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Where local FAISS index will be stored
FAISS_DIR = Path(__file__).resolve().parents[1] / "data" / "faiss_index"


def _using_pinecone() -> bool:
    return bool(os.getenv("PINECONE_API_KEY")) and bool(os.getenv("PINECONE_INDEX"))


def _load_and_chunk(pdf_paths: List[str], chunk_size: int = 1000, chunk_overlap: int = 200):
    docs = []
    for path in pdf_paths:
        docs.extend(PyPDFLoader(path).load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    return chunks


def index_pdfs(
    pdf_paths: List[str],
    namespace: str = "__default__",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> int:
    chunks = _load_and_chunk(pdf_paths, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # ---- Pinecone mode (optional) ----
    if _using_pinecone():
        index_name = os.getenv("PINECONE_INDEX")
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=embeddings,
            namespace=namespace,
        )
        vectorstore.add_documents(chunks)
        return len(chunks)

    # ---- Local FAISS mode (default) ----
    FAISS_DIR.mkdir(parents=True, exist_ok=True)

    if (FAISS_DIR / "index.faiss").exists():
        vectorstore = FAISS.load_local(str(FAISS_DIR), embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_documents(chunks)
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(str(FAISS_DIR))
    return len(chunks)


def retrieve_policy_chunks(query: str, k: int = 3, namespace: str = "__default__"):
    # ---- Pinecone mode ----
    if _using_pinecone():
        index_name = os.getenv("PINECONE_INDEX")
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=embeddings,
            namespace=namespace,
        )
        return vectorstore.similarity_search(query, k=k)

    # ---- Local FAISS mode ----
    if not (FAISS_DIR / "index.faiss").exists():
        return []

    vectorstore = FAISS.load_local(str(FAISS_DIR), embeddings, allow_dangerous_deserialization=True)
    return vectorstore.similarity_search(query, k=k)


def ask_policy(question: str, k: int = 3, namespace: str = "__default__") -> str:
    docs = retrieve_policy_chunks(query=question, k=k, namespace=namespace)
    if not docs:
        return "No relevant policy text found. Upload and index a PDF first."

    answer = []
    for i, d in enumerate(docs, start=1):
        snippet = d.page_content.strip().replace("\n", " ")
        answer.append(f"{i}) {snippet}")

    return "\n\n".join(answer)
