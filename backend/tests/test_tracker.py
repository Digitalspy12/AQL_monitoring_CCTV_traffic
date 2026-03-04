"""
Tests for the centroid tracker.
"""

import pytest
from app.ai.tracker import CentroidTracker


class TestCentroidTracker:
    def setup_method(self):
        self.tracker = CentroidTracker(max_disappeared=5, max_distance=50)

    def test_register_first_detection(self):
        dets = [{"bbox": [10, 10, 50, 50], "class_name": "car"}]
        tracked = self.tracker.update(dets)
        assert len(tracked) == 1
        assert self.tracker.total_counted == 1

    def test_track_across_frames(self):
        dets1 = [{"bbox": [10, 10, 50, 50], "class_name": "car"}]
        dets2 = [{"bbox": [12, 12, 52, 52], "class_name": "car"}]  # slight movement

        self.tracker.update(dets1)
        tracked = self.tracker.update(dets2)

        # Should still be the same object (1 total), not 2
        assert self.tracker.total_counted == 1
        assert len(tracked) == 1

    def test_new_object_detected(self):
        dets1 = [{"bbox": [10, 10, 50, 50], "class_name": "car"}]
        dets2 = [
            {"bbox": [12, 12, 52, 52], "class_name": "car"},
            {"bbox": [200, 200, 250, 250], "class_name": "bus"},  # new object
        ]

        self.tracker.update(dets1)
        self.tracker.update(dets2)
        assert self.tracker.total_counted == 2

    def test_disappeared_object(self):
        dets = [{"bbox": [10, 10, 50, 50], "class_name": "car"}]
        self.tracker.update(dets)

        # No detections for max_disappeared + 1 frames
        for _ in range(6):
            self.tracker.update([])

        # Object should be deregistered, but total_counted stays
        assert self.tracker.total_counted == 1

    def test_empty_input(self):
        tracked = self.tracker.update([])
        assert tracked == {}
        assert self.tracker.total_counted == 0

    def test_reset(self):
        dets = [{"bbox": [10, 10, 50, 50], "class_name": "car"}]
        self.tracker.update(dets)
        self.tracker.reset()
        assert self.tracker.total_counted == 0
