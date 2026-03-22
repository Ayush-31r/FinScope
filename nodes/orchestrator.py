import yfinance as yf


def orchestrator(state):
    if not state["ticker"]:
        return {"errors": ["No ticker provided"]}
    
    else:
        ticker = state["ticker"]

        stock = yf.Ticker(ticker)
        company = stock.info["longName"]

        return {"company_name" : company, "errors" : []}