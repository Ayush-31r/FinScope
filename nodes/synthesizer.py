from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import MODEL_NAME, GROQ_API_KEY


llm = ChatGroq(api_key=GROQ_API_KEY,model=MODEL_NAME)
def synthesizer(state):
    risk = state["risk_data"]
    rag = state["rag_context"]
    news = state["news_result"]

    systemPrompt = """You are a quantitative financial analyst. You will be given recent news summaries, SEC filing excerpts, and a structured risk assessment for a stock. Write a professional analyst brief with exactly these five sections:

                    1. Company Snapshot — one line summary
                    2. Recent News Sentiment — what the news suggests
                    3. SEC Filings Insight — key findings from 10-K/10-Q
                    4. Risk Assessment — risk level, key risks, strengths
                    5. Final Verdict — recommendation with one line reasoning

                    Constraints:
                    - Professional, concise tone
                    - Prose only, no bullet points
                    - No disclaimers
                    - 300-400 words maximum"""
    userPrompt = f"""Give a analyst brief for the stock with
                    news summary : {news}
                    SEC-Filings : {rag}
                    risk assesment : {risk}"""

    response = llm.invoke([SystemMessage(content = systemPrompt), HumanMessage(content = userPrompt)])

    return {"analyst_brief" : response.content}