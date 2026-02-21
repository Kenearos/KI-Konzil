"""
CouncilRun model — persists council run history in PostgreSQL.

Each run record stores the execution metadata, status, and results.
Replaces the in-memory run_store for persistent storage.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from models.blueprint import Base


class CouncilRun(Base):
    """
    A persisted council run stored in PostgreSQL.

    Tracks the full lifecycle of a run: pending → running → completed/failed/paused.
    """

    __tablename__ = "council_runs"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    blueprint_id = Column(String(36), nullable=True)
    input_topic = Column(Text, nullable=False)
    status = Column(
        String(20),
        nullable=False,
        default="pending",
    )
    execution_mode = Column(
        String(20),
        nullable=False,
        default="auto-pilot",
    )
    final_draft = Column(Text, nullable=True)
    critic_score = Column(Float, nullable=True)
    iteration_count = Column(Integer, nullable=True)
    active_node = Column(String(255), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    def to_dict(self) -> dict:
        """Serialize to a JSON-friendly dict."""
        return {
            "id": self.id,
            "blueprint_id": self.blueprint_id,
            "input_topic": self.input_topic,
            "status": self.status,
            "execution_mode": self.execution_mode,
            "final_draft": self.final_draft,
            "critic_score": self.critic_score,
            "iteration_count": self.iteration_count,
            "active_node": self.active_node,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
