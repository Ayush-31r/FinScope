import yfinance as yf,json,os,re
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import GROQ_API_KEY, MODEL_NAME


llm = ChatGroq(api_key=GROQ_API_KEY,model=MODEL_NAME)
def risk_node(state):
    ticker = state["ticker"]
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="3mo")
    metrics = {"currentPrice" : info.get("currentPrice"),
               "marketCap" : info.get("marketCap"),
               "trailingPE" : info.get("trailingPE"),
               "debtToEquity" : info.get("debtToEquity"),
               "fiftyTwoWeekHigh" : info.get("fiftyTwoWeekHigh"),
               "fiftyTwoWeekLow" : info.get("fiftyTwoWeekLow"),
               "annualizedVolatility" : round(float((hist["Close"].pct_change().dropna()).std() * (252**0.5)),4),
               "momentum3mo" : round(float((hist["Close"].iloc[-1] - hist["Close"].iloc[0])/(hist["Close"].iloc[0])),4)}
    

    system_prompt = "you are a quantitative risk analyst, return ONLY a JSON object with these exact keys: risk_level, key_risks, strengths, recommendation, reasoning. No markdown, no extra text."
    user_prompt = f"Analyze this stock: {json.dumps(metrics)}"

    response = llm.invoke([SystemMessage(content = system_prompt),HumanMessage(content=user_prompt)])
    match = re.search(r'\{.*\}', response.content, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in LLM response: {response.content}")
    risk_assessment = json.loads(match.group())

    return {"risk_data" : risk_assessment}