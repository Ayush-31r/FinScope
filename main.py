from state import AgentState
from nodes.risk_node import risk_node
from nodes.rag_node import rag_node
from nodes.news_node import news_node
from nodes.orchestrator import orchestrator
from nodes.synthesizer import synthesizer
from langgraph.graph import StateGraph, END, START

graph = StateGraph(AgentState)

# NODES
graph.add_node("orchestrator", orchestrator)
graph.add_node("news_node", news_node)
graph.add_node("rag_node", rag_node)
graph.add_node("risk_node", risk_node)
graph.add_node("synthesizer", synthesizer)

# EDGES
graph.add_edge(START,"orchestrator")

graph.add_edge("orchestrator","news_node")
graph.add_edge("orchestrator","rag_node")
graph.add_edge("orchestrator","risk_node")

graph.add_edge("news_node","synthesizer")
graph.add_edge("rag_node","synthesizer")
graph.add_edge("risk_node","synthesizer")

graph.add_edge("synthesizer",END)

app = graph.compile()
result = app.invoke({"ticker":"AAPL", "errors":[]})
print(result["analyst_brief"])