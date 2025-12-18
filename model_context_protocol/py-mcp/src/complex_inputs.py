"""
FastMCP Complex Inputs Example

Demonstrates validation via Pydantic with complex models.
This example shows how to use complex data structures with MCP tools,
including nested models and field validation.
"""

import logging
from typing import Annotated
import uvicorn

from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mcp.complex_inputs")

# Create an MCP server instance
mcp = FastMCP("ComplexInputsServer", json_response=True)


# Define complex Pydantic models for validation
class Shrimp(BaseModel):
    """Model representing a shrimp in the tank"""
    name: Annotated[str, Field(max_length=10, description="Name of the shrimp")]
    species: Annotated[str, Field(description="Species of the shrimp")]
    age_months: Annotated[int, Field(ge=0, le=360, description="Age in months (0-360)")]


class ShrimpTank(BaseModel):
    """Model representing a shrimp tank with multiple shrimp"""
    tank_name: Annotated[str, Field(description="Name of the tank")]
    capacity: Annotated[int, Field(ge=1, description="Tank capacity in liters")]
    shrimp_list: Annotated[list[Shrimp], Field(description="List of shrimp in the tank")]


class FishFood(BaseModel):
    """Model representing fish food"""
    name: Annotated[str, Field(description="Name of the food")]
    protein_percent: Annotated[float, Field(ge=0, le=100, description="Protein percentage")]


class AquariumSetup(BaseModel):
    """Complex model for aquarium setup"""
    tank: ShrimpTank
    food: Annotated[list[FishFood], Field(description="Available food types")]
    maintenance_schedule: Annotated[dict[str, str], Field(description="Maintenance schedule")]


@mcp.tool(
    name="name_shrimp",
    description="List all shrimp names in the tank, optionally appending extra names"
)
def name_shrimp(
    tank: ShrimpTank,
    extra_names: Annotated[list[str], Field(max_length=10, description="Additional names to append")],
) -> list[str]:
    """
    List all shrimp names in the tank, optionally appending extra names.

    Args:
        tank: The shrimp tank object with shrimp list
        extra_names: Additional names to append to the list

    Returns:
        List of all shrimp names plus extra names
    """
    logger.info(f"name_shrimp called with tank: {tank.tank_name}, capacity: {tank.capacity}")
    shrimp_names = [shrimp.name for shrimp in tank.shrimp_list]
    all_names = shrimp_names + extra_names
    logger.info(f"Returning names: {all_names}")
    return all_names


@mcp.tool(
    name="analyze_tank",
    description="Analyze the shrimp tank and return statistics"
)
def analyze_tank(tank: ShrimpTank) -> dict:
    """
    Analyze the shrimp tank and return statistics.

    Args:
        tank: The shrimp tank to analyze

    Returns:
        Dictionary with tank statistics
    """
    logger.info(f"analyze_tank called for tank: {tank.tank_name}")

    num_shrimp = len(tank.shrimp_list)
    avg_age = sum(shrimp.age_months for shrimp in tank.shrimp_list) / num_shrimp if num_shrimp > 0 else 0

    species_count = {}
    for shrimp in tank.shrimp_list:
        species_count[shrimp.species] = species_count.get(shrimp.species, 0) + 1

    stocking_density = num_shrimp / tank.capacity

    result = {
        "tank_name": tank.tank_name,
        "capacity": tank.capacity,
        "num_shrimp": num_shrimp,
        "average_age_months": round(avg_age, 2),
        "species_distribution": species_count,
        "stocking_density": round(stocking_density, 2),
    }

    logger.info(f"Tank analysis result: {result}")
    return result


@mcp.tool(
    name="configure_aquarium",
    description="Configure a complete aquarium setup with tank, food, and maintenance schedule"
)
def configure_aquarium(
    setup: AquariumSetup,
    notes: Annotated[str, Field(default="", description="Additional setup notes")]
) -> dict:
    """
    Configure a complete aquarium setup with tank, food, and maintenance schedule.

    Args:
        setup: The aquarium setup configuration
        notes: Optional additional notes

    Returns:
        Configuration summary
    """
    logger.info(f"configure_aquarium called for tank: {setup.tank.tank_name}")

    config_summary = {
        "tank": {
            "name": setup.tank.tank_name,
            "capacity": setup.tank.capacity,
            "shrimp_count": len(setup.tank.shrimp_list),
        },
        "food": [
            {
                "name": f.name,
                "protein_percent": f.protein_percent
            }
            for f in setup.food
        ],
        "maintenance": setup.maintenance_schedule,
        "notes": notes,
    }

    logger.info(f"Aquarium configuration: {config_summary}")
    return config_summary


@mcp.tool(
    name="find_shrimp_by_species",
    description="Find all shrimp of a specific species in the tank"
)
def find_shrimp_by_species(
    tank: ShrimpTank,
    species: Annotated[str, Field(description="Species to search for")]
) -> list[dict]:
    """
    Find all shrimp of a specific species in the tank.

    Args:
        tank: The shrimp tank to search
        species: The species to find

    Returns:
        List of shrimp matching the species
    """
    logger.info(f"find_shrimp_by_species called for species: {species}")

    matching_shrimp = [
        {
            "name": shrimp.name,
            "species": shrimp.species,
            "age_months": shrimp.age_months
        }
        for shrimp in tank.shrimp_list
        if shrimp.species.lower() == species.lower()
    ]

    logger.info(f"Found {len(matching_shrimp)} shrimp of species {species}")
    return matching_shrimp

