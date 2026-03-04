"""
YOLOv8 Nano vehicle detection pipeline.

Loads the model once and exposes a simple `detect(frame)` interface
that returns bounding boxes, class labels, and confidence scores.
"""

from __future__ import annotations

import logging
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO

from app.config import CONFIDENCE_THRESHOLD, VEHICLE_CLASSES, YOLO_MODEL

logger = logging.getLogger(__name__)

# ── Singleton model loader ─────────────────────────────────────────────

_model: YOLO | None = None


def _get_model() -> YOLO:
    """Lazy-load YOLOv8 Nano (downloads weights on first run)."""
    global _model
    if _model is None:
        logger.info("Loading YOLO model: %s", YOLO_MODEL)
        _model = YOLO(YOLO_MODEL)
        logger.info("YOLO model loaded successfully.")
    return _model


# ── Public API ─────────────────────────────────────────────────────────

def detect_vehicles(frame: np.ndarray) -> list[dict[str, Any]]:
    """
    Run YOLOv8 inference on a single BGR frame.

    Returns a list of detections:
        [
            {
                "class_id": 2,
                "class_name": "car",
                "confidence": 0.87,
                "bbox": [x1, y1, x2, y2],
            },
            ...
        ]
    Only vehicle classes defined in VEHICLE_CLASSES are returned.
    """
    model = _get_model()
    results = model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD)
    detections: list[dict[str, Any]] = []

    for result in results:
        boxes = result.boxes
        if boxes is None:
            continue

        for box in boxes:
            class_id = int(box.cls[0])
            if class_id not in VEHICLE_CLASSES:
                continue

            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append(
                {
                    "class_id": class_id,
                    "class_name": VEHICLE_CLASSES[class_id],
                    "confidence": round(conf, 3),
                    "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                }
            )

    return detections


def annotate_frame(
    frame: np.ndarray, detections: list[dict[str, Any]]
) -> np.ndarray:
    """
    Draw bounding boxes and labels on a copy of the frame.
    """
    annotated = frame.copy()
    colors = {
        "car": (0, 255, 0),
        "motorcycle": (255, 165, 0),
        "bus": (0, 100, 255),
        "truck": (255, 0, 0),
    }

    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        color = colors.get(det["class_name"], (255, 255, 255))
        label = f"{det['class_name']} {det['confidence']:.0%}"

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

        # Label background
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
        cv2.putText(
            annotated, label, (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA,
        )

    return annotated


def count_by_class(detections: list[dict[str, Any]]) -> dict[str, int]:
    """Aggregate detections into per-class counts."""
    counts: dict[str, int] = {}
    for det in detections:
        name = det["class_name"]
        counts[name] = counts.get(name, 0) + 1
    return counts
