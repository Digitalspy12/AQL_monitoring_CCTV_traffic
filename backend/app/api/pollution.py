"""
REST endpoints for pollution data.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.db.crud import get_pollution_history

router = APIRouter(prefix="/api/pollution", tags=["pollution"])


@router.get("/history")
async def pollution_history(limit: int = 100):
    """Return the most recent pollution readings."""
    rows = await get_pollution_history(limit)
    return {"data": rows, "count": len(rows)}
