"""
REST endpoints for traffic data.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.db.crud import get_traffic_history

router = APIRouter(prefix="/api/traffic", tags=["traffic"])


@router.get("/history")
async def traffic_history(limit: int = 100):
    """Return the most recent traffic snapshots."""
    rows = await get_traffic_history(limit)
    return {"data": rows, "count": len(rows)}
