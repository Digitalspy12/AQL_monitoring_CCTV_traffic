"""
CRUD helpers for traffic and pollution data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.database import get_db


# ── Traffic ────────────────────────────────────────────────────────────

async def insert_traffic(counts: dict[str, int], fps: float) -> None:
    """Persist a traffic snapshot."""
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO traffic_log
               (timestamp, car_count, bus_count, motorcycle_count, truck_count, total_count, fps)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now(timezone.utc).isoformat(),
                counts.get("car", 0),
                counts.get("bus", 0),
                counts.get("motorcycle", 0),
                counts.get("truck", 0),
                sum(counts.values()),
                fps,
            ),
        )
        await db.commit()
    finally:
        await db.close()


async def get_traffic_history(limit: int = 100) -> list[dict[str, Any]]:
    """Return recent traffic snapshots, newest first."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM traffic_log ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


# ── Pollution ──────────────────────────────────────────────────────────

async def insert_pollution(
    lat: float, lng: float, aqi: float, noise_db: float, vehicle_count: int
) -> None:
    """Persist a pollution reading."""
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO pollution_log
               (timestamp, lat, lng, aqi, noise_db, vehicle_count)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                datetime.now(timezone.utc).isoformat(),
                lat, lng, aqi, noise_db, vehicle_count,
            ),
        )
        await db.commit()
    finally:
        await db.close()


async def get_pollution_history(limit: int = 100) -> list[dict[str, Any]]:
    """Return recent pollution readings, newest first."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM pollution_log ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()
