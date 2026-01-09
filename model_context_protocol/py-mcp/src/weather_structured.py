"""
FastApiMCP Weather Server with Structured Output

Demonstrates FastApiMCP integration for REST API and MCP protocol support.
Returns well-typed, validated data that clients can easily process.

Features:
  - Pydantic-based structured output validation
  - FastAPI endpoints automatically exposed as MCP tools
  - REST API endpoints for direct access
  - HTTP/POST MCP protocol support via POST /mcp endpoint
  - Comprehensive logging and error handling
"""

import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status, Header
import uvicorn

from fastapi_mcp import FastApiMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("weather.mcp")

# API Key authentication
API_KEY = os.getenv("API_KEY", "test-key-12345")


def verify_api_key(x_api_key: str = Header(...)) -> str:
    """Verify API key from request header."""
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key


# Create FastAPI app
app = FastAPI(
    title="Weather MCP Server",
    version="1.0.0",
    description="Weather service with structured output via MCP and REST API"
)

# Create FastApiMCP instance
mcp = FastApiMCP(app, name="Weather Service")
# Mount HTTP transport for MCP endpoints - enables POST /mcp endpoint
mcp.mount_http()


# ============================================================================
# Data Models
# ============================================================================

# Example 1: Using a Pydantic model for structured output
class WeatherData(BaseModel):
    """Structured weather data response."""

    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage (0-100)")
    condition: str = Field(description="Weather condition (sunny, cloudy, rainy, etc.)")
    wind_speed: float = Field(description="Wind speed in km/h")
    location: str = Field(description="Location name")
    timestamp: datetime = Field(default_factory=datetime.now, description="Observation time")


# Example 2: Using TypedDict for a simpler structure
class WeatherSummary(TypedDict):
    """Simple weather summary."""

    city: str
    temp_c: float
    description: str


# Example 4: Using dataclass for weather alerts
@dataclass
class WeatherAlert:
    """Weather alert information."""

    severity: str  # "low", "medium", "high"
    title: str
    description: str
    affected_areas: list[str]
    valid_until: datetime


# Example 6: Weather statistics with nested models
class DailyStats(BaseModel):
    """Statistics for a single day."""

    high: float
    low: float
    mean: float


class WeatherStats(BaseModel):
    """Weather statistics over a period."""

    location: str
    period_days: int
    temperature: DailyStats
    humidity: DailyStats
    precipitation_mm: float = Field(description="Total precipitation in millimeters")


# ============================================================================
# FastAPI Endpoints (automatically exposed as MCP tools)
# ============================================================================

@app.post("/weather", operation_id="get_weather", tags=["Weather"])
async def get_weather(city: str) -> WeatherData:
    """Get current weather for a city with full structured data."""
    logger.info(f"get_weather called for city: {city}")
    # In a real implementation, this would fetch from a weather API
    data = WeatherData(
        temperature=22.5,
        humidity=65.0,
        condition="partly cloudy",
        wind_speed=12.3,
        location=city
    )
    logger.info(f"Returning weather data for {city}")
    return data


@app.post("/weather-summary", operation_id="get_weather_summary", tags=["Weather"])
async def get_weather_summary(city: str) -> WeatherSummary:
    """Get a brief weather summary for a city."""
    logger.info(f"get_weather_summary called for city: {city}")
    summary = WeatherSummary(
        city=city,
        temp_c=22.5,
        description="Partly cloudy with light breeze"
    )
    logger.info(f"Returning summary for {city}")
    return summary


@app.post("/weather-metrics", operation_id="get_weather_metrics", tags=["Weather"])
async def get_weather_metrics(request_body: dict) -> dict[str, dict[str, float]]:
    """Get weather metrics for multiple cities.

    Returns a dictionary mapping city names to their metrics.

    Request body: {"cities": ["city1", "city2", ...]}
    """
    cities = request_body.get("cities", [])
    if not isinstance(cities, list):
        cities = [cities] if cities else []

    logger.info(f"get_weather_metrics called for cities: {cities}")
    # Returns nested dictionaries with weather metrics
    metrics = {
        city: {
            "temperature": 20.0 + i * 2,
            "humidity": 60.0 + i * 5,
            "pressure": 1013.0 + i * 0.5
        }
        for i, city in enumerate(cities)
    }
    logger.info(f"Returning metrics for {len(cities)} cities")
    return metrics


