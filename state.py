from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    ticker : str
    news_result : Optional[dict]
    rag_context : Optional[str]
    risk_data : Optional[dict]
    analyst_brief : Optional[str]
    errors : List[str]
