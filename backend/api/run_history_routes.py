"""
REST API routes for council run history.

Endpoints:
    GET  /api/runs/           — List recent council runs
    GET  /api/runs/{run_id}   — Get a specific run's details
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from services.run_service import get_run, list_runs


run_history_router = APIRouter()


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class RunHistoryResponse(BaseModel):
    id: str
    blueprint_id: Optional[str] = None
    input_topic: str
    status: str
    execution_mode: str
    final_draft: Optional[str] = None
    critic_score: Optional[float] = None
    iteration_count: Optional[int] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@run_history_router.get("/runs/", response_model=List[RunHistoryResponse])
async def list_all_runs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """List recent council runs, ordered by most recent first."""
    runs = await list_runs(session, limit=limit, offset=offset)
    return [r.to_dict() for r in runs]


@run_history_router.get("/runs/{run_id}", response_model=RunHistoryResponse)
async def get_single_run(
    run_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Retrieve a specific council run by ID."""
    run = await get_run(session, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return run.to_dict()