@app.post("/weather-alerts", operation_id="get_weather_alerts", tags=["Weather"])
async def get_weather_alerts(region: str) -> list[dict]:
    """Get active weather alerts for a region."""
    logger.info(f"get_weather_alerts called for region: {region}")
    # In production, this would fetch real alerts
    if region.lower() == "california":
        alerts = [
            {
                "severity": "high",
                "title": "Heat Wave Warning",
                "description": "Temperatures expected to exceed 40 degrees",
                "affected_areas": ["Los Angeles", "San Diego", "Riverside"],
                "valid_until": "2024-07-15T18:00:00",
            },
            {
                "severity": "medium",
                "title": "Air Quality Advisory",
                "description": "Poor air quality due to wildfire smoke",
                "affected_areas": ["San Francisco Bay Area"],
                "valid_until": "2024-07-14T12:00:00",
            },
        ]
        logger.info(f"Returning {len(alerts)} alerts for {region}")
        return alerts
    logger.info(f"No alerts for region: {region}")
    return []


@app.post("/temperature", operation_id="get_temperature", tags=["Weather"])
async def get_temperature(city: str, unit: str = "celsius") -> dict:
    """Get just the temperature for a city.

    Returns temperature in specified unit (celsius or fahrenheit).
    """
    logger.info(f"get_temperature called for city: {city}, unit: {unit}")
    base_temp = 22.5
    if unit.lower() == "fahrenheit":
        result = base_temp * 9 / 5 + 32
    else:
        result = base_temp
    logger.info(f"Returning temperature: {result} {unit}")
    return {"temperature": result, "unit": unit, "city": city}


@app.post("/weather-stats", operation_id="get_weather_stats", tags=["Weather"])
async def get_weather_stats(city: str, days: int = 7) -> WeatherStats:
    """Get weather statistics for the past N days."""
    logger.info(f"get_weather_stats called for city: {city}, days: {days}")
    stats = WeatherStats(
        location=city,
        period_days=days,
        temperature=DailyStats(high=28.5, low=15.2, mean=21.8),
        humidity=DailyStats(high=85.0, low=45.0, mean=65.0),
        precipitation_mm=12.4,
    )
    logger.info(f"Returning weather stats for {city}")
    return stats



# ============================================================================
# Service Endpoints
# ============================================================================

@app.get("/", tags=["Service"])
async def get_info():
    """Get server information and available endpoints."""
    logger.info("GET / called")
    return {
        "name": "Weather MCP Server",
        "version": "1.0.0",
        "status": "running",
        "description": "Weather service with structured output via MCP and REST API",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Server information"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/openapi.json", "method": "GET", "description": "OpenAPI schema"},
            {"path": "/mcp", "method": "POST", "description": "MCP protocol endpoint"},
        ],
    }


@app.get("/health", tags=["Service"])
async def health_check():
    """Health check endpoint."""
    logger.info("GET /health called")
    return {"status": "healthy", "service": "Weather MCP Server"}


if __name__ == "__main__":
    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000

    logger.info(f"Starting Weather MCP Server on {host}:{port}")
    logger.info(f"API Key: {API_KEY}")
    logger.info("Available endpoints:")
    logger.info("  GET /                 - Server information")
    logger.info("  GET /health           - Health check")
    logger.info("  GET /api/tools        - List available tools")
    logger.info("  POST /mcp             - MCP protocol endpoint")

    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except KeyboardInterrupt:
        logger.info("Server stopped by user (CTRL+C)")
        sys.exit(0)

