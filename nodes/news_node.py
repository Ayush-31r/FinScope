import yfinance as yf
from ddgs import DDGS

def news_node(state):
    ticker = state["ticker"]
    stock = yf.Ticker(ticker)
    company = stock.info["longName"]

    news_content = []
    with DDGS() as ddgs:
        results = list(ddgs.text(f"{company} stock earnings revenue 2025 2026 financial results",max_results=5))
        for result in results:
            news_content.append({"title" : result["title"],"body" : result["body"]})
        
    return {"news_result" : news_content}