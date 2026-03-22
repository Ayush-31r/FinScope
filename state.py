from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    ticker : str
    company_name : Optional[str]
    news_results: Optional[List[dict]]
    rag_context : Optional[str]
    risk_data : Optional[dict]
    analyst_brief : Optional[str]
    errors : List[str]
