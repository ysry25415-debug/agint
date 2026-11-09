"""
Schemas for connector data.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime


class ProductData(BaseModel):
    """Standardized product data from any source."""
    # Identification
    source_product_id: str
    source_name: str
    source_url: Optional[HttpUrl] = None

    # Product details
    name: str
    normalized_name: str
    brand: Optional[str] = None
    model_number: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

    # Pricing
    price: float
    currency: str
    original_price: Optional[float] = None
    discount_percent: Optional[int] = None

    # Availability
    available: bool = True
    stock_level: Optional[str] = None
    in_stock: Optional[bool] = None

    # Specifications
    specifications: Dict[str, Any] = Field(default_factory=dict)
    images: List[HttpUrl] = Field(default_factory=list)

    # Seller/Supplier
    seller_name: Optional[str] = None
    seller_url: Optional[HttpUrl] = None
    seller_location: Optional[str] = None

    # Metrics
    rating: Optional[float] = None
    review_count: Optional[int] = None
    likes: Optional[int] = None
    shares: Optional[int] = None

    # Timestamps
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = None

    # Raw data (preserved for attribution)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class DiscoveryResult(BaseModel):
    """Standardized discovery result from a connector."""
    source_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    query: Optional[str] = None
    category: Optional[str] = None
    total_results: int = 0
    products: List[ProductData] = Field(default_factory=list)
    next_offset: Optional[int] = None
    has_more: bool = False
    source_metadata: Dict[str, Any] = Field(default_factory=dict)


class ConnectorStatus(BaseModel):
    """Health status of a connector."""
    name: str
    is_healthy: bool
    status: str
    last_check: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    rate_limit: Dict[str, Any] = Field(default_factory=dict)


class SourceMapping(BaseModel):
    """Mapping between source categories and internal categories."""
    source_category: str
    internal_category: str
    confidence: float = 1.0