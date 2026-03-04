"""
FastAPI application entry point.

Starts the ASGI server, initialises the database,
mounts REST routers, and exposes the WebSocket endpoint.
"""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.pollution import router as pollution_router
from app.api.traffic import router as traffic_router
from app.config import CORS_ORIGINS
from app.db.database import init_db
from app.models.schemas import HealthCheck
from app.ws.stream import (
    broadcast_loop,
    get_latest_payload,
    register_client,
    start_processing,
    stop_processing,
    unregister_client,
)

# ── Logging ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
)
logger = logging.getLogger(__name__)

# ── App ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Digital Twin — Smart City API",
    version="0.1.0",
    description="Real-time traffic detection and pollution estimation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(traffic_router)
app.include_router(pollution_router)


# ── Lifecycle ──────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    logger.info("Initialising database…")
    await init_db()
    logger.info("Starting video processing…")
    start_processing()
    asyncio.create_task(broadcast_loop())
    logger.info("🚀  Digital Twin API is live.")


@app.on_event("shutdown")
async def on_shutdown():
    stop_processing()
    logger.info("Shutdown complete.")


# ── Health ─────────────────────────────────────────────────────────────

@app.get("/", response_model=HealthCheck, tags=["system"])
async def root():
    return HealthCheck()


@app.get("/api/snapshot", tags=["system"])
async def snapshot():
    """Return the latest processing snapshot (REST fallback)."""
    return get_latest_payload()


# ── WebSocket ──────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    q = register_client()
    logger.info("WebSocket client connected.")
    try:
        while True:
            payload = await q.get()
            await ws.send_text(json.dumps(payload, default=str))
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as exc:
        logger.warning("WebSocket error: %s", exc)
    finally:
        unregister_client(q)
