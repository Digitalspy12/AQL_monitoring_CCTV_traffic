"""
Simple centroid-based object tracker.

Assigns persistent IDs to detected vehicles across frames to avoid
double-counting the same vehicle in consecutive frames.
"""

from __future__ import annotations

import math
from collections import OrderedDict
from typing import Any


class CentroidTracker:
    """
    Tracks objects by matching centroids between frames.

    Parameters
    ----------
    max_disappeared : int
        Number of consecutive frames an object can be missing before
        it is deregistered.
    max_distance : float
        Maximum pixel distance to consider a match.
    """

    def __init__(self, max_disappeared: int = 30, max_distance: float = 80.0):
        self._next_id = 0
        self._objects: OrderedDict[int, tuple[float, float]] = OrderedDict()
        self._disappeared: dict[int, int] = {}
        self._max_disappeared = max_disappeared
        self._max_distance = max_distance

        # Running total of unique objects that were registered
        self.total_counted: int = 0

    # ── Internal helpers ───────────────────────────────────────────────

    def _register(self, centroid: tuple[float, float]) -> int:
        obj_id = self._next_id
        self._objects[obj_id] = centroid
        self._disappeared[obj_id] = 0
        self._next_id += 1
        self.total_counted += 1
        return obj_id

    def _deregister(self, obj_id: int) -> None:
        del self._objects[obj_id]
        del self._disappeared[obj_id]

    @staticmethod
    def _centroid(bbox: list[float]) -> tuple[float, float]:
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    @staticmethod
    def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    # ── Public ─────────────────────────────────────────────────────────

    def update(self, detections: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
        """
        Accept new detections and return a dict mapping object IDs →
        detection dicts (with an extra "object_id" key injected).

        Parameters
        ----------
        detections : list[dict]
            Each dict must have a ``"bbox"`` key with ``[x1, y1, x2, y2]``.

        Returns
        -------
        dict[int, dict]
            Currently tracked objects keyed by ID.
        """
        # If no detections, mark all existing objects as disappeared
        if not detections:
            for obj_id in list(self._disappeared):
                self._disappeared[obj_id] += 1
                if self._disappeared[obj_id] > self._max_disappeared:
                    self._deregister(obj_id)
            return {}

        input_centroids = [self._centroid(d["bbox"]) for d in detections]

        # First frame — register everything
        if not self._objects:
            tracked: dict[int, dict[str, Any]] = {}
            for i, det in enumerate(detections):
                obj_id = self._register(input_centroids[i])
                det["object_id"] = obj_id
                tracked[obj_id] = det
            return tracked

        # Match existing objects to new centroids (greedy nearest)
        obj_ids = list(self._objects.keys())
        obj_centroids = list(self._objects.values())

        # Build distance matrix
        used_det: set[int] = set()
        used_obj: set[int] = set()
        tracked = {}

        # Sort all pairs by distance
        pairs = []
        for oi, oc in enumerate(obj_centroids):
            for di, dc in enumerate(input_centroids):
                pairs.append((self._dist(oc, dc), oi, di))
        pairs.sort()

        for dist, oi, di in pairs:
            if oi in used_obj or di in used_det:
                continue
            if dist > self._max_distance:
                break
            obj_id = obj_ids[oi]
            self._objects[obj_id] = input_centroids[di]
            self._disappeared[obj_id] = 0
            detections[di]["object_id"] = obj_id
            tracked[obj_id] = detections[di]
            used_obj.add(oi)
            used_det.add(di)

        # Increment disappeared for unmatched existing objects
        for oi in range(len(obj_ids)):
            if oi not in used_obj:
                obj_id = obj_ids[oi]
                self._disappeared[obj_id] += 1
                if self._disappeared[obj_id] > self._max_disappeared:
                    self._deregister(obj_id)

        # Register new detections that didn't match
        for di in range(len(detections)):
            if di not in used_det:
                obj_id = self._register(input_centroids[di])
                detections[di]["object_id"] = obj_id
                tracked[obj_id] = detections[di]

        return tracked

    def reset(self) -> None:
        """Clear all tracked objects and counters."""
        self._objects.clear()
        self._disappeared.clear()
        self._next_id = 0
        self.total_counted = 0
