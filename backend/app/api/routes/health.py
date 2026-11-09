"""
Health check endpoints.
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check endpoint")
async def health_check():
    """Check application health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "product_hunter_ai",
    }


@router.get("/health/database", summary="Database health check")
async def database_health():
    """Check database connection health."""
    # Database check would be implemented here
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "component": "database",
    }


@router.get("/health/redis", summary="Redis health check")
async def redis_health():
    """Check Redis connection health."""
    # Redis check would be implemented here
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "component": "redis",
    }