"""
Application configuration — centralizes all settings.
"""

import os
from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "digitaltwin.db"
SAMPLE_VIDEO = BASE_DIR / "sample_videos" / "traffic_sample.mp4"

# Ensure data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── AI Model ───────────────────────────────────────────────────────────
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")  # auto-downloads on first run
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.35"))

# Vehicle COCO class IDs → readable labels
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

# ── Video Processing ──────────────────────────────────────────────────
VIDEO_SOURCE = os.getenv("VIDEO_SOURCE", str(SAMPLE_VIDEO))
FRAME_SKIP = int(os.getenv("FRAME_SKIP", "2"))  # process every Nth frame
TARGET_FPS = int(os.getenv("TARGET_FPS", "15"))

# ── Map / Heatmap Defaults ────────────────────────────────────────────
# Default centre — New Delhi, India (change to your city)
DEFAULT_LAT = float(os.getenv("DEFAULT_LAT", "28.6139"))
DEFAULT_LNG = float(os.getenv("DEFAULT_LNG", "77.2090"))
MAP_ZOOM = int(os.getenv("MAP_ZOOM", "13"))

# ── Server ─────────────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
WS_PUSH_INTERVAL = float(os.getenv("WS_PUSH_INTERVAL", "1.0"))  # seconds
