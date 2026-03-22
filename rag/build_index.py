import requests,os
import faiss
import pickle
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

HEADERS = {"User-Agent" : "finscope project@finscope.com"}
INDEX_DIR = Path("/app/data/indexes")

def get_cik(ticker):
    
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url,headers=HEADERS)
    data = response.json()

    for entry in data.values():
        if entry["ticker"] == ticker:
            return entry["cik_str"]


def get_filing_url(cik):
    padded_cik = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    filings = data["filings"]["recent"]
    ten_k_url = None
    ten_q_url = None

    for form, accession, primary_doc in zip(filings["form"], filings["accessionNumber"], filings["primaryDocument"]):
        if form in ("10-K", "20-F") and ten_k_url is None:
            accession_clean = accession.replace("-", "")
            ten_k_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{primary_doc}"

        if form in ("10-Q", "6-K") and ten_q_url is None:
            accession_clean = accession.replace("-", "")
            ten_q_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{primary_doc}"

        if ten_k_url and ten_q_url:
            break

    return ten_k_url, ten_q_url

def fetch_and_clean(url):
    
    response = requests.get(url,headers=HEADERS)
    soup = BeautifulSoup(response.content,"html.parser")
    text = soup.get_text()
    clean_text = " ".join(text.split())

    return clean_text



def build_save_index(ticker):
    cik = get_cik(ticker)
    ten_k_url,ten_q_url = get_filing_url(cik)
    if not ten_k_url and not ten_q_url:
        return "No SEC filings found for the ticker"
    text = ""
    if ten_k_url:
        text += fetch_and_clean(ten_k_url)
    if ten_q_url:
        text += fetch_and_clean(ten_q_url)
    spliter = RecursiveCharacterTextSplitter(chunk_size = 1000,chunk_overlap = 200)
    chunks = spliter.split_text(text)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)
    embeddings = embeddings.astype("float32")

    faiss.normalize_L2(embeddings)
    dimensions = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimensions)
    index.add(embeddings)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_DIR / f"{ticker}.index"))
    with open(str(INDEX_DIR / f"{ticker}_chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)