"""
REST API routes for council blueprint CRUD.

Endpoints:
    GET    /api/councils/           — List all blueprints
    POST   /api/councils/           — Create a new blueprint
    GET    /api/councils/{id}       — Get a specific blueprint
    PUT    /api/councils/{id}       — Update a blueprint
    DELETE /api/councils/{id}       — Delete a blueprint
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from services.blueprint_service import (
    create_blueprint,
    delete_blueprint,
    get_blueprint,
    list_blueprints,
    update_blueprint,
)

blueprint_router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class AgentTools(BaseModel):
    webSearch: bool = False
    pdfReader: bool = False


class BlueprintNodeSchema(BaseModel):
    id: str
    label: str
    systemPrompt: str = ""
    model: str = "claude-3-5-sonnet"
    tools: AgentTools = Field(default_factory=AgentTools)
    position: dict = Field(default_factory=lambda: {"x": 0, "y": 0})


class BlueprintEdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    type: str = "linear"
    condition: Optional[str] = None


class BlueprintCreateRequest(BaseModel):
    version: int = 1
    name: str = Field(..., min_length=1, max_length=255)
    nodes: List[BlueprintNodeSchema]
    edges: List[BlueprintEdgeSchema] = []
    id: Optional[str] = None


class BlueprintUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    nodes: Optional[List[BlueprintNodeSchema]] = None
    edges: Optional[List[BlueprintEdgeSchema]] = None


class BlueprintResponse(BaseModel):
    id: str
    version: int
    name: str
    nodes: list
    edges: list
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@blueprint_router.get("/councils/", response_model=List[BlueprintResponse])
async def list_all_blueprints(
    session: AsyncSession = Depends(get_session),
):
    """List all council blueprints."""
    blueprints = await list_blueprints(session)
    return [bp.to_dict() for bp in blueprints]


@blueprint_router.post(
    "/councils/",
    response_model=BlueprintResponse,
    status_code=201,
)
async def create_new_blueprint(
    request: BlueprintCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Create a new council blueprint."""
    bp = await create_blueprint(
        session=session,
        name=request.name,
        nodes=[n.model_dump() for n in request.nodes],
        edges=[e.model_dump() for e in request.edges],
        blueprint_id=request.id,
        version=request.version,
    )
    return bp.to_dict()


@blueprint_router.get("/councils/{blueprint_id}", response_model=BlueprintResponse)
async def get_single_blueprint(
    blueprint_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Retrieve a specific blueprint by ID."""
    bp = await get_blueprint(session, blueprint_id)
    if bp is None:
        raise HTTPException(status_code=404, detail=f"Blueprint '{blueprint_id}' not found.")
    return bp.to_dict()


@blueprint_router.put("/councils/{blueprint_id}", response_model=BlueprintResponse)
async def update_existing_blueprint(
    blueprint_id: str,
    request: BlueprintUpdateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Update an existing blueprint."""
    bp = await update_blueprint(
        session=session,
        blueprint_id=blueprint_id,
        name=request.name,
        nodes=[n.model_dump() for n in request.nodes] if request.nodes is not None else None,
        edges=[e.model_dump() for e in request.edges] if request.edges is not None else None,
    )
    if bp is None:
        raise HTTPException(status_code=404, detail=f"Blueprint '{blueprint_id}' not found.")
    return bp.to_dict()


@blueprint_router.delete("/councils/{blueprint_id}", status_code=204)
async def delete_existing_blueprint(
    blueprint_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Delete a blueprint by ID."""
    deleted = await delete_blueprint(session, blueprint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Blueprint '{blueprint_id}' not found.")
