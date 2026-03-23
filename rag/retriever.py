import os
import gc
import faiss
import pickle
import numpy as np
from huggingface_hub import InferenceClient
from rag.build_index import build_save_index
from pathlib import Path

INDEX_DIR = Path("/app/data/indexes")

def retrieve(ticker, query, k=3):
    index_path = INDEX_DIR / f"{ticker}.index"
    print(f"DEBUG checking: {index_path} | exists: {index_path.exists()}", flush=True)

    if not index_path.exists():
        build_save_index(ticker)

    index = faiss.read_index(str(index_path))
    with open(str(INDEX_DIR / f"{ticker}_chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)

    hf = InferenceClient(token=os.environ.get("HF_TOKEN"))
    query_embeddings = np.array(hf.feature_extraction([query], model="sentence-transformers/all-MiniLM-L6-v2"), dtype="float32")
    del hf
    gc.collect()

    faiss.normalize_L2(query_embeddings)
    distances, indices = index.search(query_embeddings, k)

    results = [chunks[i] for i in indices[0]]
    return " ".join(results)