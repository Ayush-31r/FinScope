# FinScope 🔍
### Multi-Agent Financial Analyst System

> Drop a stock ticker. Get a full analyst brief in seconds.
---

## What it does

FinScope takes any stock ticker (AAPL, TSLA, GOOGL...) and runs 3 parallel AI agents to generate a structured financial analyst brief — pulling from SEC filings, live market data, and financial news simultaneously.

No manual research. No copy-pasting. Just a ticker.

---

## How it works

```
User Input (Ticker)
       │
  Orchestrator
  ┌────┴────┐────────────┐
  │         │            │
News      RAG          Risk
Agent     Agent        Agent
  │         │            │
DuckDuckGo SEC EDGAR   yFinance
           FAISS       Llama 3.3 70B
  └────┬────┘────────────┘
       │
  Synthesizer (Llama 3.3 70B)
       │
  5-Section Analyst Brief
```

### The 3 Agents

| Agent | Data Source | Output |
|-------|------------|--------|
| **News Agent** | DuckDuckGo | 5 recent articles with summaries |
| **RAG Agent** | SEC EDGAR 10-K/10-Q via FAISS | Top 5 relevant filing chunks |
| **Risk Agent** | yFinance (7 metrics) | Risk level, strengths, recommendation |

### The Brief
Every analysis returns a structured 5-section report:
1. Company Snapshot
2. Recent News Sentiment
3. SEC Filings Insight
4. Risk Assessment
5. Final Verdict

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Agent Orchestration | LangGraph |
| LLM | Llama 3.3 70B via Groq |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Vector Store | FAISS |
| Market Data | yFinance |
| SEC Filings | SEC EDGAR REST API |
| Web Search | DuckDuckGo |
| Backend | FastAPI |
| Frontend | React |
| Deployment | Railway |

---

## Performance

| Query Type | Latency |
|-----------|---------|
| Cold (first run, builds FAISS index) | ~16s |
| Warm (cached index) | ~2.4s |
| Latency reduction | ~85% |

FAISS indexes are persisted per ticker — repeat queries skip the embedding step entirely.

---

## Run Locally

```bash
# Clone the repo
git clone https://github.com/Ayush-31r/FinScope.git
cd FinScope

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY=your_key_here

# Start the backend
uvicorn main:app --reload

# Start the frontend (in a separate terminal)
cd frontend
npm install && npm start
```

---

## Project Structure

```
FinScope/
├── agents/
│   ├── news_agent.py
│   ├── rag_agent.py
│   └── risk_agent.py
├── orchestrator.py
├── synthesizer.py
├── main.py          # FastAPI app
├── frontend/        # React app
└── data/
    └── indexes/     # Persisted FAISS indexes
```

---

## Built by

**Ayush Rai** · [LinkedIn](https://linkedin.com/in/ayush-rai-v1) · [Portfolio](https://snglrty.vercel.app)
