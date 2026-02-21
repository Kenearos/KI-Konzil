"""
WebSocket endpoint for real-time agent status updates.

Clients connect to /ws/council/{run_id} and receive JSON events whenever
an agent node becomes active or the run status changes.

Event format:
    {"event": "node_active", "run_id": "...", "node": "master_agent", "iteration": 2}
    {"event": "run_paused", "run_id": "...", "next_nodes": ["critic_agent"], "current_draft": "..."}
    {"event": "run_complete", "run_id": "...", "final_draft": "...", "critic_score": 8.5}
    {"event": "run_failed", "run_id": "...", "error": "..."}
"""

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.run_store import run_store
from services.dynamic_graph_builder import get_god_mode_state


ws_router = APIRouter()

# Active WebSocket connections keyed by run_id
_connections: dict[str, list[WebSocket]] = {}


async def broadcast_event(run_id: str, event: dict) -> None:
    """
    Send an event to all WebSocket clients subscribed to a run_id.

    Args:
        run_id: The council run identifier.
        event:  The event dict to serialize and broadcast.
    """
    clients = _connections.get(run_id, [])
    disconnected = []

    for ws in clients:
        try:
            await ws.send_text(json.dumps(event))
        except Exception:  # noqa: BLE001
            disconnected.append(ws)

    # Clean up dead connections
    for ws in disconnected:
        clients.remove(ws)


@ws_router.websocket("/ws/council/{run_id}")
async def council_websocket(websocket: WebSocket, run_id: str):
    """
    WebSocket endpoint for live council run updates.

    On connect: sends the current run status immediately.
    While running: polls the run store and pushes status changes.
    On paused: sends a god mode pause event with next_nodes.
    On complete/failed: sends a final event and closes the connection.
    """
    await websocket.accept()

    # Register this client
    if run_id not in _connections:
        _connections[run_id] = []
    _connections[run_id].append(websocket)

    try:
        # Send current state immediately on connect
        run = run_store.get(run_id)
        if run is None:
            await websocket.send_text(
                json.dumps({"event": "error", "message": f"Run '{run_id}' not found."})
            )
            return

        await websocket.send_text(
            json.dumps({"event": "connected", "run_id": run_id, "status": run["status"]})
        )

        # Poll for status changes and push updates
        last_node = None
        last_status = run["status"]
        while True:
            run = run_store.get(run_id)
            if run is None:
                break

            current_node = run.get("active_node")
            current_status = run["status"]

            # Emit node_active when the active agent changes
            if current_node and current_node != last_node and current_node != "done":
                await websocket.send_text(
                    json.dumps({
                        "event": "node_active",
                        "run_id": run_id,
                        "node": current_node,
                        "iteration": run.get("iteration_count"),
                    })
                )
                last_node = current_node

            # God Mode: emit pause event
            if current_status == "paused" and last_status != "paused":
                god_state = get_god_mode_state(run_id)
                await websocket.send_text(
                    json.dumps({
                        "event": "run_paused",
                        "run_id": run_id,
                        "next_nodes": god_state["next_nodes"] if god_state else [],
                        "current_draft": (
                            god_state["current_state"].get("current_draft", "")
                            if god_state else ""
                        ),
                        "critic_score": (
                            god_state["current_state"].get("critic_score")
                            if god_state else None
                        ),
                        "iteration_count": (
                            god_state["current_state"].get("iteration_count")
                            if god_state else None
                        ),
                    })
                )
                last_status = current_status

            # Status changed from paused back to running (user approved)
            if current_status == "running" and last_status == "paused":
                await websocket.send_text(
                    json.dumps({
                        "event": "run_resumed",
                        "run_id": run_id,
                    })
                )
                last_status = current_status

            if current_status == "completed":
                await websocket.send_text(
                    json.dumps({
                        "event": "run_complete",
                        "run_id": run_id,
                        "final_draft": run.get("final_draft"),
                        "critic_score": run.get("critic_score"),
                        "iteration_count": run.get("iteration_count"),
                    })
                )
                break

            if current_status == "failed":
                await websocket.send_text(
                    json.dumps({
                        "event": "run_failed",
                        "run_id": run_id,
                        "error": run.get("error"),
                    })
                )
                break

            last_status = current_status
            await asyncio.sleep(0.5)  # 500ms polling interval

    except WebSocketDisconnect:
        pass
    finally:
        if run_id in _connections:
            try:
                _connections[run_id].remove(websocket)
            except ValueError:
                pass
