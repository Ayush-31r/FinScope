import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from rag.build_index import build_save_index
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent.parent  # rag/retriever.py → rag/ → repo root
INDEX_DIR = _REPO_ROOT / "data" / "indexes"

def retrieve(ticker, query, k=3):
    index_path = INDEX_DIR / f"{ticker}.index"
    print(f"DEBUG checking: {index_path} | exists: {index_path.exists()}", flush=True)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    index_path = INDEX_DIR / f"{ticker}.index"
    if not index_path.exists():
        build_save_index(ticker)

    index = faiss.read_index(str(index_path))
    with open(str(INDEX_DIR / f"{ticker}_chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)
    
    query_embeddings = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_embeddings)
    distances, indices = index.search(query_embeddings,k)
    
    results = [chunks[i] for i in indices[0]]
    return " ".join(results)