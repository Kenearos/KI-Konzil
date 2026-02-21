"""
Blueprint model — stores council blueprints as JSON in PostgreSQL.

Each blueprint represents a complete council graph configuration created
by the user in the "Rat-Architekt" (Setup Mode) frontend tab.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""

    pass


class Blueprint(Base):
    """
    A council blueprint stored in PostgreSQL.

    The nodes and edges are stored as JSON columns matching the
    CouncilBlueprint TypeScript interface from the frontend.
    """

    __tablename__ = "blueprints"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    version = Column(Integer, nullable=False, default=1)
    name = Column(String(255), nullable=False)
    nodes = Column(JSON, nullable=False, default=list)
    edges = Column(JSON, nullable=False, default=list)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """Serialize to the CouncilBlueprint JSON format expected by the frontend."""
        return {
            "id": self.id,
            "version": self.version,
            "name": self.name,
            "nodes": self.nodes,
            "edges": self.edges,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
