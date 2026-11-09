# Product Hunter AI - Database Design

## Architecture Overview

This document describes the PostgreSQL database schema designed for Supabase deployment, supporting the Product Hunter AI market intelligence platform.

## Design Principles

1. **Supabase Compatibility**: Uses UUID primary keys and PostgreSQL-specific features
2. **Data Deduplication**: Unique constraints prevent duplicate products and observations
3. **Historical Tracking**: All price and score changes are preserved
4. **Row Level Security**: User-sensitive data is protected by RLS policies
5. **Performance**: Strategic indexes for common queries
6. **Source Attribution**: All data retains source tracking and timestamps

## Entity Relationship Diagram

```
┌──────────────┐     ┌──────────────────┐     ┌───────────────┐
│   categories │     │     competitors  │
└──────┬───────┘     └────────┬─────────┘     └──────┬────────┘
       │                      │                       │
       │    ┌─────────────────┼───────────────────────┤
       │    │                 │                       │
       ▼    ▼                 ▼                       ▼
  ┌──────────────┐    ┌───────────────┐    ┌──────────────────┐
  │   products   │    │competitor_prod│    │  opportunity_    │
  │              │◄──►│  _products    │    │   scores         │
  └──────┬───────┘    └───────────────┘    └────────┬─────────┘
         │                                         │
         ├──► product_variants                    │
         │                                         │
         ├──► source_observations ◄── sources ◄───┤
         │      (with url uniqueness)              │
         │                                         │
         ├──► market_prices ◄═══ suppliers ◄─── supplier_products
         │      (is_current flag)                  │
         │                                         │
         └──► profit_calculations                  │
                                                   │
  ┌──────────────┐                                 │
  │ daily_reports│◄── report_items ◄─────────────┘
  └──────────────┘
         │
         └──► Telegram notifications
```

## Table Specifications

### Core Tables

| Table | Primary Key | Description |
|-------|-------------|-------------|
| `categories` | code (VARCHAR) | Product category reference |
| `products` | id (UUID) | Main product catalog |
| `product_variants` | id (UUID) | Product variations |
| `sources` | id (UUID) | Data source registry |
| `source_observations` | id (UUID) | Raw source data |
| `historical_prices` | id (UUID) | Price change history |
| `market_prices` | id (UUID) | Current marketplace prices |
| `trend_history` | id (UUID) | Trend metrics over time |

### Supplier Tables

| Table | Description |
|-------|-------------|
| `suppliers` | Supplier profiles and verification |
| `supplier_products` | Products from suppliers with pricing |

### Analysis Tables

| Table | Description |
|-------|-------------|
| `opportunity_scores` | AI-scored product opportunities |
| `profit_calculations` | Detailed profit margin analysis |
| `competitors` | Competitor company information |
| `competitor_products` | Competitor product listings |

### Reporting Tables

| Table | Description |
|-------|-------------|
| `daily_reports` | Generated daily intelligence reports |
| `report_items` | Products featured in reports |
| `agent_executions` | Agent run logs and metrics |

### User Tables

| Table | Description |
|-------|-------------|
| `users` | User accounts and roles |
| `user_preferences` | User customization settings |
| `telegram_notifications` | Sent notification records |
| `session_tokens` | Authentication sessions |
| `audit_log` | Security audit trail |

## Key Constraints

### Products
```sql
CONSTRAINT uq_product_normalized_name_brand 
    UNIQUE (normalized_name, brand)
```
Prevents duplicate product entries.

### Source Observations
```sql
CONSTRAINT uq_observation_url_source 
    UNIQUE (url, source_id)
```
Prevents duplicate observations from the same source.

### Opportunity Scores
```sql
CONSTRAINT uq_opportunity_score_product 
    UNIQUE (product_id)
```
Ensures one score per product (latest overwrites).

## Indexes Strategy

### Primary Performance Indexes
- `idx_products_normalized_name` - Full-text product search
- `idx_products_brand_category` - Brand/category filtering
- `idx_opportunity_scores_total_score` - Score-based sorting
- `idx_market_prices_marketplace` - Marketplace-specific queries
- `idx_historical_prices_product_time` - Price history timelines
- `idx_agent_executions_type_time` - Agent monitoring

### Composite Indexes
```sql
-- Product lookup by category
CREATE INDEX idx_products_category_created 
    ON products (category_code, created_at DESC);

-- Market price history
CREATE INDEX idx_market_prices_product_marketplace 
    ON market_prices (product_id, marketplace, is_current);

-- Score rankings
CREATE INDEX idx_scores_category_score 
    ON opportunity_scores (total_score DESC)
    WHERE product_id IN (SELECT id FROM products WHERE category_code IS NOT NULL);
```

## Views

### v_product_summary
```sql
SELECT
    p.id as product_id,
    p.normalized_name,
    p.brand,
    c.name as category_name,
    COALESCE(ms.total_score, 0) as opportunity_score,
    COUNT(DISTINCT po.id) as source_observations
FROM products p
LEFT JOIN opportunity_scores ms ON p.id = ms.product_id
LEFT JOIN categories c ON p.category_code = c.code
LEFT JOIN source_observations po ON p.id = po.product_id
WHERE p.is_active = TRUE
GROUP BY p.id, c.name, ms.total_score
ORDER BY ms.total_score DESC NULLS LAST
LIMIT 100;
```

## Storage Estimation

| Table | Avg Row Size | Estimated Rows | Disk Usage |
|-------|--------------|----------------|------------|
| products | ~500 bytes | 1M | ~500 MB |
| source_observations | ~800 bytes | 10M | ~8 GB |
| historical_prices | ~200 bytes | 5M | ~1 GB |
| opportunity_scores | ~300 bytes | 1M | ~300 MB |
| suppliers | ~1KB | 100K | ~100 MB |
| agent_executions | ~500 bytes | 500K | ~250 MB |

## Migration Strategy

Migrations are applied in order:
1. `001_initial_schema.sql` - Base tables and constraints
2. `002_add_indexes_and_functions.sql` - Performance optimization
3. `003_rls_policies.sql` - Security policies

## Row Level Security Policy Examples

```sql
-- Users can only see their own data
CREATE POLICY users_can_select_own ON users
FOR SELECT
USING (auth.uid() = id);

-- Admins have full access
CREATE POLICY admin_full_access ON users
FOR ALL
USING (auth.role() = 'admin');
```

## Query Patterns

### Find best opportunities in a category
```sql
SELECT * FROM v_product_summary 
WHERE category_code = 'smart_gadgets' 
AND opportunity_score >= 75
ORDER BY opportunity_score DESC;
```

### Get price history for a product
```sql
SELECT 
    recorded_at,
    price,
    currency,
    marketplace
FROM historical_prices
WHERE product_id = :product_id
ORDER BY recorded_at DESC
LIMIT 30;
```

### Find suppliers with verified status
```sql
SELECT 
    name,
    country,
    rating,
    response_time
FROM suppliers
WHERE is_verified = TRUE 
AND source_platform = 'aliexpress'
ORDER BY rating DESC
LIMIT 20;
```

### Monitor agent health
```sql
SELECT 
    agent_type,
    status,
    started_at,
    duration_seconds,
    items_created
FROM agent_executions
WHERE started_at > NOW() - INTERVAL '24 hours'
ORDER BY started_at DESC;
```