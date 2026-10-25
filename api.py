import re
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent_system import MODEL_CONFIG, create_two_agent_system
from db.service import run_analysis

LLM_LIST = ["gemini", "openai", "claude", "perplexity", "openrouter", "ollama"]
DOCS_PATH = Path(__file__).parent / "docs"

app = FastAPI(title="Trading Assistant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_orchestrators: dict = {}
_lock = threading.Lock()


def _model_name(provider: str) -> str:
    return MODEL_CONFIG.get(f"{provider.upper()}_MODEL", "")


def _get_orchestrator(provider: str):
    with _lock:
        if provider not in _orchestrators:
            _orchestrators[provider] = create_two_agent_system(provider=provider)
        return _orchestrators[provider]


def _split_raw_data(response_text: str) -> tuple[str, str | None]:
    """Separate the analysis text from the trailing <details> raw data block."""
    pattern = re.compile(
        r"<details>.*?<summary>.*?</summary>\s*(.*?)\s*</details>",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(response_text)
    if not match:
        return response_text.strip(), None
    return pattern.sub("", response_text).strip(), match.group(1).strip()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str = Field(min_length=1, max_length=100)
    provider: str


@app.get("/api/config")
def get_config():
    return {
        "providers": [{"id": p, "model": _model_name(p)} for p in LLM_LIST],
        "default_provider": MODEL_CONFIG.get("LLM_Model_provider", "gemini"),
        "example_questions": [
            "Tell me about Apple stock",
            "What is the gold price trend?",
            "Analyze gold price trends over the past year",
            "Compare Apple and Microsoft financial performance",
            "What does recent interest rate in Germany look like?",
        ],
    }


# Sync handler: FastAPI runs it in a worker thread so the LLM call does not block the loop.
@app.post("/api/chat")
def chat(req: ChatRequest):
    if req.provider not in LLM_LIST:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")
    try:
        orchestrator = _get_orchestrator(req.provider)
        outcome = run_analysis(orchestrator, req.message, session_id=req.session_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    analysis, raw_data = _split_raw_data(outcome["response"])
    return {"run_id": outcome["run_id"], "analysis": analysis, "raw_data": raw_data}


def _doc_files() -> dict[str, Path]:
    return {f.stem: f for f in sorted(DOCS_PATH.glob("*.md"))}


@app.get("/api/docs")
def list_docs():
    return [
        {"id": stem, "title": stem.replace("_", " ").title()} for stem in _doc_files()
    ]


@app.get("/api/docs/{doc_id}")
def get_doc(doc_id: str):
    path = _doc_files().get(doc_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc_id, "content": path.read_text(encoding="utf-8")}
