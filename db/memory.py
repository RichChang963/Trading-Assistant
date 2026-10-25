from db.connection import get_session
from db.embeddings import embed_text
from db.models import ResearchMemory


class MemoryRepository:
    def add_memory(
        self,
        user_id: str,
        content: str,
        analysis_run_id: int | None = None,
        metadata: dict | None = None,
    ) -> int:
        memory = ResearchMemory(
            user_id=user_id,
            analysis_run_id=analysis_run_id,
            content=content,
            embedding=embed_text(content),
            metadata_=metadata or {},
        )
        with get_session() as session:
            session.add(memory)
            session.commit()
            return memory.id

    def search(self, user_id: str, query: str, limit: int = 5, symbol: str | None = None) -> list[dict]:
        distance = ResearchMemory.embedding.cosine_distance(embed_text(query))
        stmt = (
            ResearchMemory.__table__.select()
            .with_only_columns(
                ResearchMemory.id,
                ResearchMemory.content,
                ResearchMemory.metadata_,
                ResearchMemory.created_at,
                distance.label("distance"),
            )
            .where(ResearchMemory.user_id == user_id)
            .order_by(distance)
            .limit(limit)
        )
        if symbol:
            stmt = stmt.where(ResearchMemory.metadata_["symbol"].astext == symbol.upper())
        with get_session() as session:
            rows = session.execute(stmt).all()
        return [
            {
                "id": r.id,
                "content": r.content,
                "metadata": r.metadata_,
                "created_at": r.created_at,
                "similarity": 1 - r.distance,
            }
            for r in rows
        ]
