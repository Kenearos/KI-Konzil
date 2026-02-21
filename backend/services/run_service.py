"""
Run Service — CRUD operations for persisted council runs.

Provides async functions to create, read, update, and list council runs
in PostgreSQL. Works alongside the in-memory run_store which handles
real-time status during execution.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.council_run import CouncilRun


async def create_run(
    session: AsyncSession,
    run_id: str,
    input_topic: str,
    blueprint_id: Optional[str] = None,
    execution_mode: str = "auto-pilot",
) -> CouncilRun:
    """Create a new council run record."""
    run = CouncilRun(
        id=run_id,
        blueprint_id=blueprint_id,
        input_topic=input_topic,
        status="pending",
        execution_mode=execution_mode,
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)
    return run


async def get_run(session: AsyncSession, run_id: str) -> Optional[CouncilRun]:
    """Get a council run by ID."""
    result = await session.execute(select(CouncilRun).where(CouncilRun.id == run_id))
    return result.scalar_one_or_none()


async def list_runs(
    session: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> List[CouncilRun]:
    """List council runs, ordered by most recent first."""
    result = await session.execute(
        select(CouncilRun)
        .order_by(CouncilRun.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def update_run(
    session: AsyncSession,
    run_id: str,
    updates: dict,
) -> Optional[CouncilRun]:
    """Update a council run with the given fields."""
    run = await get_run(session, run_id)
    if run is None:
        return None

    for key, value in updates.items():
        if hasattr(run, key):
            setattr(run, key, value)

    # Auto-set completed_at when status becomes terminal
    if updates.get("status") in ("completed", "failed"):
        run.completed_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(run)
    return run
