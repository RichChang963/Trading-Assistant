import json
import logging
import os
from typing import Any

from db.memory import MemoryRepository
from db.repository import AnalysisRepository

logger = logging.getLogger(__name__)

# No auth yet: replace with a verified identity before supporting multiple users.
DEFAULT_USER_ID = os.getenv("APP_USER_ID", "local")


def _build_snapshots(result: dict[str, Any]) -> list[dict]:
    raw = result.get("data_response")
    routing = result.get("routing_info") or {}
    if not raw:
        return []
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        payload = {"text": raw}
    if not isinstance(payload, dict):
        payload = {"data": payload}
    params = routing.get("parameters") or {}
    return [
        {
            "provider": "openbb",
            "endpoint": routing.get("suggested_tool"),
            "symbol": params.get("symbol"),
            "payload": payload,
        }
    ]


def run_analysis(
    orchestrator,
    query: str,
    session_id: str,
    user_id: str = DEFAULT_USER_ID,
    verbose: bool = False,
    repository: AnalysisRepository | None = None,
) -> dict[str, Any]:
    """Run the orchestrator and persist the run; DB failures never block the answer."""
    repository = repository or AnalysisRepository()

    run_id = None
    try:
        run_id = repository.create_analysis(user_id=user_id, query=query)
    except Exception:
        logger.exception("Could not create analysis record")

    try:
        result = orchestrator.run_query(query, verbose=verbose, session_id=session_id)
    except Exception as exc:
        if run_id is not None:
            _safely(repository.mark_failed, run_id, str(exc))
        raise

    response = orchestrator.response_from_result(result)
    if run_id is not None:
        if result.get("error") or "final_response" not in result:
            _safely(repository.mark_failed, run_id, result.get("error") or "missing final response", response)
        else:
            _safely(repository.save_analysis_result, run_id, response, _build_snapshots(result))
            _safely(_remember, run_id, user_id, query, response, result)

    return {"run_id": run_id, "response": response, "result": result}


def _remember(run_id: int, user_id: str, query: str, response: str, result: dict[str, Any]) -> None:
    # Keep only the analysis text; raw data lives in api_snapshots.
    summary = response.split("\n---\n<details>", 1)[0].strip()
    if not summary:
        return
    params = (result.get("routing_info") or {}).get("parameters") or {}
    symbol = params.get("symbol")
    MemoryRepository().add_memory(
        user_id=user_id,
        analysis_run_id=run_id,
        content=f"Q: {query}\n\n{summary}",
        metadata={"kind": "analysis_summary", "symbol": symbol.upper() if symbol else None},
    )


def _safely(fn, *args) -> None:
    try:
        fn(*args)
    except Exception:
        logger.exception("Could not persist analysis record")
