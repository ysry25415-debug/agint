-- Product Hunter AI - Additional Indexes and Functions
-- Supabase PostgreSQL Migration 002

-- ============================================================================
-- COMPOSITE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite indexes for product searches
CREATE INDEX IF NOT EXISTS idx_products_brand_category_active ON products (brand, category_code, is_active);
CREATE INDEX IF NOT EXISTS idx_products_category_created ON products (category_code, created_at DESC);

-- Composite indexes for price comparisons
CREATE INDEX IF NOT EXISTS idx_historical_prices_product_currency ON historical_prices (product_id, currency, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_market_prices_product_marketplace ON market_prices (product_id, marketplace, is_current);

-- Composite indexes for supplier searches
CREATE INDEX IF NOT EXISTS idx_supplier_products_category_price ON supplier_products (category_code, price);
CREATE INDEX IF NOT EXISTS idx_suppliers_platform_country ON suppliers (source_platform, country);

-- Composite indexes for scores
CREATE INDEX IF NOT EXISTS idx_scores_category_score ON opportunity_scores (total_score DESC)
    WHERE product_id IN (SELECT id FROM products WHERE category_code IS NOT NULL);

-- Composite indexes for trend analysis
CREATE INDEX IF NOT EXISTS idx_trends_type_metric_time ON trend_history (trend_type, metric_name, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_trends_category_trend_time ON trend_history (category_code, trend_type, recorded_at DESC);

-- Composite indexes for observations
CREATE INDEX IF NOT EXISTS idx_observations_price_currency ON source_observations (price, currency) WHERE price IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_observations_social_metrics ON source_observations (likes DESC, shares DESC, comments DESC);

-- ============================================================================
-- CUSTOM FUNCTIONS
-- ============================================================================

-- Function to calculate normalized product similarity
CREATE OR REPLACE FUNCTION calculate_product_similarity(
    product1_name TEXT,
    product2_name TEXT
) RETURNS NUMERIC(5, 4) AS $$
DECLARE
    sim NUMERIC(5, 4);
BEGIN
    -- Simple Levenshtein-based similarity
    sim := 1.0 - (
        LEV(LOWER(product1_name), LOWER(product2_name))::NUMERIC /
        GREATEST(LENGTH(product1_name), LENGTH(product2_name), 1)
    );
    RETURN GREATEST(sim, 0);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to generate opportunity score
CREATE OR REPLACE FUNCTION calculate_opportunity_score(
    market_growth_rate NUMERIC,
    demand_index NUMERIC,
    competition_index NUMERIC,
    profit_margin NUMERIC,
    sourcing_difficulty NUMERIC,
    marketing_potential NUMERIC
) RETURNS TABLE (
    total_score NUMERIC(5, 2),
    confidence NUMERIC(5, 2)
) AS $$
BEGIN
    -- Weighted scoring system
    -- Demand: 25%, Market Growth: 15%, Competition: 15%, Profit: 20%, Sourcing: 10%, Marketing: 10%, Risk: 5%
    -- Competition inverse (lower competition is better)
    -- Risk adjustment based on seasonality

    RETURN QUERY
    SELECT
        ROUND(
            (LEAST(demand_index * 0.25, 25) +
             LEAST(market_growth_rate * 0.15, 15) +
             LEAST((10 - competition_index) * 1.5, 15) +
             LEAST(profit_margin * 0.20, 20) +
             LEAST((10 - sourcing_difficulty) * 0.10, 10) +
             LEAST(marketing_potential * 0.10, 10) +
             GREATEST(5 - ABS(market_growth_rate - 3) * 0.5, 0))::NUMERIC, 2
        ) as total_score,
        ROUND(
            (CASE
                WHEN market_growth_rate >= 5 THEN 0.95
                WHEN market_growth_rate >= 2 THEN 0.85
                WHEN market_growth_rate >= 0 THEN 0.75
                ELSE 0.65
            END) * 0.9
        )::NUMERIC as confidence;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to aggregate daily statistics
CREATE OR REPLACE FUNCTION aggregate_daily_stats(target_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    products_discovered INTEGER,
    prices_tracked INTEGER,
    opportunities_found INTEGER,
    suppliers_found INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT p.id)::INTEGER as products_discovered,
        COUNT(DISTINCT hp.id)::INTEGER as prices_tracked,
        COUNT(DISTINCT o.id)::INTEGER as opportunities_found,
        COUNT(DISTINCT s.id)::INTEGER as suppliers_found
    FROM products p
    LEFT JOIN historical_prices hp ON hp.recorded_at::DATE = target_date
    LEFT JOIN opportunity_scores o ON o.scored_at::DATE = target_date
    LEFT JOIN suppliers s ON s.created_at::DATE = target_date
    WHERE p.created_at::DATE = target_date;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

-- Materialized view for daily opportunity rankings
DROP MATERIALIZED VIEW IF EXISTS mv_daily_opportunities;
CREATE MATERIALIZED VIEW mv_daily_opportunities AS
SELECT
    DATE(CURRENT_TIMESTAMP) as report_date,
    p.id as product_id,
    p.normalized_name,
    p.category_code,
    ms.total_score,
    ms.confidence_score,
    mp.price as egypt_price,
    mp.currency as egypt_currency,
    s.name as supplier_name,
    sp.price as supplier_price,
    sp.currency as supplier_currency,
    pc.estimated_net_profit,
    pc.profit_margin,
    ROW_NUMBER() OVER (ORDER BY ms.total_score DESC) as ranking
FROM products p
INNER JOIN opportunity_scores ms ON p.id = ms.product_id
LEFT JOIN market_prices mp ON p.id = mp.product_id AND mp.is_current = TRUE
LEFT JOIN supplier_products sp ON p.id = sp.product_id
LEFT JOIN profit_calculations pc ON p.id = pc.product_id
WHERE p.is_active = TRUE
WITH NO DATA;

CREATE INDEX IF NOT EXISTS idx_mv_daily_opportunities_ranking ON mv_daily_opportunities (ranking);
CREATE INDEX IF NOT EXISTS idx_mv_daily_opportunities_category ON mv_daily_opportunities (category_code);
CREATE INDEX IF NOT EXISTS idx_mv_daily_opportunities_score ON mv_daily_opportunities (total_score DESC);

-- Materialized view for market trends
DROP MATERIALIZED VIEW IF EXISTS mv_market_trends;
CREATE MATERIALIZED VIEW mv_market_trends AS
SELECT
    c.code as category_code,
    COUNT(DISTINCT p.id) as product_count,
    AVG(ms.total_score) as avg_opportunity_score,
    AVG(mp.price) as avg_egypt_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ms.total_score) as median_score,
    COUNT(DISTINCT s.id) as active_suppliers,
    MAX(ms.scored_at) as last_scored_at,
    DATE(CURRENT_TIMESTAMP) as calculated_at
FROM categories c
LEFT JOIN products p ON c.code = p.category_code AND p.is_active = TRUE
LEFT JOIN opportunity_scores ms ON p.id = ms.product_id
LEFT JOIN market_prices mp ON p.id = mp.product_id AND mp.is_current = TRUE
LEFT JOIN supplier_products sp ON p.id = sp.product_id
LEFT JOIN suppliers s ON sp.supplier_id = s.id
GROUP BY c.code
WITH NO DATA;

CREATE INDEX IF NOT EXISTS idx_mv_trends_category ON mv_market_trends (category_code);
CREATE INDEX IF NOT EXISTS idx_mv_trends_avg_score ON mv_market_trends (avg_opportunity_score DESC);

-- ============================================================================
-- TRIGGERS FOR AUTOMATION
-- ============================================================================

-- Trigger function to refresh materialized views on new scores
CREATE OR REPLACE FUNCTION refresh_mv_daily_opportunities()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_opportunities;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_refresh_mv_opportunities
AFTER INSERT OR UPDATE ON opportunity_scores
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_mv_daily_opportunities();

-- Trigger function to update opportunity score when prices change
CREATE OR REPLACE FUNCTION update_opportunity_on_price_change()
RETURNS TRIGGER AS $$
DECLARE
    new_profit_margin NUMERIC;
    new_score RECORD;
BEGIN
    -- Recalculate profit margin if supplier or market price changes
    IF TG_OP = 'UPDATE' AND (NEW.price IS DISTINCT FROM OLD.price OR NEW.currency IS DISTINCT FROM OLD.currency) THEN
        SELECT
            o.id
        INTO new_score
        FROM opportunity_scores o
        WHERE o.product_id = NEW.product_id
        ORDER BY o.scored_at DESC
        LIMIT 1;

        IF FOUND THEN
            -- Trigger recalculation (would be called by application)
            PERFORM pg_notify('score_recalc', NEW.product_id::TEXT);
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_opportunity
AFTER UPDATE ON market_prices
FOR EACH ROW
EXECUTE FUNCTION update_opportunity_on_price_change();

-- ============================================================================
-- INDEXES FOR FULL TEXT SEARCH (SUPABASE)
-- ============================================================================

-- Create tsvector column for full text search if not exists
ALTER TABLE products ADD COLUMN IF NOT EXISTS name_search TSVECTOR;

-- Trigger to update tsvector
CREATE OR REPLACE FUNCTION products_tsvector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.name_search :=
        setweight(to_tsvector('english', coalesce(NEW.normalized_name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.brand, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(NEW.description, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE INDEX IF NOT EXISTS idx_products_name_search ON products USING GIN (name_search);
CREATE TRIGGER trigger_products_tsvector BEFORE INSERT OR UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION products_tsvector_update();

-- ============================================================================
-- SUPABASE FUNCTIONS
-- ============================================================================

-- Function to get all opportunities for daily report
CREATE OR REPLACE FUNCTION supabase_get_daily_opportunities(limit_count INTEGER DEFAULT 20)
RETURNS TABLE (
    product_id UUID,
    product_name TEXT,
    category TEXT,
    opportunity_score NUMERIC,
    profit_margin NUMERIC,
    selling_price NUMERIC,
    confidence NUMERIC,
    source_url TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.normalized_name,
        p.category_code,
        ms.total_score,
        pc.profit_margin,
        mp.price,
        ms.confidence_score,
        (SELECT url FROM source_observations so WHERE so.product_id = p.id ORDER BY so.discovery_time DESC LIMIT 1)
    FROM products p
    INNER JOIN opportunity_scores ms ON p.id = ms.product_id
    LEFT JOIN profit_calculations pc ON p.id = pc.product_id
    LEFT JOIN market_prices mp ON p.id = mp.product_id AND mp.is_current = TRUE
    WHERE p.is_active = TRUE
      AND ms.total_score >= 70
    ORDER BY ms.total_score DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to check source health
CREATE OR REPLACE FUNCTION supabase_check_source_health(source_name TEXT)
RETURNS TABLE (
    healthy BOOLEAN,
    status TEXT,
    last_check TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.is_active AND s.status = 'healthy' as healthy,
        s.status as status,
        s.last_check as last_check
    FROM sources s
    WHERE s.name = source_name;
END;
$$ LANGUAGE plpgsql;