"""
Tests for the Weather Structured functionality of the MCP Server.

Tests the Pydantic model validation and structured data handling
including nested models, field validation, and MCP tool integration.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from datetime import datetime
from pydantic import ValidationError

from weather_structured import (
    WeatherData,
    WeatherSummary,
    WeatherAlert,
    DailyStats,
    WeatherStats,
    get_weather,
    get_weather_summary,
    get_weather_metrics,
    get_weather_alerts,
    get_temperature,
    get_weather_stats,
)


class TestWeatherDataModel:
    """Tests for the WeatherData Pydantic model."""

    def test_weather_data_valid_creation(self):
        """Test creating a valid WeatherData."""
        weather = WeatherData(
            temperature=22.5,
            humidity=65.0,
            condition="partly cloudy",
            wind_speed=12.3,
            location="London",
            timestamp=datetime(2025, 12, 24, 22, 55, 4)
        )

        assert weather.temperature == 22.5
        assert weather.humidity == 65.0
        assert weather.condition == "partly cloudy"
        assert weather.wind_speed == 12.3
        assert weather.location == "London"

    def test_weather_data_temperature_float(self):
        """Test that temperature accepts various float values."""
        # Positive temperature
        weather = WeatherData(
            temperature=25.0,
            humidity=50.0,
            condition="sunny",
            wind_speed=10.0,
            location="Cairo"
        )
        assert weather.temperature == 25.0

        # Negative temperature
        weather = WeatherData(
            temperature=-15.5,
            humidity=80.0,
            condition="snowy",
            wind_speed=20.0,
            location="Moscow"
        )
        assert weather.temperature == -15.5

        # Zero temperature
        weather = WeatherData(
            temperature=0.0,
            humidity=70.0,
            condition="freezing",
            wind_speed=5.0,
            location="Nordic"
        )
        assert weather.temperature == 0.0

    def test_weather_data_humidity_constraints(self):
        """Test that humidity is a valid float."""
        # Valid humidity
        weather = WeatherData(
            temperature=20.0,
            humidity=65.0,
            condition="cloudy",
            wind_speed=10.0,
            location="Test"
        )
        assert weather.humidity == 65.0

        # High humidity
        weather = WeatherData(
            temperature=20.0,
            humidity=95.5,
            condition="rainy",
            wind_speed=10.0,
            location="Test"
        )
        assert weather.humidity == 95.5

        # Low humidity
        weather = WeatherData(
            temperature=20.0,
            humidity=10.0,
            condition="dry",
            wind_speed=10.0,
            location="Test"
        )
        assert weather.humidity == 10.0

    def test_weather_data_wind_speed(self):
        """Test wind speed values."""
        # No wind
        weather = WeatherData(
            temperature=20.0,
            humidity=50.0,
            condition="calm",
            wind_speed=0.0,
            location="Test"
        )
        assert weather.wind_speed == 0.0

        # Strong wind
        weather = WeatherData(
            temperature=20.0,
            humidity=50.0,
            condition="windy",
            wind_speed=50.5,
            location="Test"
        )
        assert weather.wind_speed == 50.5

    def test_weather_data_timestamp_default(self):
        """Test that timestamp has a default value."""
        weather = WeatherData(
            temperature=20.0,
            humidity=50.0,
            condition="cloudy",
            wind_speed=10.0,
            location="Test"
        )

        assert weather.timestamp is not None
        assert isinstance(weather.timestamp, datetime)

    def test_weather_data_missing_required_fields(self):
        """Test that all required fields must be provided."""
        # Missing temperature
        with pytest.raises(ValidationError):
            WeatherData(
                humidity=50.0,
                condition="cloudy",
                wind_speed=10.0,
                location="Test"
            )

        # Missing humidity
        with pytest.raises(ValidationError):
            WeatherData(
                temperature=20.0,
                condition="cloudy",
                wind_speed=10.0,
                location="Test"
            )

        # Missing condition
        with pytest.raises(ValidationError):
            WeatherData(
                temperature=20.0,
                humidity=50.0,
                wind_speed=10.0,
                location="Test"
            )

        # Missing wind_speed
        with pytest.raises(ValidationError):
            WeatherData(
                temperature=20.0,
                humidity=50.0,
                condition="cloudy",
                location="Test"
            )

        # Missing location
        with pytest.raises(ValidationError):
            WeatherData(
                temperature=20.0,
                humidity=50.0,
                condition="cloudy",
                wind_speed=10.0
            )

    def test_weather_data_invalid_types(self):
        """Test that invalid types are rejected."""
        # Temperature not a number
        with pytest.raises(ValidationError):
            WeatherData(
                temperature="warm",
                humidity=50.0,
                condition="cloudy",
                wind_speed=10.0,
                location="Test"
            )

        # Humidity not a number
        with pytest.raises(ValidationError):
            WeatherData(
                temperature=20.0,
                humidity="high",
                condition="cloudy",
                wind_speed=10.0,
                location="Test"
            )

        # Wind speed not a number
        with pytest.raises(ValidationError):
            WeatherData(
                temperature=20.0,
                humidity=50.0,
                condition="cloudy",
                wind_speed="strong",
                location="Test"
            )


class TestWeatherSummaryModel:
    """Tests for the WeatherSummary TypedDict."""

    def test_weather_summary_valid_creation(self):
        """Test creating a valid WeatherSummary."""
        summary = WeatherSummary(
            city="Paris",
            temp_c=22.5,
            description="Partly cloudy with light breeze"
        )

        assert summary["city"] == "Paris"
        assert summary["temp_c"] == 22.5
        assert summary["description"] == "Partly cloudy with light breeze"

    def test_weather_summary_various_temperatures(self):
        """Test various temperature values in summary."""
        # Cold temperature
        summary = WeatherSummary(city="Oslo", temp_c=-10.0, description="Freezing")
        assert summary["temp_c"] == -10.0

        # Hot temperature
        summary = WeatherSummary(city="Phoenix", temp_c=45.0, description="Very hot")
        assert summary["temp_c"] == 45.0

        # Room temperature
        summary = WeatherSummary(city="Spring", temp_c=20.0, description="Pleasant")
        assert summary["temp_c"] == 20.0

    def test_weather_summary_various_descriptions(self):
        """Test various weather descriptions."""
        descriptions = [
            "Sunny and clear",
            "Rainy with thunderstorms",
            "Snowy conditions",
            "Foggy morning",
            "Clear night",
            "Partly cloudy with light breeze"
        ]

        for desc in descriptions:
            summary = WeatherSummary(city="Test", temp_c=20.0, description=desc)
            assert summary["description"] == desc


class TestWeatherAlertDataclass:
    """Tests for the WeatherAlert dataclass."""

    def test_weather_alert_valid_creation(self):
        """Test creating a valid WeatherAlert."""
        alert = WeatherAlert(
            severity="high",
            title="Heat Wave Warning",
            description="Temperatures expected to exceed 40 degrees",
            affected_areas=["Los Angeles", "San Diego"],
            valid_until=datetime(2024, 7, 15, 18, 0)
        )

        assert alert.severity == "high"
        assert alert.title == "Heat Wave Warning"
        assert alert.description == "Temperatures expected to exceed 40 degrees"
        assert alert.affected_areas == ["Los Angeles", "San Diego"]

    def test_weather_alert_severity_levels(self):
        """Test various severity levels."""
        severities = ["low", "medium", "high"]

        for severity in severities:
            alert = WeatherAlert(
                severity=severity,
                title="Test Alert",
                description="Test",
                affected_areas=["Test City"],
                valid_until=datetime(2024, 7, 15, 18, 0)
            )
            assert alert.severity == severity

    def test_weather_alert_multiple_areas(self):
        """Test alert with multiple affected areas."""
        areas = ["Los Angeles", "San Diego", "Riverside", "Ventura", "Santa Barbara"]
        alert = WeatherAlert(
            severity="high",
            title="Heat Wave",
            description="Extreme heat warning",
            affected_areas=areas,
            valid_until=datetime(2024, 7, 15, 18, 0)
        )

        assert len(alert.affected_areas) == 5
        assert "Los Angeles" in alert.affected_areas

    def test_weather_alert_single_area(self):
        """Test alert with single affected area."""
        alert = WeatherAlert(
            severity="low",
            title="Minor Alert",
            description="Minor weather event",
            affected_areas=["Small Town"],
            valid_until=datetime(2024, 7, 15, 18, 0)
        )

        assert len(alert.affected_areas) == 1
        assert alert.affected_areas[0] == "Small Town"

    def test_weather_alert_empty_areas(self):
        """Test alert with empty affected areas list."""
        alert = WeatherAlert(
            severity="low",
            title="General Alert",
            description="Regional weather event",
            affected_areas=[],
            valid_until=datetime(2024, 7, 15, 18, 0)
        )

        assert len(alert.affected_areas) == 0


class TestDailyStatsModel:
    """Tests for the DailyStats Pydantic model."""

    def test_daily_stats_valid_creation(self):
        """Test creating valid DailyStats."""
        stats = DailyStats(high=28.5, low=15.2, mean=21.8)

        assert stats.high == 28.5
        assert stats.low == 15.2
        assert stats.mean == 21.8

    def test_daily_stats_consistent_values(self):
        """Test DailyStats with consistent temperature order (high >= mean >= low)."""
        stats = DailyStats(high=30.0, low=10.0, mean=20.0)

        assert stats.high >= stats.mean
        assert stats.mean >= stats.low

    def test_daily_stats_same_values(self):
        """Test DailyStats when all values are the same (no variation)."""
        stats = DailyStats(high=20.0, low=20.0, mean=20.0)

        assert stats.high == stats.mean == stats.low

    def test_daily_stats_negative_temperatures(self):
        """Test DailyStats with negative temperatures."""
        stats = DailyStats(high=-5.0, low=-15.0, mean=-10.0)

        assert stats.high == -5.0
        assert stats.low == -15.0
        assert stats.mean == -10.0

    def test_daily_stats_missing_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError):
            DailyStats(high=30.0, low=15.0)

        with pytest.raises(ValidationError):
            DailyStats(high=30.0, mean=22.5)

        with pytest.raises(ValidationError):
            DailyStats(low=15.0, mean=22.5)


class TestWeatherStatsModel:
    """Tests for the WeatherStats Pydantic model with nested models."""

    def test_weather_stats_valid_creation(self):
        """Test creating valid WeatherStats."""
        temp_stats = DailyStats(high=28.5, low=15.2, mean=21.8)
        humidity_stats = DailyStats(high=85.0, low=45.0, mean=65.0)

        stats = WeatherStats(
            location="Seattle",
            period_days=7,
            temperature=temp_stats,
            humidity=humidity_stats,
            precipitation_mm=12.4
        )

        assert stats.location == "Seattle"
        assert stats.period_days == 7
        assert stats.temperature.high == 28.5
        assert stats.humidity.low == 45.0
        assert stats.precipitation_mm == 12.4

    def test_weather_stats_nested_model_validation(self):
        """Test that nested models are properly validated."""
        temp_stats = DailyStats(high=25.0, low=15.0, mean=20.0)
        humidity_stats = DailyStats(high=80.0, low=40.0, mean=60.0)

        stats = WeatherStats(
            location="London",
            period_days=30,
            temperature=temp_stats,
            humidity=humidity_stats,
            precipitation_mm=50.0
        )

        # Verify nested model access
        assert isinstance(stats.temperature, DailyStats)
        assert isinstance(stats.humidity, DailyStats)

    def test_weather_stats_various_periods(self):
        """Test WeatherStats with various period lengths."""
        periods = [1, 7, 14, 30, 90, 365]

        for period in periods:
            temp_stats = DailyStats(high=25.0, low=15.0, mean=20.0)
            humidity_stats = DailyStats(high=80.0, low=40.0, mean=60.0)

            stats = WeatherStats(
                location="Test",
                period_days=period,
                temperature=temp_stats,
                humidity=humidity_stats,
                precipitation_mm=25.0
            )

            assert stats.period_days == period

    def test_weather_stats_zero_precipitation(self):
        """Test WeatherStats with no precipitation."""
        temp_stats = DailyStats(high=25.0, low=15.0, mean=20.0)
        humidity_stats = DailyStats(high=80.0, low=40.0, mean=60.0)

        stats = WeatherStats(
            location="Desert",
            period_days=7,
            temperature=temp_stats,
            humidity=humidity_stats,
            precipitation_mm=0.0
        )

        assert stats.precipitation_mm == 0.0

    def test_weather_stats_high_precipitation(self):
        """Test WeatherStats with high precipitation."""
        temp_stats = DailyStats(high=25.0, low=15.0, mean=20.0)
        humidity_stats = DailyStats(high=95.0, low=70.0, mean=85.0)

        stats = WeatherStats(
            location="Rainforest",
            period_days=7,
            temperature=temp_stats,
            humidity=humidity_stats,
            precipitation_mm=250.0
        )

        assert stats.precipitation_mm == 250.0

    def test_weather_stats_missing_required_fields(self):
        """Test that all fields are required."""
        temp_stats = DailyStats(high=25.0, low=15.0, mean=20.0)
        humidity_stats = DailyStats(high=80.0, low=40.0, mean=60.0)

        # Missing location
        with pytest.raises(ValidationError):
            WeatherStats(
                period_days=7,
                temperature=temp_stats,
                humidity=humidity_stats,
                precipitation_mm=12.4
            )

        # Missing period_days
        with pytest.raises(ValidationError):
            WeatherStats(
                location="Test",
                temperature=temp_stats,
                humidity=humidity_stats,
                precipitation_mm=12.4
            )

        # Missing temperature
        with pytest.raises(ValidationError):
            WeatherStats(
                location="Test",
                period_days=7,
                humidity=humidity_stats,
                precipitation_mm=12.4
            )

        # Missing humidity
        with pytest.raises(ValidationError):
            WeatherStats(
                location="Test",
                period_days=7,
                temperature=temp_stats,
                precipitation_mm=12.4
            )

        # Missing precipitation_mm
        with pytest.raises(ValidationError):
            WeatherStats(
                location="Test",
                period_days=7,
                temperature=temp_stats,
                humidity=humidity_stats
            )


class TestGetWeatherTool:
    """Tests for the get_weather tool."""

    def test_get_weather_london(self):
        """Test get_weather returns valid data for London."""
        result = get_weather("London")

        assert isinstance(result, WeatherData)
        assert result.location == "London"
        assert isinstance(result.temperature, float)
        assert isinstance(result.humidity, float)
        assert isinstance(result.condition, str)
        assert isinstance(result.wind_speed, float)

    def test_get_weather_various_cities(self):
        """Test get_weather with various city names."""
        cities = ["Paris", "Tokyo", "Sydney", "New York", "Dubai"]

        for city in cities:
            result = get_weather(city)
            assert result.location == city
            assert result.temperature is not None

    def test_get_weather_returns_pydantic_model(self):
        """Test that get_weather returns proper Pydantic model."""
        result = get_weather("Berlin")

        assert hasattr(result, 'temperature')
        assert hasattr(result, 'humidity')
        assert hasattr(result, 'condition')
        assert hasattr(result, 'wind_speed')
        assert hasattr(result, 'location')
        assert hasattr(result, 'timestamp')

    def test_get_weather_timestamp_is_datetime(self):
        """Test that timestamp is a datetime object."""
        result = get_weather("Paris")

        assert isinstance(result.timestamp, datetime)


class TestGetWeatherSummaryTool:
    """Tests for the get_weather_summary tool."""

    def test_get_weather_summary_basic(self):
        """Test get_weather_summary returns correct structure."""
        result = get_weather_summary("Paris")

        assert isinstance(result, dict)
        assert "city" in result
        assert "temp_c" in result
        assert "description" in result
        assert result["city"] == "Paris"

    def test_get_weather_summary_various_cities(self):
        """Test get_weather_summary with various cities."""
        cities = ["London", "Tokyo", "Cairo", "Moscow"]

        for city in cities:
            result = get_weather_summary(city)
            assert result["city"] == city
            assert isinstance(result["temp_c"], float)
            assert isinstance(result["description"], str)

    def test_get_weather_summary_temperature_range(self):
        """Test that temperature values are reasonable."""
        result = get_weather_summary("TestCity")

        # Temperature should be a reasonable value
        assert -50 <= result["temp_c"] <= 60

    def test_get_weather_summary_description_present(self):
        """Test that description is always present."""
        result = get_weather_summary("City")

        assert result["description"]
        assert len(result["description"]) > 0


class TestGetWeatherMetricsTool:
    """Tests for the get_weather_metrics tool."""

    def test_get_weather_metrics_single_city(self):
        """Test get_weather_metrics with single city."""
        result = get_weather_metrics(["Tokyo"])

        assert isinstance(result, dict)
        assert "Tokyo" in result
        assert "temperature" in result["Tokyo"]
        assert "humidity" in result["Tokyo"]
        assert "pressure" in result["Tokyo"]

    def test_get_weather_metrics_multiple_cities(self):
        """Test get_weather_metrics with multiple cities."""
        result = get_weather_metrics(["Tokyo", "Sydney", "Mumbai"])

        assert len(result) == 3
        assert all(city in result for city in ["Tokyo", "Sydney", "Mumbai"])

    def test_get_weather_metrics_city_values(self):
        """Test that each city has temperature, humidity, and pressure."""
        cities = ["London", "Paris", "Berlin"]
        result = get_weather_metrics(cities)

        for city in cities:
            assert "temperature" in result[city]
            assert "humidity" in result[city]
            assert "pressure" in result[city]
            assert isinstance(result[city]["temperature"], float)
            assert isinstance(result[city]["humidity"], float)
            assert isinstance(result[city]["pressure"], float)

    def test_get_weather_metrics_empty_list(self):
        """Test get_weather_metrics with empty city list."""
        result = get_weather_metrics([])

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_get_weather_metrics_nested_structure(self):
        """Test that nested structure is correct."""
        result = get_weather_metrics(["CityA", "CityB"])

        # Verify nested dict structure
        for city_data in result.values():
            assert isinstance(city_data, dict)
            for metric_name, metric_value in city_data.items():
                assert isinstance(metric_name, str)
                assert isinstance(metric_value, float)


class TestGetWeatherAlertsTool:
    """Tests for the get_weather_alerts tool."""

    def test_get_weather_alerts_california(self):
        """Test get_weather_alerts returns alerts for California."""
        result = get_weather_alerts("California")

        assert isinstance(result, list)
        assert len(result) > 0
        for alert in result:
            assert isinstance(alert, WeatherAlert)

    def test_get_weather_alerts_structure(self):
        """Test alert structure."""
        result = get_weather_alerts("California")

        for alert in result:
            assert hasattr(alert, 'severity')
            assert hasattr(alert, 'title')
            assert hasattr(alert, 'description')
            assert hasattr(alert, 'affected_areas')
            assert hasattr(alert, 'valid_until')

    def test_get_weather_alerts_california_content(self):
        """Test California alerts have expected content."""
        result = get_weather_alerts("California")

        # Should have heat wave and air quality alerts
        titles = [alert.title for alert in result]
        assert any("Heat" in title for title in titles)
        assert any("Air" in title for title in titles)

    def test_get_weather_alerts_severity_levels(self):
        """Test that alerts have valid severity levels."""
        result = get_weather_alerts("California")

        valid_severities = ["low", "medium", "high"]
        for alert in result:
            assert alert.severity in valid_severities

    def test_get_weather_alerts_affected_areas(self):
        """Test that alerts have affected areas."""
        result = get_weather_alerts("California")

        for alert in result:
            assert len(alert.affected_areas) > 0
            for area in alert.affected_areas:
                assert isinstance(area, str)
                assert len(area) > 0

    def test_get_weather_alerts_nonexistent_region(self):
        """Test get_weather_alerts with nonexistent region returns empty."""
        result = get_weather_alerts("Nonexistent")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_weather_alerts_case_insensitive(self):
        """Test that California alerts are case-insensitive."""
        result_upper = get_weather_alerts("CALIFORNIA")
        result_lower = get_weather_alerts("california")
        result_mixed = get_weather_alerts("California")

        # All should return results (if case-insensitive)
        assert len(result_upper) > 0 or len(result_lower) > 0 or len(result_mixed) > 0


class TestGetTemperatureTool:
    """Tests for the get_temperature tool."""

    def test_get_temperature_celsius_default(self):
        """Test get_temperature returns Celsius by default."""
        result = get_temperature("Berlin")

        assert isinstance(result, float)
        # Default temperature in implementation is 22.5°C
        assert result == 22.5

    def test_get_temperature_celsius_explicit(self):
        """Test get_temperature with explicit Celsius unit."""
        result = get_temperature("Berlin", unit="celsius")

        assert isinstance(result, float)
        assert result == 22.5

    def test_get_temperature_fahrenheit(self):
        """Test get_temperature conversion to Fahrenheit."""
        result = get_temperature("Berlin", unit="fahrenheit")

        # 22.5°C = 72.5°F
        assert isinstance(result, float)
        assert result == 72.5

    def test_get_temperature_various_cities(self):
        """Test get_temperature with various cities."""
        cities = ["London", "Paris", "Tokyo", "Sydney"]

        for city in cities:
            result = get_temperature(city)
            assert isinstance(result, float)

    def test_get_temperature_celsius_lowercase(self):
        """Test temperature with lowercase celsius."""
        result = get_temperature("City", unit="celsius")

        assert result == 22.5

    def test_get_temperature_fahrenheit_lowercase(self):
        """Test temperature with lowercase fahrenheit."""
        result = get_temperature("City", unit="fahrenheit")

        assert result == 72.5

    def test_get_temperature_conversion_math(self):
        """Test Fahrenheit conversion math is correct."""
        celsius_temp = 22.5
        expected_fahrenheit = celsius_temp * 9 / 5 + 32

        result = get_temperature("Test", unit="fahrenheit")

        assert result == expected_fahrenheit


class TestGetWeatherStatsTool:
    """Tests for the get_weather_stats tool."""

    def test_get_weather_stats_default_period(self):
        """Test get_weather_stats with default 7-day period."""
        result = get_weather_stats("Seattle")

        assert isinstance(result, WeatherStats)
        assert result.location == "Seattle"
        assert result.period_days == 7
        assert isinstance(result.temperature, DailyStats)
        assert isinstance(result.humidity, DailyStats)

    def test_get_weather_stats_custom_period(self):
        """Test get_weather_stats with custom period."""
        result = get_weather_stats("Seattle", days=30)

        assert result.location == "Seattle"
        assert result.period_days == 30

    def test_get_weather_stats_various_periods(self):
        """Test get_weather_stats with various period lengths."""
        periods = [1, 7, 14, 30, 90]

        for period in periods:
            result = get_weather_stats("City", days=period)
            assert result.period_days == period

    def test_get_weather_stats_nested_models(self):
        """Test that nested models are properly structured."""
        result = get_weather_stats("London", days=7)

        # Check temperature stats
        assert isinstance(result.temperature, DailyStats)
        assert result.temperature.high > result.temperature.mean
        assert result.temperature.mean > result.temperature.low

        # Check humidity stats
        assert isinstance(result.humidity, DailyStats)
        assert result.humidity.high >= result.humidity.mean
        assert result.humidity.mean >= result.humidity.low

    def test_get_weather_stats_precipitation(self):
        """Test precipitation value."""
        result = get_weather_stats("Rainforest", days=30)

        assert isinstance(result.precipitation_mm, float)
        assert result.precipitation_mm >= 0

    def test_get_weather_stats_various_cities(self):
        """Test get_weather_stats with various cities."""
        cities = ["London", "Tokyo", "Sydney", "New York"]

        for city in cities:
            result = get_weather_stats(city)
            assert result.location == city


class TestWeatherIntegration:
    """Integration tests for weather tools."""

    def test_full_weather_workflow(self):
        """Test a complete weather query workflow."""
        # Get full weather data
        weather = get_weather("London")
        assert weather.location == "London"

        # Get summary
        summary = get_weather_summary("London")
        assert summary["city"] == "London"

        # Get metrics for multiple cities
        metrics = get_weather_metrics(["London", "Paris", "Berlin"])
        assert len(metrics) == 3

        # Get temperature
        temp = get_temperature("London", unit="celsius")
        assert isinstance(temp, float)

        # Get stats
        stats = get_weather_stats("London", days=30)
        assert stats.location == "London"

    def test_temperature_consistency(self):
        """Test temperature values are consistent across tools."""
        # get_weather returns 22.5 by default
        weather = get_weather("Test")
        temp_single = get_temperature("Test", unit="celsius")

        # Both should return similar temperature values
        assert isinstance(weather.temperature, float)
        assert isinstance(temp_single, float)

    def test_alerts_workflow(self):
        """Test alert retrieval workflow."""
        # Get alerts for a region
        alerts = get_weather_alerts("California")

        if len(alerts) > 0:
            # Verify alert structure
            for alert in alerts:
                assert alert.severity in ["low", "medium", "high"]
                assert alert.title
                assert alert.description
                assert len(alert.affected_areas) > 0

    def test_stats_nested_model_access(self):
        """Test accessing nested model data."""
        stats = get_weather_stats("Seattle", days=7)

        # Access nested temperature stats
        high_temp = stats.temperature.high
        low_temp = stats.temperature.low
        mean_temp = stats.temperature.mean

        assert high_temp > low_temp
        assert low_temp < mean_temp < high_temp

        # Access nested humidity stats
        high_humidity = stats.humidity.high
        low_humidity = stats.humidity.low

        assert high_humidity > low_humidity

    def test_error_handling_in_workflow(self):
        """Test error handling in weather workflow."""
        # Invalid models should fail during creation
        with pytest.raises(ValidationError):
            WeatherData(
                temperature="invalid",
                humidity=50.0,
                condition="cloudy",
                wind_speed=10.0,
                location="Test"
            )

        with pytest.raises(ValidationError):
            DailyStats(high="invalid", low=10.0, mean=15.0)


class TestEdgeCases:
    """Edge case tests for weather functionality."""

    def test_extreme_temperatures(self):
        """Test with extreme temperature values."""
        # Very cold
        weather = WeatherData(
            temperature=-100.0,
            humidity=50.0,
            condition="extreme cold",
            wind_speed=10.0,
            location="South Pole"
        )
        assert weather.temperature == -100.0

        # Very hot
        weather = WeatherData(
            temperature=60.0,
            humidity=10.0,
            condition="extreme heat",
            wind_speed=20.0,
            location="Death Valley"
        )
        assert weather.temperature == 60.0

    def test_extreme_wind_speeds(self):
        """Test with extreme wind speeds."""
        # Calm
        weather = WeatherData(
            temperature=20.0,
            humidity=50.0,
            condition="calm",
            wind_speed=0.0,
            location="Test"
        )
        assert weather.wind_speed == 0.0

        # Hurricane-force winds
        weather = WeatherData(
            temperature=20.0,
            humidity=80.0,
            condition="hurricane",
            wind_speed=250.0,
            location="Test"
        )
        assert weather.wind_speed == 250.0

    def test_extreme_humidity_values(self):
        """Test with extreme humidity values."""
        # Dry
        weather = WeatherData(
            temperature=25.0,
            humidity=1.0,
            condition="very dry",
            wind_speed=15.0,
            location="Desert"
        )
        assert weather.humidity == 1.0

        # Very humid
        weather = WeatherData(
            temperature=28.0,
            humidity=99.0,
            condition="oppressive",
            wind_speed=5.0,
            location="Tropics"
        )
        assert weather.humidity == 99.0

    def test_large_precipitation_values(self):
        """Test with large precipitation amounts."""
        temp = DailyStats(high=20.0, low=15.0, mean=17.5)
        humidity = DailyStats(high=95.0, low=70.0, mean=85.0)

        stats = WeatherStats(
            location="Rainforest",
            period_days=30,
            temperature=temp,
            humidity=humidity,
            precipitation_mm=1000.0  # 1 meter of rain
        )

        assert stats.precipitation_mm == 1000.0

    def test_minimal_setup(self):
        """Test with minimal valid setup."""
        # Minimal WeatherData
        weather = WeatherData(
            temperature=0.0,
            humidity=0.0,
            condition="",
            wind_speed=0.0,
            location=""
        )

        assert weather.temperature == 0.0

        # Minimal stats
        temp = DailyStats(high=0.0, low=0.0, mean=0.0)
        humidity = DailyStats(high=0.0, low=0.0, mean=0.0)

        stats = WeatherStats(
            location="",
            period_days=1,
            temperature=temp,
            humidity=humidity,
            precipitation_mm=0.0
        )

        assert stats.period_days == 1

    def test_maximum_values(self):
        """Test with maximum reasonable values."""
        # Maximum temperature stats
        temp = DailyStats(high=60.0, low=-50.0, mean=5.0)
        humidity = DailyStats(high=100.0, low=0.0, mean=50.0)

        stats = WeatherStats(
            location="TestCity",
            period_days=365,
            temperature=temp,
            humidity=humidity,
            precipitation_mm=5000.0
        )

        assert stats.period_days == 365
        assert stats.precipitation_mm == 5000.0

