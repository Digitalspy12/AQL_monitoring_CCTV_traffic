"""
Tests for the pollution estimation module.
"""

import pytest
from app.ai.pollution import estimate_aqi, estimate_noise, aqi_category, generate_heatmap_points


class TestEstimateAQI:
    def test_zero_vehicles(self):
        assert estimate_aqi({}) == 0.0

    def test_single_car(self):
        aqi = estimate_aqi({"car": 1})
        assert 0 < aqi < 50  # should be low

    def test_heavy_traffic(self):
        aqi = estimate_aqi({"car": 50, "bus": 10, "truck": 5})
        assert aqi > 100  # should be significant

    def test_cap_at_500(self):
        aqi = estimate_aqi({"truck": 1000})
        assert aqi == 500.0

    def test_all_vehicle_types(self):
        aqi = estimate_aqi({"car": 5, "motorcycle": 3, "bus": 2, "truck": 1})
        assert aqi > 0


class TestEstimateNoise:
    def test_zero_vehicles(self):
        assert estimate_noise(0) == 40.0  # base ambient

    def test_some_vehicles(self):
        noise = estimate_noise(10)
        assert noise > 40.0  # above ambient
        assert noise < 130.0  # below cap

    def test_increases_with_count(self):
        low = estimate_noise(5)
        high = estimate_noise(50)
        assert high > low

    def test_cap_at_130(self):
        noise = estimate_noise(10**9)
        assert noise <= 130.0


class TestAQICategory:
    def test_good(self):
        assert aqi_category(25) == "Good"

    def test_moderate(self):
        assert aqi_category(75) == "Moderate"

    def test_unhealthy(self):
        assert aqi_category(175) == "Unhealthy"

    def test_hazardous(self):
        assert aqi_category(400) == "Hazardous"


class TestHeatmapPoints:
    def test_returns_correct_count(self):
        points = generate_heatmap_points({"car": 10}, num_points=8)
        assert len(points) == 8

    def test_point_structure(self):
        points = generate_heatmap_points({"car": 5})
        for p in points:
            assert "lat" in p
            assert "lng" in p
            assert "intensity" in p
            assert 0 <= p["intensity"] <= 1
