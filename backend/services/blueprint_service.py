"""
Blueprint Service — CRUD operations for council blueprints.

Handles persistence of blueprints to PostgreSQL via SQLAlchemy async sessions.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.blueprint import Blueprint


async def create_blueprint(
    session: AsyncSession,
    name: str,
    nodes: list,
    edges: list,
    blueprint_id: Optional[str] = None,
    version: int = 1,
) -> Blueprint:
    """Create and persist a new blueprint."""
    bp = Blueprint(
        name=name,
        version=version,
        nodes=nodes,
        edges=edges,
    )
    if blueprint_id:
        bp.id = blueprint_id

    session.add(bp)
    await session.commit()
    await session.refresh(bp)
    return bp


async def get_blueprint(
    session: AsyncSession,
    blueprint_id: str,
) -> Optional[Blueprint]:
    """Retrieve a blueprint by ID."""
    result = await session.execute(
        select(Blueprint).where(Blueprint.id == blueprint_id)
    )
    return result.scalar_one_or_none()


async def list_blueprints(session: AsyncSession) -> List[Blueprint]:
    """Retrieve all blueprints, ordered by most recently updated."""
    result = await session.execute(
        select(Blueprint).order_by(Blueprint.updated_at.desc())
    )
    return list(result.scalars().all())


async def update_blueprint(
    session: AsyncSession,
    blueprint_id: str,
    name: Optional[str] = None,
    nodes: Optional[list] = None,
    edges: Optional[list] = None,
) -> Optional[Blueprint]:
    """Update an existing blueprint. Returns None if not found."""
    bp = await get_blueprint(session, blueprint_id)
    if bp is None:
        return None

    if name is not None:
        bp.name = name
    if nodes is not None:
        bp.nodes = nodes
    if edges is not None:
        bp.edges = edges
    bp.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(bp)
    return bp


async def delete_blueprint(
    session: AsyncSession,
    blueprint_id: str,
) -> bool:
    """Delete a blueprint by ID. Returns True if deleted, False if not found."""
    bp = await get_blueprint(session, blueprint_id)
    if bp is None:
        return False

    await session.delete(bp)
    await session.commit()
    return True
