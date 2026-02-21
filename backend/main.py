"""
CouncilOS — FastAPI application entrypoint.

Start the server:
    uvicorn main:app --reload --port 8000

API Overview:
    POST   /api/councils/                     — Create a blueprint
    GET    /api/councils/                     — List all blueprints
    GET    /api/councils/{id}                 — Get specific blueprint
    PUT    /api/councils/{id}                 — Update a blueprint
    DELETE /api/councils/{id}                 — Delete a blueprint
    POST   /api/councils/run                  — Start a run (Phase 1)
    POST   /api/councils/{id}/run             — Start a run from a blueprint
    GET    /api/councils/run/{run_id}         — Poll run status/result
    POST   /api/councils/run/{run_id}/approve — God Mode: approve/reject/modify
    GET    /api/councils/run/{run_id}/state   — God Mode: paused state
    POST   /api/councils/upload-pdf           — Upload PDF for ingestion
    GET    /api/runs/                         — List run history
    GET    /api/runs/{run_id}                 — Get historical run detail
    GET    /api/health                        — Health check
    WS     /ws/council/{run_id}               — Real-time agent status events
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.blueprint_routes import blueprint_router
from api.run_history_routes import run_history_router
from api.websocket import ws_router
from database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown logic."""
    print("CouncilOS API starting up...")
    await init_db()
    print("Database initialized.")
    yield
    await close_db()
    print("CouncilOS API shutting down...")


app = FastAPI(
    title="CouncilOS API",
    description=(
        "Backend for the CouncilOS multi-agent AI pipeline platform. "
        "Orchestrates LangGraph council runs and streams real-time agent "
        "status via WebSockets."
    ),
    version="0.3.0",
    lifespan=lifespan,
)

# CORS — allow all origins in development; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST routes under /api prefix
app.include_router(router, prefix="/api")
app.include_router(blueprint_router, prefix="/api")
app.include_router(run_history_router, prefix="/api")

# Mount WebSocket routes (no prefix — path is /ws/council/{run_id})
app.include_router(ws_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
