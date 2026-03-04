"""
Pydantic schemas for API request/response models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Traffic ────────────────────────────────────────────────────────────

class VehicleDetection(BaseModel):
    """Single detected vehicle in a frame."""
    class_name: str = Field(..., examples=["car", "bus", "motorcycle"])
    confidence: float = Field(..., ge=0, le=1)
    bbox: list[float] = Field(..., description="[x1, y1, x2, y2]")


class TrafficSnapshot(BaseModel):
    """Aggregated counts for one time-slice."""
    timestamp: datetime
    car_count: int = 0
    bus_count: int = 0
    motorcycle_count: int = 0
    truck_count: int = 0
    total_count: int = 0
    fps: float = 0.0


class TrafficLive(BaseModel):
    """Payload pushed over WebSocket every tick."""
    timestamp: str
    detections: list[VehicleDetection] = []
    counts: dict[str, int] = {}
    total: int = 0
    fps: float = 0.0
    frame_base64: Optional[str] = None  # annotated frame as base64 JPEG


# ── Pollution ──────────────────────────────────────────────────────────

class PollutionReading(BaseModel):
    """Single pollution estimate tied to a location."""
    timestamp: datetime
    lat: float
    lng: float
    aqi: float = Field(..., ge=0, description="Estimated Air Quality Index")
    noise_db: float = Field(..., ge=0, description="Estimated noise in dB")
    vehicle_count: int = 0


class PollutionHeatmapPoint(BaseModel):
    """One point for the Leaflet heatmap layer."""
    lat: float
    lng: float
    intensity: float = Field(..., ge=0, le=1)


class PollutionLive(BaseModel):
    """Real-time pollution payload."""
    timestamp: str
    aqi: float
    noise_db: float
    category: str  # "Good", "Moderate", "Unhealthy", etc.
    heatmap_points: list[PollutionHeatmapPoint] = []


# ── Generic ────────────────────────────────────────────────────────────

class HealthCheck(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
