"""
Base connector class and common utilities.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Generator
from pydantic import BaseModel, Field
import logging
import time
import asyncio

logger = logging.getLogger(__name__)


class SourceType(str, Enum):
    """Types of data sources."""
    MARKETPLACE = "marketplace"
    SOCIAL_MEDIA = "social_media"
    SUPPLIER = "supplier"
    AGGREGATOR = "aggregator"


@dataclass
class ConnectorResult:
    """Result from a connector operation."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    items_found: int = 0
    items_processed: int = 0
    items_created: int = 0
    items_updated: int = 0
    items_skipped: int = 0
    source_status: str = "unknown"
    error_message: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConnectorConfig(BaseModel):
    """Configuration for a connector."""
    name: str
    source_type: SourceType
    api_endpoint: Optional[str] = None
    auth_method: Optional[str] = "api_key"
    rate_limit: int = 60  # requests per minute
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5
    country_focus: Optional[str] = None
    is_active: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict)


class BaseConnector(ABC):
    """
    Abstract base class for all source connectors.
    Provides common functionality for rate limiting, retries, and health checks.
    """

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self._last_request_time: float = 0
        self._request_count: int = 0
        self._is_healthy: bool = True
        self._error_message: Optional[str] = None
        self._sessions: Dict[str, Any] = {}  # For HTTP clients, etc.

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def is_healthy(self) -> bool:
        return self._is_healthy and self.config.is_active

    def _check_rate_limit(self) -> None:
        """Enforces rate limiting for the connector."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time

        min_interval = 60.0 / self.config.rate_limit

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)

        self._last_request_time = time.time()
        self._request_count += 1

    def _get_session(self, key: str = "default"):
        """Get or create a session for HTTP clients."""
        if key not in self._sessions:
            self._sessions[key] = self._create_session()
        return self._sessions[key]

    def _create_session(self):
        """Create a new HTTP session. Override in subclasses."""
        import httpx

        return httpx.AsyncClient(
            timeout=self.config.timeout,
            headers={"User-Agent": "ProductHunterAI/0.1"},
        )

    def _retry_wrapper(self, func, *args, **kwargs):
        """Execute a function with retry logic."""
        last_error = None

        for attempt in range(self.config.retry_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt + 1}/{self.config.retry_attempts} "
                    f"failed for {self.name}: {e}"
                )
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))

        raise last_error

    @abstractmethod
    async def discover_products(
        self,
        query: str = "",
        category: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        **kwargs
    ) -> ConnectorResult:
        """
        Discover products from this source.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    async def get_product_details(
        self,
        product_id: str,
        **kwargs
    ) -> ConnectorResult:
        """
        Get detailed information about a specific product.
        Must be implemented by subclasses.
        """
        pass

    async def health_check(self) -> ConnectorResult:
        """Check if the source is accessible and healthy."""
        try:
            # Simple connectivity check
            if hasattr(self, '_get_session'):
                session = self._get_session()
                response = await session.get(self.config.api_endpoint or "/", timeout=5.0)
                is_healthy = response.status_code < 500
            else:
                is_healthy = True

            self._is_healthy = is_healthy
            self._error_message = None if is_healthy else "Health check failed"

            return ConnectorResult(
                success=is_healthy,
                source_status="healthy" if is_healthy else "degraded",
                metadata={"checked_at": datetime.utcnow().isoformat()}
            )
        except Exception as e:
            self._is_healthy = False
            self._error_message = str(e)
            logger.error(f"Health check failed for {self.name}: {e}")

            return ConnectorResult(
                success=False,
                source_status="down",
                error_message=str(e),
            )

    async def close(self):
        """Close any open sessions and cleanup resources."""
        for session in self._sessions.values():
            if hasattr(session, 'aclose'):
                await session.aclose()
        self._sessions.clear()


# Sync wrapper for use in non-async contexts
def async_to_sync(coro):
    """Convert async coroutine to sync function."""
    import asyncio

    try:
        loop = asyncio.get_running_loop()
        # If we're in an async context, we can't run sync
        raise RuntimeError("Cannot run async function in sync context without a thread")
    except RuntimeError:
        # No running loop, create a new one
        return asyncio.run(coro)