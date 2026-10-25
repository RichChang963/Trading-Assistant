from datetime import datetime, timezone

from backend.db.connection import get_session
from backend.db.models import AnalysisRun, ApiSnapshot


class AnalysisRepository:
    def create_analysis(self, user_id: str, query: str) -> int:
        with get_session() as session:
            run = AnalysisRun(user_id=user_id, query=query, status="pending")
            session.add(run)
            session.commit()
            return run.id

    def save_analysis_result(self, run_id: int, answer: str, snapshots: list[dict]) -> None:
        with get_session() as session:
            run = session.get(AnalysisRun, run_id)
            run.answer = answer
            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc)
            session.add_all(ApiSnapshot(analysis_run_id=run_id, **s) for s in snapshots)
            session.commit()

    def mark_failed(self, run_id: int, error: str, answer: str | None = None) -> None:
        with get_session() as session:
            run = session.get(AnalysisRun, run_id)
            run.status = "failed"
            run.error = error
            run.answer = answer
            run.completed_at = datetime.now(timezone.utc)
            session.commit()
