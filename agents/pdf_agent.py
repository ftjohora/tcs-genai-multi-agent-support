import os
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")



# Use your existing embeddings object / function if you already have one.
# If you already created embeddings earlier in this file, reuse it.
# Otherwise, ensure you have `embeddings = HuggingFaceEmbeddings(...)`

def index_pdfs(pdf_paths: List[str], namespace: str = "__default__", chunk_size: int = 1000, chunk_overlap: int = 200) -> int:
    docs = []
    for path in pdf_paths:
        docs.extend(PyPDFLoader(path).load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)

    index_name = os.getenv("PINECONE_INDEX")

    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings,
        namespace=namespace,
    )

    vectorstore.add_documents(chunks)
    return len(chunks)

def retrieve_policy_chunks(query: str, k: int = 3, namespace: str = "__default__"):
    index_name = os.getenv("PINECONE_INDEX")

    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings,
        namespace=namespace,
    )
    return vectorstore.similarity_search(query, k=k)
def ask_policy(question: str, k: int = 3, namespace: str = "__default__") -> str:
    docs = retrieve_policy_chunks(query=question, k=k, namespace=namespace)
    if not docs:
        return "No relevant policy text found in the indexed documents."

    answer = []
    for i, d in enumerate(docs, start=1):
        snippet = d.page_content.strip().replace("\n", " ")
        answer.append(f"{i}) {snippet}")

    return "\n\n".join(answer)