# Create FastAPI app for HTTP API
app = FastAPI(
    title="MCP Complex Inputs Server",
    description="RESTful API for complex input handling with Pydantic validation",
    version="1.0.0"
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "MCP Complex Inputs Server"}


# Tool endpoints
@app.post("/api/tools/name_shrimp", tags=["Tools"], summary="List all shrimp names")
async def api_name_shrimp(
    tank: ShrimpTank,
    extra_names: Annotated[list[str], Field(max_length=10, description="Additional names")] = []
):
    """
    List all shrimp names in the tank, optionally appending extra names.

    **Parameters:**
    - tank: The shrimp tank object with shrimp list
    - extra_names: Additional names to append (max 10)

    **Returns:** List of all shrimp names
    """
    logger.info(f"API: name_shrimp called")
    return name_shrimp(tank, extra_names)


@app.post("/api/tools/analyze_tank", tags=["Tools"], summary="Analyze shrimp tank")
async def api_analyze_tank(tank: ShrimpTank):
    """
    Analyze the shrimp tank and return statistics.

    **Parameters:**
    - tank: The shrimp tank to analyze

    **Returns:** Dictionary with tank statistics including:
    - tank_name
    - capacity
    - num_shrimp
    - average_age_months
    - species_distribution
    - stocking_density
    """
    logger.info(f"API: analyze_tank called")
    return analyze_tank(tank)


@app.post("/api/tools/configure_aquarium", tags=["Tools"], summary="Configure aquarium")
async def api_configure_aquarium(
    setup: AquariumSetup,
    notes: Annotated[str, Field(default="", description="Additional setup notes")] = ""
):
    """
    Configure a complete aquarium setup with tank, food, and maintenance schedule.

    **Parameters:**
    - setup: The aquarium setup configuration
    - notes: Optional additional notes

    **Returns:** Configuration summary
    """
    logger.info(f"API: configure_aquarium called")
    return configure_aquarium(setup, notes)


@app.post("/api/tools/find_shrimp_by_species", tags=["Tools"], summary="Find shrimp by species")
async def api_find_shrimp_by_species(
    tank: ShrimpTank,
    species: Annotated[str, Field(description="Species to search for")]
):
    """
    Find all shrimp of a specific species in the tank.

    **Parameters:**
    - tank: The shrimp tank to search
    - species: The species to find (case-insensitive)

    **Returns:** List of shrimp matching the species
    """
    logger.info(f"API: find_shrimp_by_species called for species: {species}")
    return find_shrimp_by_species(tank, species)


# List tools endpoint
@app.get("/api/tools", tags=["Tools"], summary="List available tools")
async def list_tools():
    """
    List all available MCP tools.

    **Returns:** List of available tools with descriptions
    """
    tools = [
        {
            "name": "name_shrimp",
            "description": "List all shrimp names in a tank with optional extra names",
            "endpoint": "POST /api/tools/name_shrimp"
        },
        {
            "name": "analyze_tank",
            "description": "Analyze shrimp tank and return statistics",
            "endpoint": "POST /api/tools/analyze_tank"
        },
        {
            "name": "configure_aquarium",
            "description": "Configure a complete aquarium setup",
            "endpoint": "POST /api/tools/configure_aquarium"
        },
        {
            "name": "find_shrimp_by_species",
            "description": "Find shrimp of a specific species in the tank",
            "endpoint": "POST /api/tools/find_shrimp_by_species"
        }
    ]
    return {"tools": tools, "count": len(tools)}


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    MCP Complex Inputs Server - Root endpoint.

    **Available endpoints:**
    - GET /health - Health check
    - GET /api/tools - List available tools
    - GET /docs - Interactive API documentation (Swagger UI)
    - GET /redoc - Alternative API documentation (ReDoc)
    """
    return {
        "service": "MCP Complex Inputs Server",
        "version": "1.0.0",
        "documentation": "Visit /docs for interactive API documentation",
        "endpoints": [
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/api/tools", "method": "GET", "description": "List available tools"},
            {"path": "/api/tools/name_shrimp", "method": "POST", "description": "Name shrimp"},
            {"path": "/api/tools/analyze_tank", "method": "POST", "description": "Analyze tank"},
            {"path": "/api/tools/configure_aquarium", "method": "POST", "description": "Configure aquarium"},
            {"path": "/api/tools/find_shrimp_by_species", "method": "POST", "description": "Find shrimp by species"},
            {"path": "/docs", "method": "GET", "description": "Interactive API documentation"},
            {"path": "/redoc", "method": "GET", "description": "Alternative API documentation"}
        ]
    }


if __name__ == "__main__":
    logger.info("Starting Complex Inputs MCP server...")
    logger.info("Available endpoints:")
    logger.info("  GET  /health")
    logger.info("  GET  /api/tools")
    logger.info("  POST /api/tools/name_shrimp")
    logger.info("  POST /api/tools/analyze_tank")
    logger.info("  POST /api/tools/configure_aquarium")
    logger.info("  POST /api/tools/find_shrimp_by_species")
    logger.info("  Visit http://127.0.0.1:8000/docs for interactive documentation")
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except KeyboardInterrupt:
        logger.info("Complex Inputs MCP server stopped by user (CTRL+C)")
        exit(0)



