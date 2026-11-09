"""
Base database models for Product Hunter AI.
Defines all tables for products, sources, prices, suppliers, and agents.
Updated for Supabase PostgreSQL with UUID primary keys.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Table, Index, func, UniqueConstraint, Numeric,
    CheckConstraint, LargeBinary
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship, declared_attr
import uuid

from backend.app.core.database import Base


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


class Product(Base):
    """Main product table with deduplication support."""

    __tablename__ = "products"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    normalized_name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=True, index=True)
    model_number = Column(String(100), nullable=True, index=True)
    category_code = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    specifications = Column(JSONB, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    observations = relationship("SourceObservation", back_populates="product", cascade="all, delete-orphan")
    market_prices = relationship("MarketPrice", back_populates="product", cascade="all, delete-orphan")
    scores = relationship("OpportunityScore", back_populates="product", cascade="all, delete-orphan")
    report_items = relationship("ReportItem", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_products_normalized_name", "normalized_name"),
        Index("idx_products_brand_category", "brand", "category_code"),
        UniqueConstraint("normalized_name", "brand", name="uq_product_normalized_name_brand"),
    )


class ProductVariant(Base):
    """Product variants with different specifications."""

    __tablename__ = "product_variants"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    sku = Column(String(100), nullable=True, unique=True)
    color = Column(String(50), nullable=True)
    storage = Column(String(50), nullable=True)
    memory = Column(String(50), nullable=True)
    specifications = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="variants")

    __table_args__ = (Index("idx_variants_product", "product_id"),)


class Category(Base):
    """Product category lookup table."""

    __tablename__ = "categories"

    code = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Source(Base):
    """Data sources for product information."""

    __tablename__ = "sources"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    type = Column(String(50), nullable=False)
    api_endpoint = Column(Text, nullable=True)
    country_focus = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    auth_method = Column(String(50), default='api_key')
    rate_limit = Column(Integer, default=60)
    last_check = Column(DateTime, nullable=True)
    status = Column(String(20), default='unknown')
    error_message = Column(Text, nullable=True)
    api_key_encrypted = Column(LargeBinary, nullable=True)
    config = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    observations = relationship("SourceObservation", back_populates="source", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_sources_name", "name"),
        Index("idx_sources_type", "type"),
        Index("idx_sources_status", "status"),
    )


class SourceObservation(Base):
    """Raw observations from sources about products."""

    __tablename__ = "source_observations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    source_id = Column(PG_UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False)
    discovery_time = Column(DateTime, default=datetime.utcnow, index=True)
    url = Column(Text, nullable=False)
    title = Column(String(500), nullable=True)
    author = Column(String(200), nullable=True)
    price = Column(Numeric(12, 4), nullable=True)
    currency = Column(String(3), default='USD')
    availability = Column(String(100), nullable=True)
    stock_level = Column(String(50), nullable=True)
    likes = Column(Integer, nullable=True)
    shares = Column(Integer, nullable=True)
    comments = Column(Integer, nullable=True)
    views = Column(Integer, nullable=True)
    rank_position = Column(Integer, nullable=True)
    rank_type = Column(String(50), nullable=True)
    raw_data = Column(JSONB, nullable=True)
    extracted_by = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    source_product_id = Column(String(255), nullable=True)

    product = relationship("Product", back_populates="observations")
    source = relationship("Source", back_populates="observations")

    __table_args__ = (
        Index("idx_observations_product", "product_id"),
        Index("idx_observations_source", "source_id"),
        Index("idx_observations_discovery_time", "discovery_time"),
        Index("idx_observations_url", "url"),
        UniqueConstraint("url", "source_id", name="uq_observation_url_source"),
    )


class HistoricalPrice(Base):
    """Historical price tracking for products."""

    __tablename__ = "historical_prices"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    source_id = Column(PG_UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False)
    marketplace = Column(String(100), nullable=True)
    price = Column(Numeric(12, 4), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    recorded_at = Column(DateTime, default=datetime.utcnow)
    recorded_by = Column(String(100), nullable=True)

    __table_args__ = (
        Index("idx_historical_prices_product_time", "product_id", "recorded_at"),
        Index("idx_historical_prices_source_time", "source_id", "recorded_at"),
        Index("idx_historical_prices_marketplace", "marketplace"),
    )


class MarketPrice(Base):
    """Current market prices from Egyptian marketplaces."""

    __tablename__ = "market_prices"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    marketplace = Column(String(100), nullable=False)
    price = Column(Numeric(12, 4), nullable=False)
    currency = Column(String(3), nullable=False, default='EGP')
    url = Column(Text, nullable=True)
    available = Column(Boolean, default=True)
    shipping_info = Column(String(200), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    is_current = Column(Boolean, default=True)

    product = relationship("Product", back_populates="market_prices")

    __table_args__ = (
        Index("idx_market_prices_product", "product_id"),
        Index("idx_market_prices_marketplace", "marketplace"),
        Index("idx_market_prices_current", "is_current"),
    )


class Competitor(Base):
    """Competitor information for market analysis."""

    __tablename__ = "competitors"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    brand = Column(String(100), nullable=True)
    country = Column(String(100), default='EG')
    website = Column(String(200), nullable=True)
    social_followers = Column(Integer, nullable=True)
    monthly_visitors = Column(Integer, nullable=True)
    average_price = Column(Numeric(12, 4), nullable=True)
    price_range = Column(String(100), nullable=True)
    founded_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("CompetitorProduct", back_populates="competitor", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_competitors_name", "name"),)


class CompetitorProduct(Base):
    """Competitor's products for comparison."""

    __tablename__ = "competitor_products"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(PG_UUID(as_uuid=True), ForeignKey("competitors.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), nullable=False, index=True)
    category_code = Column(String(50), nullable=True)
    price = Column(Numeric(12, 4), nullable=True)
    currency = Column(String(3), default='EGP')
    availability = Column(String(50), nullable=True)
    rating = Column(Numeric(3, 2), nullable=True)
    review_count = Column(Integer, nullable=True)
    url = Column(String(500), nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    competitor = relationship("Competitor", back_populates="products")

    __table_args__ = (
        Index("idx_competitor_products_normalized_name", "normalized_name"),
        UniqueConstraint("competitor_id", "normalized_name", name="uq_competitor_product"),
    )


class Supplier(Base):
    """Supplier information for sourcing analysis."""

    __tablename__ = "suppliers"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    source_platform = Column(String(100), nullable=False)
    platform_product_id = Column(String(100), nullable=True, index=True)
    supplier_id = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    minimum_order = Column(String(100), nullable=True)
    delivery_time = Column(String(100), nullable=True)
    shipping_cost = Column(Numeric(12, 4), nullable=True)
    shipping_currency = Column(String(3), default='USD')
    rating = Column(Numeric(3, 2), nullable=True)
    review_count = Column(Integer, nullable=True)
    response_time = Column(String(50), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_top_rated = Column(Boolean, default=False)
    company_description = Column(Text, nullable=True)
    response_rate = Column(String(50), nullable=True)
    annual_revenue = Column(String(100), nullable=True)
    employees = Column(Integer, nullable=True)
    verification_status = Column(String(50), nullable=True)
    verified_date = Column(DateTime, nullable=True)
    website = Column(String(200), nullable=True)
    contact_info = Column(JSONB, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    products_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier_products = relationship("SupplierProduct", back_populates="supplier", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_suppliers_platform_product", "source_platform", "platform_product_id"),)


class SupplierProduct(Base):
    """Products from suppliers."""

    __tablename__ = "suppliers_products"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = Column(PG_UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    product_name = Column(String(500), nullable=False)
    normalized_name = Column(String(500), nullable=False, index=True)
    price = Column(Numeric(12, 4), nullable=False)
    currency = Column(String(3), default='USD')
    price_usd = Column(Numeric(12, 4), nullable=True)
    category_code = Column(String(50), nullable=True)
    specifications = Column(JSONB, nullable=True)
    stock_status = Column(String(50), nullable=True)
    minimum_order_quantity = Column(Integer, nullable=True)
    package_details = Column(String(500), nullable=True)
    url = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    last_price_update = Column(DateTime, nullable=True)

    supplier = relationship("Supplier", back_populates="supplier_products")

    __table_args__ = (
        Index("idx_supplier_products_normalized_name", "normalized_name"),
        Index("idx_supplier_products_supplier", "supplier_id"),
        Index("idx_supplier_products_price", "price"),
    )


class OpportunityScore(Base):
    """Product opportunity scores with detailed breakdown."""

    __tablename__ = "opportunity_scores"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    scored_at = Column(DateTime, default=datetime.utcnow, index=True)
    total_score = Column(Numeric(5, 2), nullable=False)
    confidence_score = Column(Numeric(5, 2), nullable=True)

    # Score breakdown (weighted components)
    demand_signals_score = Column(Numeric(5, 2), nullable=True)
    market_growth_score = Column(Numeric(5, 2), nullable=True)
    competition_score = Column(Numeric(5, 2), nullable=True)
    profit_potential_score = Column(Numeric(5, 2), nullable=True)
    sourcing_feasibility_score = Column(Numeric(5, 2), nullable=True)
    marketing_potential_score = Column(Numeric(5, 2), nullable=True)
    risk_seasonality_score = Column(Numeric(5, 2), nullable=True)

    scored_by = Column(String(100), nullable=False)
    scoring_details = Column(JSONB, nullable=True)

    product = relationship("Product", back_populates="scores")

    __table_args__ = (
        Index("idx_opportunity_scores_product", "product_id"),
        Index("idx_opportunity_scores_total_score", "total_score"),
        Index("idx_opportunity_scores_scored_at", "scored_at"),
        UniqueConstraint("product_id", name="uq_opportunity_score_product"),
    )


class ProfitCalculation(Base):
    """Detailed profit calculation for products."""

    __tablename__ = "profit_calculations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    supplier_id = Column(PG_UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    supplier_purchase_price = Column(Numeric(12, 4), nullable=False)
    supplier_currency = Column(String(3), nullable=False, default='USD')
    currency_conversion_rate = Column(Numeric(12, 6), default=1.0)
    currency_conversion_date = Column(DateTime, nullable=True)
    international_shipping = Column(Numeric(12, 4), default=0.0)
    shipping_currency = Column(String(3), default='USD')
    customs_duty_rate = Column(Numeric(5, 2), default=0.0)
    customs_duty_amount = Column(Numeric(12, 4), default=0.0)
    customs_fee = Column(Numeric(12, 4), default=0.0)
    local_delivery_cost = Column(Numeric(12, 4), default=0.0)
    marketing_costs = Column(Numeric(12, 4), default=0.0)
    estimated_selling_price = Column(Numeric(12, 4), nullable=False)
    selling_currency = Column(String(3), nullable=False, default='EGP')
    gross_profit = Column(Numeric(12, 4))
    estimated_net_profit = Column(Numeric(12, 4))
    profit_margin = Column(Numeric(8, 2))
    calculated_at = Column(DateTime, default=datetime.utcnow)
    calculated_by = Column(String(100), nullable=False)
    calculation_notes = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_profit_calc_product", "product_id"),
        Index("idx_profit_calc_profit_margin", "profit_margin"),
        Index("idx_profit_calc_net_profit", "estimated_net_profit"),
        Index("idx_profit_calc_calculated_at", "calculated_at"),
    )


class DailyReport(Base):
    """Daily research reports."""

    __tablename__ = "daily_reports"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_date = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(20), default='draft')
    total_products = Column(Integer, default=0)
    report_data = Column(JSONB, nullable=True)
    summary = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    telegram_message_id = Column(String(50), nullable=True)
    telegram_chat_id = Column(String(50), nullable=True)
    report_type = Column(String(50), default='daily')

    report_items = relationship("ReportItem", back_populates="report", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_reports_date", "report_date"),
        Index("idx_reports_status", "status"),
    )


class ReportItem(Base):
    """Items within a daily report."""

    __tablename__ = "report_items"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(PG_UUID(as_uuid=True), ForeignKey("daily_reports.id"), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    opportunity_score = Column(Numeric(5, 2), nullable=True)
    profit_margin = Column(Numeric(8, 2), nullable=True)
    profit_estimate = Column(Numeric(12, 4), nullable=True)
    ranking = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    report = relationship("DailyReport", back_populates="report_items")
    product = relationship("Product", back_populates="report_items")

    __table_args__ = (
        Index("idx_report_items_report", "report_id"),
        Index("idx_report_items_product", "product_id"),
    )


class AgentExecution(Base):
    """Agent execution logs for monitoring and debugging."""

    __tablename__ = "agent_executions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Numeric(10, 3), nullable=True)
    items_processed = Column(Integer, nullable=True)
    items_created = Column(Integer, nullable=True)
    items_updated = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    source_stats = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_agent_executions_type_time", "agent_type", "started_at"),
        Index("idx_agent_executions_status", "status"),
    )


