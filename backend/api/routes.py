"""
REST API routes for CouncilOS.

Endpoints:
    POST /api/councils/run                     — Start a new council run (Phase 1)
    POST /api/councils/{id}/run                — Start a run from a blueprint (Phase 3)
    GET  /api/councils/run/{run_id}            — Poll the status/result of a run
    POST /api/councils/run/{run_id}/approve    — God Mode: approve/reject/modify (Phase 4)
    GET  /api/councils/run/{run_id}/state      — God Mode: get paused state (Phase 4)
    POST /api/councils/upload-pdf              — Upload and ingest a PDF (Phase 4)
    GET  /api/health                           — Health check
"""

import os
import tempfile
import uuid
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.run_store import run_store
from database import get_session
from services.blueprint_service import get_blueprint
from services.dynamic_graph_builder import (
    get_god_mode_state,
    resume_god_mode,
    run_blueprint_council_async,
)
from services.graph_builder import run_council_async


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
    god_mode: bool = Field(
        default=False,
        description="If true, the run pauses before each node for human approval.",
    )


class CouncilRunResponse(BaseModel):
    run_id: str
    status: str  # "pending" | "running" | "completed" | "failed" | "paused"
    message: str


class CouncilResultResponse(BaseModel):
    run_id: str
    status: str
    final_draft: Optional[str] = None
    critic_score: Optional[float] = None
    iteration_count: Optional[int] = None
    error: Optional[str] = None
    paused: Optional[bool] = None
    next_nodes: Optional[List[str]] = None
    current_draft: Optional[str] = None


class GodModeApprovalRequest(BaseModel):
    action: str = Field(
        ...,
        description="Action to take: 'approve', 'reject', or 'modify'.",
    )
    modified_state: Optional[dict] = Field(
        default=None,
        description="Partial state override when action is 'modify'.",
    )


class PdfUploadResponse(BaseModel):
    filename: str
    chunks_ingested: int
    message: str


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

    Set god_mode=true to pause before each agent node and require
    human approval via the /approve endpoint.
    """
    bp = await get_blueprint(session, blueprint_id)
    if bp is None:
        raise HTTPException(status_code=404, detail=f"Blueprint '{blueprint_id}' not found.")

    run_id = str(uuid.uuid4())
    run_store.create(run_id, request.input_topic)

    blueprint_dict = bp.to_dict()
    background_tasks.add_task(
        _execute_blueprint_run,
        run_id,
        request.input_topic,
        blueprint_dict,
        request.god_mode,
    )

    mode_label = "God Mode" if request.god_mode else "Auto-Pilot"
    return CouncilRunResponse(
        run_id=run_id,
        status="pending",
        message=(
            f"Council run started from blueprint '{bp.name}' ({mode_label}). "
            f"Connect to /ws/council/{run_id} for live updates."
        ),
    )


@router.get("/councils/run/{run_id}", response_model=CouncilResultResponse)
async def get_council_result(run_id: str):
    """
    Retrieve the current status or final result of a council run.

    In God Mode, includes paused state and next_nodes info.
    """
    run = run_store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")

    # Check for god mode paused state
    god_state = get_god_mode_state(run_id)
    paused = god_state["paused"] if god_state else None
    next_nodes = god_state["next_nodes"] if god_state else None
    current_draft = (
        god_state["current_state"].get("current_draft") if god_state else None
    )

    return CouncilResultResponse(
        run_id=run_id,
        status=run["status"],
        final_draft=run.get("final_draft"),
        critic_score=run.get("critic_score"),
        iteration_count=run.get("iteration_count"),
        error=run.get("error"),
        paused=paused,
        next_nodes=next_nodes,
        current_draft=current_draft,
    )


@router.post("/councils/run/{run_id}/approve", response_model=CouncilResultResponse)
async def approve_god_mode(
    run_id: str,
    request: GodModeApprovalRequest,
    background_tasks: BackgroundTasks,
):
    """
    Approve, reject, or modify a paused God Mode council run.

    Actions:
        approve — continue execution to the next node
        reject  — stop the run entirely
        modify  — update the state before continuing (pass modified_state)
    """
    god_state = get_god_mode_state(run_id)
    if not god_state or not god_state.get("paused"):
        raise HTTPException(
            status_code=400,
            detail=f"Run '{run_id}' is not paused in God Mode.",
        )

    if request.action == "reject":
        await resume_god_mode(run_id, action="reject")
        run_store.update(run_id, {"status": "failed", "error": "Rejected by user in God Mode."})
        return CouncilResultResponse(
            run_id=run_id,
            status="failed",
            error="Rejected by user in God Mode.",
        )

    # Resume in background (approve or modify)
    background_tasks.add_task(
        _resume_god_mode_task,
        run_id,
        request.action,
        request.modified_state,
    )

    return CouncilResultResponse(
        run_id=run_id,
        status="running",
    )


@router.get("/councils/run/{run_id}/state")
async def get_run_state(run_id: str):
    """
    Get the full paused state of a God Mode run for the approval UI.
    """
    god_state = get_god_mode_state(run_id)
    if not god_state:
        raise HTTPException(
            status_code=404,
            detail=f"No God Mode session found for run '{run_id}'.",
        )
    return god_state


@router.post("/councils/upload-pdf", response_model=PdfUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and ingest a PDF file into the ChromaDB vector store.

    The content becomes searchable by agents with the PDF Reader tool enabled.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    from tools.pdf_reader import ingest_pdf

    # Save upload to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        chunks = ingest_pdf(tmp_path)
    finally:
        os.unlink(tmp_path)

    return PdfUploadResponse(
        filename=file.filename,
        chunks_ingested=chunks,
        message=f"Successfully ingested {chunks} chunks from '{file.filename}'.",
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
    run_id: str,
    input_topic: str,
    blueprint: dict,
    god_mode: bool = False,
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
            god_mode=god_mode,
            on_node_event=lambda nid, node: run_store.update(
                nid, {"active_node": node}
            ),
        )

        # In god mode, the first invoke will pause at the first node
        if god_mode and final_state:
            god_state = get_god_mode_state(run_id)
            if god_state and god_state.get("paused"):
                run_store.update(run_id, {
                    "status": "paused",
                    "active_node": god_state["next_nodes"][0] if god_state["next_nodes"] else None,
                })
                return

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


async def _resume_god_mode_task(
    run_id: str,
    action: str,
    modified_state: Optional[dict],
) -> None:
    """Background task that resumes a god mode run after human approval."""
    run_store.update(run_id, {"status": "running"})
    try:
        state = await resume_god_mode(run_id, action=action, modified_state=modified_state)

        if state is None:
            run_store.update(run_id, {"status": "failed", "error": "God Mode session not found."})
            return

        # Check if paused again at next node
        god_state = get_god_mode_state(run_id)
        if god_state and god_state.get("paused"):
            run_store.update(run_id, {
                "status": "paused",
                "active_node": god_state["next_nodes"][0] if god_state["next_nodes"] else None,
                "current_draft": state.get("current_draft"),
                "critic_score": state.get("critic_score"),
                "iteration_count": state.get("iteration_count"),
            })
        else:
            run_store.update(
                run_id,
                {
                    "status": "completed",
                    "final_draft": state.get("current_draft"),
                    "critic_score": state.get("critic_score"),
                    "iteration_count": state.get("iteration_count"),
                    "active_node": "done",
                },
            )
    except Exception as exc:  # noqa: BLE001
        run_store.update(run_id, {"status": "failed", "error": str(exc)})
