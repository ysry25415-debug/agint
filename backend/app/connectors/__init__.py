"""
Source connector framework for Product Hunter AI.
Provides modular connectors for different data sources.
"""

from .base import BaseConnector, ConnectorResult, SourceType
from .schemas import ConnectorConfig, DiscoveryResult, ProductData
from .exceptions import ConnectorError, RateLimitError, AuthError

__all__ = [
    "BaseConnector",
    "ConnectorResult",
    "SourceType",
    "ConnectorConfig",
    "DiscoveryResult",
    "ProductData",
    "ConnectorError",
    "RateLimitError",
    "AuthError",
]