"""
Tests for the Weather Structured FastAPI MCP Server.

Comprehensive tests for Pydantic model validation, structured output handling,
FastAPI endpoint integration, and MCP protocol support.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from weather_structured import (
    app,
    mcp,
    WeatherData,
    DailyStats,
    WeatherStats,
    API_KEY,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def client():
    """Create FastAPI TestClient for all tests."""
    return TestClient(app)


@pytest.fixture
def valid_api_key():
    """Provide valid API key for authenticated endpoints."""
    return API_KEY


@pytest.fixture
def auth_headers(valid_api_key):
    """Provide authorization headers for authenticated requests."""
    return {"X-API-Key": valid_api_key}


# ============================================================================
# Model Tests
# ============================================================================

class TestWeatherDataModel:
    """Tests for the WeatherData Pydantic model."""

    def test_weather_data_valid_creation(self):
        """Test creating valid WeatherData."""
        data = WeatherData(
            temperature=22.5,
            humidity=65.0,
            condition="partly cloudy",
            wind_speed=12.3,
            location="London"
        )

        assert data.temperature == 22.5
        assert data.humidity == 65.0
        assert data.condition == "partly cloudy"
        assert data.wind_speed == 12.3
        assert data.location == "London"
        assert isinstance(data.timestamp, datetime)

    def test_weather_data_default_timestamp(self):
        """Test WeatherData has default timestamp."""
        data = WeatherData(
            temperature=20.0,
            humidity=50.0,
            condition="sunny",
            wind_speed=5.0,
            location="Paris"
        )
        assert data.timestamp is not None

    def test_weather_data_json_serialization(self):
        """Test WeatherData can be converted to dict for JSON."""
        data = WeatherData(
            temperature=22.5,
            humidity=65.0,
            condition="cloudy",
            wind_speed=10.0,
            location="Berlin"
        )
        data_dict = data.model_dump()
        assert "temperature" in data_dict
        assert "location" in data_dict
        assert data_dict["temperature"] == 22.5


class TestDailyStatsModel:
    """Tests for the DailyStats model."""

    def test_daily_stats_valid_creation(self):
        """Test creating valid DailyStats."""
        stats = DailyStats(high=28.5, low=15.2, mean=21.8)

        assert stats.high == 28.5
        assert stats.low == 15.2
        assert stats.mean == 21.8

    def test_daily_stats_consistency(self):
        """Test DailyStats values have reasonable relationships."""
        stats = DailyStats(high=30.0, low=10.0, mean=20.0)

        assert stats.high >= stats.mean
        assert stats.mean >= stats.low


class TestWeatherStatsModel:
    """Tests for the WeatherStats model."""

    def test_weather_stats_valid_creation(self):
        """Test creating valid WeatherStats."""
        stats = WeatherStats(
            location="Seattle",
            period_days=7,
            temperature=DailyStats(high=25.0, low=15.0, mean=20.0),
            humidity=DailyStats(high=85.0, low=45.0, mean=65.0),
            precipitation_mm=12.4
        )

        assert stats.location == "Seattle"
        assert stats.period_days == 7
        assert isinstance(stats.temperature, DailyStats)
        assert isinstance(stats.humidity, DailyStats)
        assert stats.precipitation_mm == 12.4


# ============================================================================
# Service Endpoint Tests
# ============================================================================

class TestServiceEndpoints:
    """Tests for public service information endpoints."""

    def test_get_root_endpoint(self, client):
        """Test GET / returns server information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
        assert "endpoints" in data
        assert isinstance(data["endpoints"], list)

    def test_health_check_endpoint(self, client):
        """Test GET /health returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


# ============================================================================
# Weather Tool Endpoint Tests
# ============================================================================

class TestWeatherEndpoint:
    """Tests for the /weather endpoint."""

    def test_get_weather_success(self, client):
        """Test POST /weather returns valid WeatherData."""
        response = client.post("/weather", params={"city": "London"})

        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "London"
        assert "temperature" in data
        assert "humidity" in data
        assert "condition" in data
        assert "wind_speed" in data
        assert "timestamp" in data

    def test_get_weather_different_cities(self, client):
        """Test /weather with different city names."""
        cities = ["London", "Paris", "Tokyo", "Sydney"]

        for city in cities:
            response = client.post("/weather", params={"city": city})
            assert response.status_code == 200
            data = response.json()
            assert data["location"] == city

    def test_get_weather_special_characters(self, client):
        """Test /weather with special characters in city name."""
        response = client.post("/weather", params={"city": "São Paulo"})
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "São Paulo"

    def test_get_weather_unicode_city_names(self, client):
        """Test /weather with Unicode city names."""
        response = client.post("/weather", params={"city": "北京"})
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "北京"


class TestWeatherSummaryEndpoint:
    """Tests for the /weather-summary endpoint."""

    def test_get_weather_summary_success(self, client):
        """Test POST /weather-summary returns valid summary."""
        response = client.post("/weather-summary", params={"city": "Paris"})

        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Paris"
        assert "temp_c" in data
        assert "description" in data

    def test_get_weather_summary_structure(self, client):
        """Test WeatherSummary has all required fields."""
        response = client.post("/weather-summary", params={"city": "Berlin"})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["temp_c"], (int, float))
        assert isinstance(data["description"], str)


class TestWeatherMetricsEndpoint:
    """Tests for the /weather-metrics endpoint."""

    def test_get_weather_metrics_success(self, client):
        """Test /weather-metrics returns valid metrics."""
        response = client.post(
            "/weather-metrics",
            json={"cities": ["Tokyo", "Sydney", "Mumbai"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "Tokyo" in data
        assert "Sydney" in data
        assert "Mumbai" in data

    def test_get_weather_metrics_structure(self, client):
        """Test returned metrics have required fields."""
        response = client.post(
            "/weather-metrics",
            json={"cities": ["London"]}
        )

        assert response.status_code == 200
        data = response.json()
        metrics = data["London"]
        assert "temperature" in metrics
        assert "humidity" in metrics
        assert "pressure" in metrics


class TestWeatherAlertsEndpoint:
    """Tests for the /weather-alerts endpoint."""

    def test_get_weather_alerts_california(self, client):
        """Test /weather-alerts for California returns alerts."""
        response = client.post("/weather-alerts", params={"region": "California"})

        assert response.status_code == 200
        alerts = response.json()
        assert isinstance(alerts, list)
        assert len(alerts) > 0

        for alert in alerts:
            assert "severity" in alert
            assert "title" in alert
            assert "description" in alert
            assert "affected_areas" in alert

    def test_get_weather_alerts_no_region(self, client):
        """Test /weather-alerts for non-existent region returns empty list."""
        response = client.post("/weather-alerts", params={"region": "NonExistentRegion"})

        assert response.status_code == 200
        alerts = response.json()
        assert isinstance(alerts, list)
        assert len(alerts) == 0

    def test_get_weather_alerts_california_content(self, client):
        """Test California alerts have expected content."""
        response = client.post("/weather-alerts", params={"region": "California"})

        assert response.status_code == 200
        alerts = response.json()
        assert len(alerts) >= 2


class TestTemperatureEndpoint:
    """Tests for the /temperature endpoint."""

    def test_get_temperature_default_unit(self, client):
        """Test /temperature with default unit (celsius)."""
        response = client.post("/temperature", params={"city": "Berlin"})

        assert response.status_code == 200
        data = response.json()
        assert "temperature" in data
        assert "unit" in data
        assert "city" in data
        assert data["city"] == "Berlin"
        assert 20.0 <= data["temperature"] <= 25.0

    def test_get_temperature_fahrenheit(self, client):
        """Test /temperature with Fahrenheit unit."""
        response = client.post(
            "/temperature",
            params={"city": "Berlin", "unit": "fahrenheit"}
        )

        assert response.status_code == 200
        data = response.json()
        # 22.5°C ≈ 72.5°F
        assert 70.0 <= data["temperature"] <= 75.0
        assert data["unit"] == "fahrenheit"

    def test_get_temperature_case_insensitive(self, client):
        """Test /temperature unit parameter is case insensitive."""
        response_lower = client.post(
            "/temperature",
            params={"city": "Berlin", "unit": "celsius"}
        )
        response_upper = client.post(
            "/temperature",
            params={"city": "Berlin", "unit": "CELSIUS"}
        )

        assert response_lower.status_code == 200
        assert response_upper.status_code == 200
        assert response_lower.json()["temperature"] == response_upper.json()["temperature"]


class TestWeatherStatsEndpoint:
    """Tests for the /weather-stats endpoint."""

    def test_get_weather_stats_default_days(self, client):
        """Test /weather-stats with default days parameter."""
        response = client.post("/weather-stats", params={"city": "Seattle"})

        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Seattle"
        assert data["period_days"] == 7  # default

    def test_get_weather_stats_custom_days(self, client):
        """Test /weather-stats with custom days parameter."""
        response = client.post(
            "/weather-stats",
            params={"city": "Seattle", "days": 30}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Seattle"
        assert data["period_days"] == 30

    def test_get_weather_stats_has_nested_stats(self, client):
        """Test WeatherStats contains nested DailyStats."""
        response = client.post(
            "/weather-stats",
            params={"city": "Seattle", "days": 7}
        )

        assert response.status_code == 200
        data = response.json()
        assert "temperature" in data
        assert "humidity" in data
        assert "precipitation_mm" in data
        assert data["temperature"]["high"] > 0
        assert data["precipitation_mm"] >= 0

    def test_get_weather_stats_different_cities(self, client):
        """Test /weather-stats for different cities."""
        cities = ["Seattle", "London", "Tokyo"]

        for city in cities:
            response = client.post(
                "/weather-stats",
                params={"city": city, "days": 7}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["location"] == city


# ============================================================================
# MCP Integration Tests
# ============================================================================

class TestMCPIntegration:
    """Tests for MCP protocol integration."""

    def test_fastapi_mcp_instance_created(self):
        """Test that FastApiMCP instance is properly created."""
        assert mcp is not None
        # Verify it's a FastApiMCP instance
        assert type(mcp).__name__ == "FastApiMCP"

    def test_app_instance_created(self):
        """Test that FastAPI app is properly created."""
        assert app is not None
        assert hasattr(app, 'routes')


# ============================================================================
# Error Handling and Edge Cases
# ============================================================================

class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_weather_with_empty_city_name(self, client):
        """Test /weather with empty city name."""
        response = client.post("/weather", params={"city": ""})
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == ""

    def test_weather_summary_with_unicode(self, client):
        """Test /weather-summary with Unicode city names."""
        response = client.post("/weather-summary", params={"city": "中文"})
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "中文"

    def test_weather_metrics_with_empty_list(self, client):
        """Test /weather-metrics with empty cities list."""
        response = client.post("/weather-metrics", json={"cities": []})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 0

    def test_weather_stats_zero_days(self, client):
        """Test /weather-stats with zero days."""
        response = client.post(
            "/weather-stats",
            params={"city": "Seattle", "days": 0}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 0

    def test_weather_stats_large_days(self, client):
        """Test /weather-stats with large number of days."""
        response = client.post(
            "/weather-stats",
            params={"city": "Seattle", "days": 365}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 365


# ============================================================================
# Response Format Tests
# ============================================================================

class TestResponseFormats:
    """Tests for response format consistency and correctness."""

    def test_json_response_format(self, client):
        """Test all endpoints return valid JSON."""
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/weather", "POST"),
            ("/weather-summary", "POST"),
            ("/weather-metrics", "POST"),
            ("/weather-alerts", "POST"),
            ("/temperature", "POST"),
            ("/weather-stats", "POST"),
        ]

        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                # POST endpoints need parameters
                if endpoint == "/weather-metrics":
                    response = client.post(endpoint, json={"cities": ["Test"]})
                elif endpoint == "/weather-alerts":
                    response = client.post(endpoint, params={"region": "Test"})
                elif endpoint == "/weather-stats":
                    response = client.post(endpoint, params={"city": "Test"})
                else:
                    response = client.post(endpoint, params={"city": "Test"})

            assert response.status_code in [200, 422], f"Endpoint {endpoint} returned {response.status_code}"
            # Try to parse as JSON
            try:
                response.json()
            except ValueError:
                pytest.fail(f"Endpoint {endpoint} did not return valid JSON")

    def test_weather_response_includes_all_fields(self, client):
        """Test weather response includes all required fields."""
        response = client.post("/weather", params={"city": "London"})

        assert response.status_code == 200
        data = response.json()

        required_fields = ["temperature", "humidity", "condition", "wind_speed", "location", "timestamp"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

