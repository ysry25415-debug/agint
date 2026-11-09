"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from uuid import UUID


class ProductCategory(str, Enum):
    SMART_GADGETS = "smart_gadgets"
    MOBILE_ACCESSORIES = "mobile_accessories"
    PC_GAMING_ACCESSORIES = "pc_gaming_accessories"
    SMART_HOME = "smart_home"
    AUDIO_ELECTRONICS = "audio_electronics"
    PERSONAL_TECHNOLOGY = "personal_technology"
    INNOVATIVE_PRODUCTS = "innovative_products"
    PORTABLE_DEVICES = "portable_devices"


class AgentType(str, Enum):
    GLOBAL_DISCOVERY = "global_discovery"
    SOCIAL_TRENDS = "social_trends"
    EGYPTIAN_MARKET = "egyptian_market"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    SUPPLIER_DISCOVERY = "supplier_discovery"
    PROFIT_CALCULATION = "profit_calculation"
    PRODUCT_SCORING = "product_scoring"
    REPORT_GENERATION = "report_generation"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRIED = "retried"


# Source Observation Schemas
class SourceObservationBase(BaseModel):
    url: Optional[HttpUrl] = None
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "USD"
    availability: Optional[str] = None
    stock_level: Optional[str] = None
    likes: Optional[int] = None
    shares: Optional[int] = None
    comments: Optional[int] = None
    views: Optional[int] = None
    rank_position: Optional[int] = None
    rank_type: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class SourceObservationCreate(SourceObservationBase):
    source_id: int
    product_id: Optional[int] = None


class SourceObservationOut(SourceObservationBase):
    id: int
    source_id: int
    product_id: Optional[int] = None
    discovery_time: datetime
    extracted_by: Optional[str] = None

    class Config:
        from_attributes = True


class SourceOut(BaseModel):
    id: int
    name: str
    type: str
    country_focus: Optional[str] = None
    is_active: bool
    status: str
    error_message: Optional[str] = None
    last_check: Optional[datetime] = None

    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    normalized_name: str
    brand: Optional[str] = None
    model_number: Optional[str] = None
    category: str
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    image_url: Optional[HttpUrl] = None


class ProductCreate(ProductBase):
    variants: Optional[List[dict]] = None


class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    variant_count: int = 0

    class Config:
        from_attributes = True


class ProductDetailOut(ProductOut):
    variants: Optional[List[dict]] = None
    observations: Optional[List[SourceObservationOut]] = None
    market_prices: Optional[List[dict]] = None
    scores: Optional[List[dict]] = None


# Market Price Schemas
class MarketPriceBase(BaseModel):
    marketplace: str
    price: float
    currency: str = "EGP"
    url: Optional[HttpUrl] = None
    available: bool = True
    shipping_info: Optional[str] = None


class MarketPriceCreate(MarketPriceBase):
    product_id: int


class MarketPriceOut(MarketPriceBase):
    id: int
    product_id: int
    recorded_at: datetime
    is_current: bool

    class Config:
        from_attributes = True


# Supplier Schemas
class SupplierBase(BaseModel):
    name: str
    source_platform: str
    country: Optional[str] = None
    location: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None


class SupplierOut(SupplierBase):
    id: int
    platform_product_id: Optional[str] = None
    minimum_order: Optional[str] = None
    delivery_time: Optional[str] = None
    shipping_cost: Optional[float] = None
    is_verified: bool
    last_updated: datetime

    class Config:
        from_attributes = True


class SupplierProductOut(BaseModel):
    id: int
    supplier_id: int
    product_name: str
    normalized_name: str
    price: float
    currency: Optional[str] = None
    price_usd: Optional[float] = None
    category: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    url: Optional[HttpUrl] = None
    scraped_at: datetime

    class Config:
        from_attributes = True


# Opportunity Score Schemas
class OpportunityScoreBase(BaseModel):
    demand_signals: Optional[float] = None
    market_growth: Optional[float] = None
    competition: Optional[float] = None
    profit_potential: Optional[float] = None
    sourcing_feasibility: Optional[float] = None
    marketing_potential: Optional[float] = None
    risk_seasonality: Optional[float] = None


class OpportunityScoreOut(OpportunityScoreBase):
    id: int
    product_id: int
    total_score: float
    confidence_score: Optional[float] = None
    scored_at: datetime
    scored_by: str

    class Config:
        from_attributes = True


# Profit Calculation Schemas
class ProfitCalculation(BaseModel):
    supplier_price: float
    supplier_currency: str = "USD"
    shipping_cost: float
    shipping_currency: str = "USD"
    customs_duty: float = 0.0
    customs_fee: float = 0.0
    local_delivery: float = 0.0
    marketing_cost: float = 0.0
    estimated_selling_price: float
    selling_currency: str = "EGP"


class ProfitReport(BaseModel):
    supplier_purchase_price: float
    supplier_currency: str
    currency_conversion_rate: float
    international_shipping: float
    customs_and_taxes: float
    local_delivery: float
    marketing_costs: float
    total_costs: float
    estimated_selling_price: float
    selling_currency: str
    gross_profit: float
    estimated_net_profit: float
    profit_margin: float


# Daily Report Schemas
class ReportItemBase(BaseModel):
    product_id: int
    opportunity_score: Optional[float] = None
    profit_margin: Optional[float] = None
    profit_estimate: Optional[float] = None
    ranking: Optional[int] = None


class ReportItemOut(ReportItemBase):
    id: int
    product: Optional[dict] = None


class DailyReportBase(BaseModel):
    report_date: Optional[datetime] = None
    status: str = "draft"
    total_products: int = 0
    report_items: Optional[List[ReportItemOut]] = None


class DailyReportOut(DailyReportBase):
    id: int
    generated_at: datetime
    sent_at: Optional[datetime] = None
    top_opportunities: Optional[List[dict]] = None
    market_trends: Optional[dict] = None
    summary: Optional[str] = None


# Agent Execution Schemas
class AgentExecutionBase(BaseModel):
    agent_type: AgentType
    status: ExecutionStatus
    started_at: datetime


class AgentExecutionOut(AgentExecutionBase):
    id: int
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    items_processed: Optional[int] = None
    items_created: Optional[int] = None
    items_updated: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    source_stats: Optional[Dict[str, Any]] = None


# Request/Response Messages
class HealthCheck(BaseModel):
    status: str
    database: str
    redis: str
    timestamp: datetime


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None