import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from rag.build_index import build_save_index
print(f"CWD: {os.getcwd()}", flush=True)
print(f"Files in data/indexes/: {os.listdir('data/indexes/') if os.path.exists('data/indexes/') else 'DIRECTORY NOT FOUND'}", flush=True)


def retrieve(ticker, query, k=5):
    model = SentenceTransformer("all-MiniLM-L6-v2")

    if not os.path.exists(f"data/indexes/{ticker}.index"):
        build_save_index(ticker)

    index = faiss.read_index(f"data/indexes/{ticker}.index")
    with open(f"data/indexes/{ticker}_chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    
    query_embeddings = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_embeddings)
    distances, indices = index.search(query_embeddings,k)
    
    results = [chunks[i] for i in indices[0]]
    return " ".join(results)