"""
REST API routes for CouncilOS.

Endpoints:
    POST /api/councils/run    — Start a new council run (async, returns run_id)
    GET  /api/councils/run/{run_id}  — Poll the status/result of a run
    GET  /api/health          — Health check
"""

import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from services.graph_builder import run_council_async
from api.run_store import run_store


router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class CouncilRunRequest(BaseModel):
    input_topic: str = Field(
        ...,
        min_length=1,
        max_length=10_000,
        description="The user's prompt or document content for the council to work on.",
        examples=["Erkläre die wichtigsten Konzepte des maschinellen Lernens für Einsteiger."],
    )


class CouncilRunResponse(BaseModel):
    run_id: str
    status: str  # "pending" | "running" | "completed" | "failed"
    message: str


class CouncilResultResponse(BaseModel):
    run_id: str
    status: str
    final_draft: Optional[str] = None
    critic_score: Optional[float] = None
    iteration_count: Optional[int] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "CouncilOS API"}


@router.post("/councils/run", response_model=CouncilRunResponse, status_code=202)
async def start_council_run(
    request: CouncilRunRequest,
    background_tasks: BackgroundTasks,
):
    """
    Start a new council run.

    The run executes asynchronously in the background. Poll
    GET /api/councils/run/{run_id} for the result, or connect to the
    WebSocket at /ws/council/{run_id} for real-time updates.
    """
    run_id = str(uuid.uuid4())

    # Register the run as pending in the in-memory store
    run_store.create(run_id, request.input_topic)

    # Schedule the graph execution as a background task
    background_tasks.add_task(_execute_run, run_id, request.input_topic)

    return CouncilRunResponse(
        run_id=run_id,
        status="pending",
        message=f"Council run started. Connect to /ws/council/{run_id} for live updates.",
    )


@router.get("/councils/run/{run_id}", response_model=CouncilResultResponse)
async def get_council_result(run_id: str):
    """
    Retrieve the current status or final result of a council run.
    """
    run = run_store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")

    return CouncilResultResponse(
        run_id=run_id,
        status=run["status"],
        final_draft=run.get("final_draft"),
        critic_score=run.get("critic_score"),
        iteration_count=run.get("iteration_count"),
        error=run.get("error"),
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _execute_run(run_id: str, input_topic: str) -> None:
    """
    Background task that runs the LangGraph council and updates the run store.
    """
    run_store.update(run_id, {"status": "running"})
    try:
        final_state = await run_council_async(
            input_topic=input_topic,
            run_id=run_id,
            on_node_event=lambda nid, node: run_store.update(
                nid, {"active_node": node}
            ),
        )
        run_store.update(
            run_id,
            {
                "status": "completed",
                "final_draft": final_state.get("current_draft"),
                "critic_score": final_state.get("critic_score"),
                "iteration_count": final_state.get("iteration_count"),
                "active_node": "done",
            },
        )
    except Exception as exc:  # noqa: BLE001
        run_store.update(run_id, {"status": "failed", "error": str(exc)})
