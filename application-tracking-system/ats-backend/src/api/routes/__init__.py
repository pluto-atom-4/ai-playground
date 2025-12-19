"""API routes package."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Welcome to Application Tracking System API"}

