"""
API package for Product Hunter AI.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from .routes.health import health_router
from .routes.products import products_router
from .routes.sources import sources_router
from .routes.reports import reports_router
from ..core.config import settings
from ..core.logging_config import setup_logging

logger = logging.getLogger(__name__)


def get_application() -> FastAPI:
    """Create and configure FastAPI application."""

    setup_logging(settings.LOG_LEVEL)

    logger.info(f"Initializing {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # CORS middleware for dashboard access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(products_router, prefix="/api/v1")
    app.include_router(sources_router, prefix="/api/v1")
    app.include_router(reports_router, prefix="/api/v1")

    return app


app = get_application()