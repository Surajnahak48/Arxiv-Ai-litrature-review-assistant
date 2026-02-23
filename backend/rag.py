import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

VECTOR_DIR = "data/vectorstore"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def add_to_memory(papers):
    texts = [p["summary"] for p in papers]
    if not texts:
        return

    if os.path.exists(VECTOR_DIR):
        db = FAISS.load_local(VECTOR_DIR, embeddings)
        db.add_texts(texts)
    else:
        db = FAISS.from_texts(texts, embeddings)
        db.save_local(VECTOR_DIR)

def retrieve_context(query: str) -> str:
    if not os.path.exists(VECTOR_DIR):
        return ""

    db = FAISS.load_local(VECTOR_DIR, embeddings)
    docs = db.similarity_search(query, k=3)
    return "\n".join(d.page_content for d in docs)
