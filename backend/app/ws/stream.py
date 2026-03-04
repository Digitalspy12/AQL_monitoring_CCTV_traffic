"""
WebSocket endpoint that streams live detection + pollution data.

The processing loop runs in a background thread so it doesn't
block the async event loop, then data is pushed to all connected
WebSocket clients.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import time
from datetime import datetime, timezone
from threading import Thread
from typing import Any

import cv2
import numpy as np

from app.ai.detector import annotate_frame, count_by_class, detect_vehicles
from app.ai.pollution import (
    aqi_category,
    estimate_aqi,
    estimate_noise,
    generate_heatmap_points,
)
from app.ai.tracker import CentroidTracker
from app.config import FRAME_SKIP, TARGET_FPS, VIDEO_SOURCE, WS_PUSH_INTERVAL
from app.db.crud import insert_pollution, insert_traffic

logger = logging.getLogger(__name__)

# ── Shared state ───────────────────────────────────────────────────────
_latest_payload: dict[str, Any] = {}
_clients: set[asyncio.Queue] = set()
_processing = False
_thread: Thread | None = None


def _frame_to_base64(frame: np.ndarray, quality: int = 60) -> str:
    """Encode a BGR frame as base64 JPEG."""
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf.tobytes()).decode("ascii")


def _process_video_loop() -> None:
    """
    Blocking loop: read video → detect → track → estimate pollution
    → publish payload. Runs in a daemon thread.
    """
    global _latest_payload, _processing

    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        logger.error("Cannot open video source: %s", VIDEO_SOURCE)
        _processing = False
        return

    tracker = CentroidTracker(max_disappeared=40, max_distance=90)
    frame_idx = 0
    fps_timer = time.time()
    fps_count = 0
    current_fps = 0.0

    logger.info("Video processing started — source: %s", VIDEO_SOURCE)

    while _processing:
        ret, frame = cap.read()
        if not ret:
            # Loop video
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            tracker.reset()
            continue

        frame_idx += 1
        if frame_idx % FRAME_SKIP != 0:
            continue

        # ── Detection ──────────────────────────────────────────────
        detections = detect_vehicles(frame)
        tracked = tracker.update(detections)
        counts = count_by_class(detections)
        total = sum(counts.values())

        # FPS calculation
        fps_count += 1
        elapsed = time.time() - fps_timer
        if elapsed >= 1.0:
            current_fps = round(fps_count / elapsed, 1)
            fps_count = 0
            fps_timer = time.time()

        # ── Annotated frame ────────────────────────────────────────
        annotated = annotate_frame(frame, detections)
        frame_b64 = _frame_to_base64(annotated)

        # ── Pollution ──────────────────────────────────────────────
        aqi = estimate_aqi(counts)
        noise = estimate_noise(total)
        category = aqi_category(aqi)
        heatmap = generate_heatmap_points(counts)

        now = datetime.now(timezone.utc).isoformat()

        _latest_payload = {
            "type": "live_update",
            "timestamp": now,
            "traffic": {
                "detections": detections,
                "counts": counts,
                "total": total,
                "fps": current_fps,
            },
            "pollution": {
                "aqi": aqi,
                "noise_db": noise,
                "category": category,
                "heatmap_points": heatmap,
            },
            "frame": frame_b64,
        }

        # Persist to DB periodically (every 5 seconds)
        if frame_idx % (TARGET_FPS * 5) == 0:
            asyncio.run(_persist(counts, current_fps, aqi, noise, total, heatmap))

        # Rate-limit pushes
        time.sleep(max(0, WS_PUSH_INTERVAL - 0.01))

    cap.release()
    logger.info("Video processing stopped.")


async def _persist(
    counts: dict[str, int],
    fps: float,
    aqi: float,
    noise: float,
    total: int,
    heatmap: list[dict],
) -> None:
    """Write data to the database."""
    try:
        await insert_traffic(counts, fps)
        if heatmap:
            pt = heatmap[0]
            await insert_pollution(pt["lat"], pt["lng"], aqi, noise, total)
    except Exception as exc:
        logger.warning("DB write error: %s", exc)


# ── Public helpers ─────────────────────────────────────────────────────

def start_processing() -> None:
    """Start video processing in a background thread."""
    global _processing, _thread
    if _processing:
        return
    _processing = True
    _thread = Thread(target=_process_video_loop, daemon=True)
    _thread.start()


def stop_processing() -> None:
    """Signal the processing thread to stop."""
    global _processing
    _processing = False


def get_latest_payload() -> dict[str, Any]:
    """Return the most recent payload snapshot."""
    return _latest_payload


def register_client() -> asyncio.Queue:
    """Register a new WS client and return its queue."""
    q: asyncio.Queue = asyncio.Queue(maxsize=5)
    _clients.add(q)
    return q


def unregister_client(q: asyncio.Queue) -> None:
    """Remove a WS client queue."""
    _clients.discard(q)


async def broadcast_loop() -> None:
    """Continuously push latest payload to all client queues."""
    last_ts = ""
    while True:
        payload = _latest_payload
        ts = payload.get("timestamp", "")
        if ts and ts != last_ts:
            last_ts = ts
            dead: list[asyncio.Queue] = []
            for q in _clients:
                try:
                    q.put_nowait(payload)
                except asyncio.QueueFull:
                    pass
                except Exception:
                    dead.append(q)
            for q in dead:
                _clients.discard(q)
        await asyncio.sleep(WS_PUSH_INTERVAL)
