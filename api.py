"""
FinScope FastAPI Backend
POST /analyze  →  runs the LangGraph pipeline and returns the analyst brief
"""

import os
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# ── Logging FIRST, before any project imports ──────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("=== IMPORT START ===")

try:
    logger.info("Importing build_graph (triggers all node imports)...")
    from main import build_graph
    logger.info("=== ALL IMPORTS OK ===")
except Exception as e:
    logger.exception("=== IMPORT CRASHED ===")
    raise

# ── Lifespan: compile graph once at startup ────────────────────────────────────
graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph
    logger.info("Pulling indexes from HuggingFace...")
    from hf_index_storage import pull_indexes
    pull_indexes()
    os.makedirs("/app/data/indexes", exist_ok=True)
    for f in os.listdir("/app/data/indexes"):
        print(f"FOUND: {f}", flush=True)

    logger.info("Indexes ready.")
    logger.info("Compiling LangGraph pipeline...")
    graph = build_graph()
    logger.info("Pipeline ready.")
    yield
    logger.info("Shutting down.")

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FinScope API",
    description="Multi-Agent Financial Analysis powered by LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# ── Schemas ────────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    ticker: str

    @field_validator("ticker")
    @classmethod
    def normalize(cls, v: str) -> str:
        v = v.strip().upper()
        if not v or not v.replace(".", "").replace("-", "").isalnum():
            raise ValueError("Invalid ticker symbol")
        if len(v) > 10:
            raise ValueError("Ticker too long")
        return v

class AgentStatus(BaseModel):
    news: str
    rag: str
    risk: str

class AnalyzeResponse(BaseModel):
    ticker: str
    brief: str
    agent_status: AgentStatus
    elapsed_seconds: float

# ── Endpoint ───────────────────────────────────────────────────────────────────

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    if graph is None:
        raise HTTPException(status_code=503, detail="Pipeline not ready yet")

    ticker = req.ticker
    logger.info("Received request for %s", ticker)
    t0 = time.time()

    initial_state = {
        "ticker": ticker,
        "company_name": None,
        "news_result": None,
        "rag_context": None,
        "risk_data": None,
        "analyst_brief": None,
        "errors": [],
    }

    try:
        final_state = graph.invoke(initial_state)
    except Exception as exc:
        logger.exception("Pipeline error for %s", ticker)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}")

    if final_state.get("errors"):
        raise HTTPException(status_code=422, detail="; ".join(final_state["errors"]))

    elapsed = round(time.time() - t0, 2)
    logger.info("Analysis for %s completed in %.1fs", ticker, elapsed)

    def _dict_summary(d) -> str:
        if not d:
            return "No output"
        if isinstance(d, list):
            return f"{len(d)} articles retrieved" if d else "No output"
        for v in d.values():
            if isinstance(v, str) and v.strip():
                return v.split("\n")[0][:120]
        return "Done"

    def _first_line(text: str | None) -> str:
        if not text:
            return "No output"
        return text.split("\n")[0][:120]

    return AnalyzeResponse(
        ticker=ticker,
        brief=final_state.get("analyst_brief") or "No brief generated.",
        agent_status=AgentStatus(
            news=_dict_summary(final_state.get("news_result")),
            rag=_first_line(final_state.get("rag_context")),
            risk=_dict_summary(final_state.get("risk_data")),
        ),
        elapsed_seconds=elapsed,
    )

# ── Serve React frontend ───────────────────────────────────────────────────────
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

    @app.get("/")
    async def serve_frontend():
        return FileResponse("frontend/dist/index.html")

# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "pipeline_ready": graph is not None}

# ── Local dev ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)