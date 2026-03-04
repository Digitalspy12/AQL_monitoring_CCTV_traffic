"""
SQLite database — async access via aiosqlite.
Creates tables on startup and provides connection helpers.
"""

from __future__ import annotations

import aiosqlite

from app.config import DB_PATH

# ── Table DDL ──────────────────────────────────────────────────────────

_TRAFFIC_TABLE = """
CREATE TABLE IF NOT EXISTS traffic_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,
    car_count   INTEGER DEFAULT 0,
    bus_count   INTEGER DEFAULT 0,
    motorcycle_count INTEGER DEFAULT 0,
    truck_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    fps         REAL    DEFAULT 0
);
"""

_POLLUTION_TABLE = """
CREATE TABLE IF NOT EXISTS pollution_log (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp      TEXT    NOT NULL,
    lat            REAL   NOT NULL,
    lng            REAL   NOT NULL,
    aqi            REAL   DEFAULT 0,
    noise_db       REAL   DEFAULT 0,
    vehicle_count  INTEGER DEFAULT 0
);
"""


async def get_db() -> aiosqlite.Connection:
    """Return an open async SQLite connection."""
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    return db


async def init_db() -> None:
    """Create tables if they don't exist."""
    db = await get_db()
    try:
        await db.execute(_TRAFFIC_TABLE)
        await db.execute(_POLLUTION_TABLE)
        await db.commit()
    finally:
        await db.close()
