"""
Pollution estimation models.

Estimates Air Quality Index (AQI) and noise levels from
real-time vehicle traffic counts using EPA-style emission
factors and logarithmic noise models.
"""

from __future__ import annotations

import math
import random

from app.config import DEFAULT_LAT, DEFAULT_LNG


# ── Emission factors (grams CO₂-equivalent per vehicle per minute) ──
_EMISSION_FACTORS: dict[str, float] = {
    "car": 4.6,
    "motorcycle": 2.3,
    "bus": 12.0,
    "truck": 15.0,
}

# ── AQI breakpoints (simplified EPA scale) ─────────────────────────
_AQI_BREAKPOINTS = [
    (0, 50, "Good"),
    (51, 100, "Moderate"),
    (101, 150, "Unhealthy for Sensitive Groups"),
    (151, 200, "Unhealthy"),
    (201, 300, "Very Unhealthy"),
    (301, 500, "Hazardous"),
]

# ── Noise constants ─────────────────────────────────────────────────
_BASE_AMBIENT_DB = 40.0   # quiet street
_DB_PER_VEHICLE = 3.0     # rough contribution


def estimate_aqi(counts: dict[str, int]) -> float:
    """
    Estimate AQI from vehicle counts using emission factors.

    This is a simplified model — real AQI requires pollutant
    concentration measurements. We scale linearly then cap at 500.
    """
    total_emissions = sum(
        counts.get(vtype, 0) * factor
        for vtype, factor in _EMISSION_FACTORS.items()
    )

    # Map emissions to a 0-500 AQI range (tuned for demo scale)
    aqi = min(500.0, total_emissions * 1.5)
    return round(aqi, 1)


def estimate_noise(total_vehicles: int) -> float:
    """
    Estimate noise in dB using a logarithmic model.

    noise = base + 10 × log₁₀(1 + count × k)
    """
    if total_vehicles <= 0:
        return _BASE_AMBIENT_DB
    noise = _BASE_AMBIENT_DB + 10 * math.log10(1 + total_vehicles * _DB_PER_VEHICLE)
    return round(min(noise, 130.0), 1)  # cap at 130 dB


def aqi_category(aqi: float) -> str:
    """Return the EPA category string for a given AQI value."""
    for low, high, label in _AQI_BREAKPOINTS:
        if low <= aqi <= high:
            return label
    return "Hazardous"


def generate_heatmap_points(
    counts: dict[str, int],
    center_lat: float = DEFAULT_LAT,
    center_lng: float = DEFAULT_LNG,
    num_points: int = 12,
) -> list[dict[str, float]]:
    """
    Generate synthetic heatmap points around a centre coordinate.

    In a real deployment these coordinates would come from
    geo-tagged camera feeds. For demo purposes we scatter
    points within a small radius and assign intensity based on
    estimated pollution.
    """
    total = sum(counts.values())
    aqi = estimate_aqi(counts)
    # Normalise intensity to 0-1
    intensity = min(1.0, aqi / 300.0)

    points: list[dict[str, float]] = []
    for _ in range(num_points):
        # Spread within ~0.02 degrees (~2 km)
        lat = center_lat + random.uniform(-0.015, 0.015)
        lng = center_lng + random.uniform(-0.015, 0.015)
        # Add some per-point noise
        pt_intensity = max(0.0, min(1.0, intensity + random.uniform(-0.15, 0.15)))
        points.append({"lat": round(lat, 6), "lng": round(lng, 6), "intensity": round(pt_intensity, 3)})

    return points
