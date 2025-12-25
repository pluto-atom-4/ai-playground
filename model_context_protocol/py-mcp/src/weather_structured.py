"""
FastMCP Weather Example with Structured Output

Demonstrates how to use structured output with tools to return
well-typed, validated data that clients can easily process.
"""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

from pydantic import BaseModel, Field
from fastapi import FastAPI
import uvicorn

from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session as client_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mcp.weather")

# Create server
mcp = FastMCP("Weather Service", json_response=True)


# Example 1: Using a Pydantic model for structured output
class WeatherData(BaseModel):
    """Structured weather data response"""

    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage (0-100)")
    condition: str = Field(description="Weather condition (sunny, cloudy, rainy, etc.)")
    wind_speed: float = Field(description="Wind speed in km/h")
    location: str = Field(description="Location name")
    timestamp: datetime = Field(default_factory=datetime.now, description="Observation time")


@mcp.tool()
def get_weather(city: str) -> WeatherData:
    """Get current weather for a city with full structured data"""
    logger.info(f"get_weather called for city: {city}")
    # In a real implementation, this would fetch from a weather API
    data = WeatherData(
        temperature=22.5,
        humidity=65.0,
        condition="partly cloudy",
        wind_speed=12.3,
        location=city
    )
    logger.info(f"Returning weather data for {city}: {data}")
    return data


# Example 2: Using TypedDict for a simpler structure
class WeatherSummary(TypedDict):
    """Simple weather summary"""

    city: str
    temp_c: float
    description: str


@mcp.tool()
def get_weather_summary(city: str) -> WeatherSummary:
    """Get a brief weather summary for a city"""
    logger.info(f"get_weather_summary called for city: {city}")
    summary = WeatherSummary(
        city=city,
        temp_c=22.5,
        description="Partly cloudy with light breeze"
    )
    logger.info(f"Returning summary for {city}: {summary}")
    return summary


# Example 3: Using dict[str, Any] for flexible schemas
@mcp.tool()
def get_weather_metrics(cities: list[str]) -> dict[str, dict[str, float]]:
    """Get weather metrics for multiple cities

    Returns a dictionary mapping city names to their metrics
    """
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
    logger.info(f"Returning metrics: {metrics}")
    return metrics


# Example 4: Using dataclass for weather alerts
@dataclass
class WeatherAlert:
    """Weather alert information"""

    severity: str  # "low", "medium", "high"
    title: str
    description: str
    affected_areas: list[str]
    valid_until: datetime


@mcp.tool()
def get_weather_alerts(region: str) -> list[WeatherAlert]:
    """Get active weather alerts for a region"""
    logger.info(f"get_weather_alerts called for region: {region}")
    # In production, this would fetch real alerts
    if region.lower() == "california":
        alerts = [
            WeatherAlert(
                severity="high",
                title="Heat Wave Warning",
                description="Temperatures expected to exceed 40 degrees",
                affected_areas=["Los Angeles", "San Diego", "Riverside"],
                valid_until=datetime(2024, 7, 15, 18, 0),
            ),
            WeatherAlert(
                severity="medium",
                title="Air Quality Advisory",
                description="Poor air quality due to wildfire smoke",
                affected_areas=["San Francisco Bay Area"],
                valid_until=datetime(2024, 7, 14, 12, 0),
            ),
        ]
        logger.info(f"Returning {len(alerts)} alerts for {region}")
        return alerts
    logger.info(f"No alerts for region: {region}")
    return []


# Example 5: Returning primitives with structured output
@mcp.tool()
def get_temperature(city: str, unit: str = "celsius") -> float:
    """Get just the temperature for a city

    When returning primitives as structured output,
    the result is wrapped in {"result": value}
    """
    logger.info(f"get_temperature called for city: {city}, unit: {unit}")
    base_temp = 22.5
    if unit.lower() == "fahrenheit":
        result = base_temp * 9 / 5 + 32
    else:
        result = base_temp
    logger.info(f"Returning temperature: {result} {unit}")
    return result


# Example 6: Weather statistics with nested models
class DailyStats(BaseModel):
    """Statistics for a single day"""

    high: float
    low: float
    mean: float


class WeatherStats(BaseModel):
    """Weather statistics over a period"""

    location: str
    period_days: int
    temperature: DailyStats
    humidity: DailyStats
    precipitation_mm: float = Field(description="Total precipitation in millimeters")


@mcp.tool()
def get_weather_stats(city: str, days: int = 7) -> WeatherStats:
    """Get weather statistics for the past N days"""
    logger.info(f"get_weather_stats called for city: {city}, days: {days}")
    stats = WeatherStats(
        location=city,
        period_days=days,
        temperature=DailyStats(high=28.5, low=15.2, mean=21.8),
        humidity=DailyStats(high=85.0, low=45.0, mean=65.0),
        precipitation_mm=12.4,
    )
    logger.info(f"Returning weather stats for {city}: {stats}")
    return stats


