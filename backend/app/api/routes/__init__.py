"""
API routes package.
"""

from .health import health_router
from .products import products_router
from .sources import sources_router
from .reports import reports_router

__all__ = ["health_router", "products_router", "sources_router", "reports_router"]