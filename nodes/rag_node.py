from rag.retriever import retrieve
import yfinance as yf

def rag_node(state):
    ticker = state["ticker"]
    company = state["company_name"]
    query = f"{company} revenue growth risk factors management outlook"
    rag_context = retrieve(ticker,query)

    return {"rag_context" : rag_context}