"""
REST API routes for CouncilOS.

Endpoints:
    POST /api/councils/run               — Start a new council run (Phase 1 hard-coded graph)
    POST /api/councils/{id}/run          — Start a run from a saved blueprint (Phase 3)
    GET  /api/councils/run/{run_id}      — Poll the status/result of a run
    GET  /api/health                     — Health check
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from services.graph_builder import run_council_async
from services.dynamic_graph_builder import run_blueprint_council_async
from services.blueprint_service import get_blueprint
from database import get_session
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
    Start a new council run using the Phase 1 hard-coded graph.

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


@router.post(
    "/councils/{blueprint_id}/run",
    response_model=CouncilRunResponse,
    status_code=202,
)
async def start_blueprint_run(
    blueprint_id: str,
    request: CouncilRunRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """
    Start a council run using a saved blueprint (Phase 3 dynamic graph).

    Reads the blueprint from PostgreSQL and dynamically constructs the
    LangGraph execution graph at runtime.
    """
    bp = await get_blueprint(session, blueprint_id)
    if bp is None:
        raise HTTPException(status_code=404, detail=f"Blueprint '{blueprint_id}' not found.")

    run_id = str(uuid.uuid4())
    run_store.create(run_id, request.input_topic)

    blueprint_dict = bp.to_dict()
    background_tasks.add_task(
        _execute_blueprint_run, run_id, request.input_topic, blueprint_dict
    )

    return CouncilRunResponse(
        run_id=run_id,
        status="pending",
        message=(
            f"Council run started from blueprint '{bp.name}'. "
            f"Connect to /ws/council/{run_id} for live updates."
        ),
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
    Background task that runs the Phase 1 hard-coded LangGraph council.
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


async def _execute_blueprint_run(
    run_id: str, input_topic: str, blueprint: dict
) -> None:
    """
    Background task that runs a dynamically built LangGraph from a blueprint.
    """
    run_store.update(run_id, {"status": "running"})
    try:
        final_state = await run_blueprint_council_async(
            blueprint=blueprint,
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