# Create FastAPI app for HTTP API
app = FastAPI(title="Weather MCP Server", version="1.0.0")


@app.get("/")
async def get_info():
    """Get server information and health status"""
    logger.info("GET / called")
    try:
        tools_response = await mcp.list_tools()
        tools_list = tools_response.tools if hasattr(tools_response, 'tools') else (tools_response if isinstance(tools_response, list) else [])
        return {
            "name": "Weather MCP Server",
            "version": "1.0.0",
            "status": "running",
            "endpoints": [
                {"path": "/", "method": "GET", "description": "Server info"},
                {"path": "/health", "method": "GET", "description": "Health check"},
                {"path": "/api/tools", "method": "GET", "description": "List available tools"},
            ],
            "tools": [
                {"name": t.name, "description": t.description}
                for t in tools_list
            ] if tools_list else [],
        }
    except Exception as e:
        logger.error(f"Error in GET /: {e}")
        return {"error": str(e), "status": "error"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("GET /health called")
    return {"status": "healthy", "service": "Weather MCP Server"}


@app.get("/api/tools")
async def list_tools():
    """Get list of available tools"""
    logger.info("GET /api/tools called")
    try:
        tools_response = await mcp.list_tools()
        tools_list = tools_response.tools if hasattr(tools_response, 'tools') else (tools_response if isinstance(tools_response, list) else [])
        return {
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.inputSchema
                }
                for t in tools_list
            ] if tools_list else []
        }
    except Exception as e:
        logger.error(f"Error in GET /api/tools: {e}")
        return {"error": str(e), "tools": []}


if __name__ == "__main__":

    async def test() -> None:
        """Test the tools by calling them through the server as a client would"""
        print("Testing Weather Service Tools (via MCP protocol)\n")
        print("=" * 80)

        async with client_session(mcp._mcp_server) as client:
            # Test get_weather
            result = await client.call_tool("get_weather", {"city": "London"})
            print("\nWeather in London:")
            print(json.dumps(result.structuredContent, indent=2))

            # Test get_weather_summary
            result = await client.call_tool("get_weather_summary", {"city": "Paris"})
            print("\nWeather summary for Paris:")
            print(json.dumps(result.structuredContent, indent=2))

            # Test get_weather_metrics
            result = await client.call_tool("get_weather_metrics", {"cities": ["Tokyo", "Sydney", "Mumbai"]})
            print("\nWeather metrics:")
            print(json.dumps(result.structuredContent, indent=2))

            # Test get_weather_alerts
            result = await client.call_tool("get_weather_alerts", {"region": "California"})
            print("\nWeather alerts for California:")
            print(json.dumps(result.structuredContent, indent=2))

            # Test get_temperature
            result = await client.call_tool("get_temperature", {"city": "Berlin", "unit": "fahrenheit"})
            print("\nTemperature in Berlin:")
            print(json.dumps(result.structuredContent, indent=2))

            # Test get_weather_stats
            result = await client.call_tool("get_weather_stats", {"city": "Seattle", "days": 30})
            print("\nWeather stats for Seattle (30 days):")
            print(json.dumps(result.structuredContent, indent=2))

            # Also show the text content for comparison
            print("\nText content for last result:")
            for content in result.content:
                if content.type == "text":
                    print(content.text)

    async def print_schemas() -> None:
        """Print all tool schemas"""
        print("Tool Schemas for Weather Service\n")
        print("=" * 80)

        tools_response = await mcp.list_tools()
        tools = tools_response.tools if hasattr(tools_response, 'tools') else tools_response
        for tool in tools:
            print(f"\nTool: {tool.name}")
            print(f"Description: {tool.description}")
            print("Input Schema:")
            print(json.dumps(tool.inputSchema, indent=2))

            if tool.outputSchema:
                print("Output Schema:")
                print(json.dumps(tool.outputSchema, indent=2))
            else:
                print("Output Schema: None (returns unstructured content)")

            print("-" * 80)

    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--schemas":
        asyncio.run(print_schemas())
    elif len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Start HTTP API server
        host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
        logger.info(f"Starting Weather HTTP server on {host}:{port}")
        try:
            uvicorn.run(app, host=host, port=port, log_level="info")
        except KeyboardInterrupt:
            logger.info("Weather HTTP server stopped by user (CTRL+C)")
            exit(0)
    else:
        print("Usage:")
        print("  python weather_structured.py          # Run tool tests")
        print("  python weather_structured.py --schemas # Print tool schemas")
        print("  python weather_structured.py --http [host] [port] # Start HTTP API server")
        print()
        asyncio.run(test())

