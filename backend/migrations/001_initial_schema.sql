-- Product Hunter AI - Initial Database Schema
-- Supabase PostgreSQL with Row Level Security
-- Generated: 2026-11-09

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- TABLES
-- ============================================================================

-- Category lookup table (normalized)
CREATE TABLE IF NOT EXISTS categories (
    code VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert category codes
INSERT INTO categories (code, name, description) VALUES
    ('smart_gadgets', 'Smart Gadgets', 'Smartphones, tablets, wearables'),
    ('mobile_accessories', 'Mobile Accessories', 'Cases, chargers, accessories'),
    ('pc_gaming_accessories', 'PC & Gaming Accessories', 'Keyboards, mice, monitors'),
    ('smart_home', 'Smart Home Devices', 'Smart speakers, security, automation'),
    ('audio_electronics', 'Audio Electronics', 'Headphones, speakers, audio gear'),
    ('personal_technology', 'Personal Technology', 'Laptops, tablets, personal devices'),
    ('innovative_products', 'Innovative Products', 'Breakthrough tech products'),
    ('portable_devices', 'Portable Electronic Devices', 'Travel gadgets, portable chargers')
ON CONFLICT (code) DO NOTHING;

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_platform VARCHAR(100) NOT NULL CHECK (source_platform IN ('alibaba', '1688', 'aliexpress', 'madeinchina')),
    platform_product_id VARCHAR(100) NOT NULL,
    supplier_id VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    location VARCHAR(200),
    minimum_order VARCHAR(100),
    delivery_time VARCHAR(100),
    shipping_cost NUMERIC(12, 4),
    shipping_currency VARCHAR(3) DEFAULT 'USD',
    rating NUMERIC(3, 2),
    review_count INTEGER,
    response_time VARCHAR(50),
    is_verified BOOLEAN DEFAULT FALSE,
    is_top_rated BOOLEAN DEFAULT FALSE,
    company_description TEXT,
    response_rate VARCHAR(50),
    annual_revenue VARCHAR(100),
    employees INTEGER,
    verification_status VARCHAR(50),
    verified_date TIMESTAMP WITH TIME ZONE,
    website VARCHAR(200),
    contact_info JSONB,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    products_count INTEGER DEFAULT 0,

    CONSTRAINT uk_supplier_platform_product UNIQUE (source_platform, platform_product_id),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_suppliers_platform_product ON suppliers (source_platform, platform_product_id);
CREATE INDEX IF NOT EXISTS idx_suppliers_country ON suppliers (country);
CREATE INDEX IF NOT EXISTS idx_suppliers_rating ON suppliers (rating DESC);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    normalized_name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),
    model_number VARCHAR(100),
    category_code VARCHAR(50) NOT NULL REFERENCES categories(code),
    description TEXT,
    specifications JSONB,
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_products_category FOREIGN KEY (category_code) REFERENCES categories(code)
);

CREATE INDEX IF NOT EXISTS idx_products_normalized_name ON products USING gin (to_tsvector('english', normalized_name));
CREATE INDEX IF NOT EXISTS idx_products_brand ON products (brand);
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category_code);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products (created_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_products_unique_normalized ON products (normalized_name, brand);

-- Product variants table
CREATE TABLE IF NOT EXISTS product_variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(100) UNIQUE,
    color VARCHAR(50),
    storage VARCHAR(50),
    memory VARCHAR(50),
    specifications JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_variants_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_variants_product ON product_variants (product_id);
CREATE INDEX IF NOT EXISTS idx_variants_sku ON product_variants (sku);

-- Data sources table
CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('marketplace', 'social_media', 'supplier', 'aggregator')),
    api_endpoint TEXT,
    country_focus VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    auth_method VARCHAR(50) DEFAULT 'api_key',
    rate_limit INTEGER DEFAULT 60,
    last_check TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'unknown' CHECK (status IN ('healthy', 'degraded', 'down', 'unknown')),
    error_message TEXT,
    api_key_encrypted BYTEA,
    config JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sources_name ON sources (name);
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources (type);
CREATE INDEX IF NOT EXISTS idx_sources_status ON sources (status);

-- Source observations table
CREATE TABLE IF NOT EXISTS source_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    discovery_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    url TEXT NOT NULL,
    title VARCHAR(500),
    author VARCHAR(200),
    price NUMERIC(12, 4),
    currency VARCHAR(3) DEFAULT 'USD',
    availability VARCHAR(100),
    stock_level VARCHAR(50),
    likes INTEGER,
    shares INTEGER,
    comments INTEGER,
    views INTEGER,
    rank_position INTEGER,
    rank_type VARCHAR(50),
    raw_data JSONB,
    extracted_by VARCHAR(100),
    country VARCHAR(100),
    source_product_id VARCHAR(255),

    CONSTRAINT fk_observations_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
    CONSTRAINT fk_observations_source FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_observations_product ON source_observations (product_id);
CREATE INDEX IF NOT EXISTS idx_observations_source ON source_observations (source_id);
CREATE INDEX IF NOT EXISTS idx_observations_discovery_time ON source_observations (discovery_time DESC);
CREATE INDEX IF NOT EXISTS idx_observations_url ON source_observations (url);
CREATE UNIQUE INDEX IF NOT EXISTS idx_observations_unique_url_source ON source_observations (url, source_id);

-- Historical prices table (for tracking price changes)
CREATE TABLE IF NOT EXISTS historical_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    marketplace VARCHAR(100),
    price NUMERIC(12, 4) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    recorded_by VARCHAR(100),

    CONSTRAINT fk_hist_prices_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT fk_hist_prices_source FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hist_prices_product_time ON historical_prices (product_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_hist_prices_source_time ON historical_prices (source_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_hist_prices_marketplace ON historical_prices (marketplace);

-- Current market prices (Egyptian marketplaces)
CREATE TABLE IF NOT EXISTS market_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    marketplace VARCHAR(100) NOT NULL,
    price NUMERIC(12, 4) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'EGP',
    url TEXT,
    available BOOLEAN DEFAULT TRUE,
    shipping_info VARCHAR(200),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_current BOOLEAN DEFAULT TRUE,

    CONSTRAINT fk_market_prices_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_market_prices_product ON market_prices (product_id);
CREATE INDEX IF NOT EXISTS idx_market_prices_marketplace ON market_prices (marketplace);
CREATE INDEX IF NOT EXISTS idx_market_prices_current ON market_prices (is_current);

-- Competitors table
CREATE TABLE IF NOT EXISTS competitors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    brand VARCHAR(100),
    country VARCHAR(100) DEFAULT 'EG',
    website VARCHAR(200),
    social_followers INTEGER,
    monthly_visitors INTEGER,
    average_price NUMERIC(12, 4),
    price_range VARCHAR(100),
    founded_year INTEGER,
    description TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_competitors_name ON competitors (name);
CREATE INDEX IF NOT EXISTS idx_competitors_brand ON competitors (brand);

-- Competitor products table
CREATE TABLE IF NOT EXISTS competitor_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_id UUID NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
    product_name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255) NOT NULL,
    category_code VARCHAR(50) REFERENCES categories(code),
    price NUMERIC(12, 4),
    currency VARCHAR(3) DEFAULT 'EGP',
    availability VARCHAR(50),
    rating NUMERIC(3, 2),
    review_count INTEGER,
    url VARCHAR(500),
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_comp_product_competitor FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_comp_products_competitor ON competitor_products (competitor_id);
CREATE INDEX IF NOT EXISTS idx_comp_products_normalized_name ON competitor_products (normalized_name);
CREATE UNIQUE INDEX IF NOT EXISTS idx_comp_products_unique ON competitor_products (competitor_id, normalized_name);

-- Supplier products table
CREATE TABLE IF NOT EXISTS supplier_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    product_name VARCHAR(500) NOT NULL,
    normalized_name VARCHAR(500) NOT NULL,
    price NUMERIC(12, 4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    price_usd NUMERIC(12, 4),
    category_code VARCHAR(50) REFERENCES categories(code),
    specifications JSONB,
    stock_status VARCHAR(50),
    minimum_order_quantity INTEGER,
    package_details VARCHAR(500),
    url TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_price_update TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_supplier_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_supplier_products_normalized_name ON supplier_products (normalized_name);
CREATE INDEX IF NOT EXISTS idx_supplier_products_supplier ON supplier_products (supplier_id);
CREATE INDEX IF NOT EXISTS idx_supplier_products_price ON supplier_products (price);

-- Trend history table
CREATE TABLE IF NOT EXISTS trend_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_code VARCHAR(50) NOT NULL REFERENCES categories(code),
    trend_type VARCHAR(50) NOT NULL CHECK (trend_type IN ('search', 'social', 'video', 'ad', 'marketplace')),
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC(12, 4) NOT NULL,
    previous_value NUMERIC(12, 4),
    change_percent NUMERIC(8, 2),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    recorded_by VARCHAR(100),

    CONSTRAINT fk_trends_category FOREIGN KEY (category_code) REFERENCES categories(code) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_trends_category_time ON trend_history (category_code, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_trends_metric ON trend_history (metric_name, metric_value DESC);

-- Opportunity scores table
CREATE TABLE IF NOT EXISTS opportunity_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    scored_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_score NUMERIC(5, 2) NOT NULL,
    confidence_score NUMERIC(5, 2),

    -- Score breakdown (weights applied)
    demand_signals_score NUMERIC(5, 2),
    market_growth_score NUMERIC(5, 2),
    competition_score NUMERIC(5, 2),
    profit_potential_score NUMERIC(5, 2),
    sourcing_feasibility_score NUMERIC(5, 2),
    marketing_potential_score NUMERIC(5, 2),
    risk_seasonality_score NUMERIC(5, 2),

    -- Raw score components
    demand_signals_raw NUMERIC(5, 2),
    market_growth_raw NUMERIC(5, 2),
    competition_raw NUMERIC(5, 2),
    profit_potential_raw NUMERIC(5, 2),
    sourcing_feasibility_raw NUMERIC(5, 2),
    marketing_potential_raw NUMERIC(5, 2),
    risk_seasonality_raw NUMERIC(5, 2),

    scored_by VARCHAR(100) NOT NULL,
    scoring_details JSONB,

    CONSTRAINT fk_scores_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_scores_product ON opportunity_scores (product_id);
CREATE INDEX IF NOT EXISTS idx_scores_total_score ON opportunity_scores (total_score DESC);
CREATE INDEX IF NOT EXISTS idx_scores_scored_at ON opportunity_scores (scored_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_scores_unique_product ON opportunity_scores (product_id);

-- Agent executions table
CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN ('global_discovery', 'social_trends', 'egyptian_market', 'competitor_analysis', 'supplier_discovery', 'profit_calculation', 'product_scoring', 'report_generation')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'retried')),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds NUMERIC(10, 3),
    items_processed INTEGER,
    items_created INTEGER,
    items_updated INTEGER,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    source_stats JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_executions_type_time ON agent_executions (agent_type, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions (status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at ON agent_executions (created_at DESC);

-- Profit calculations table
CREATE TABLE IF NOT EXISTS profit_calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    supplier_purchase_price NUMERIC(12, 4) NOT NULL,
    supplier_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    currency_conversion_rate NUMERIC(12, 6) DEFAULT 1.0,
    international_shipping NUMERIC(12, 4) DEFAULT 0.0,
    shipping_currency VARCHAR(3) DEFAULT 'USD',
    customs_duty_rate NUMERIC(5, 2) DEFAULT 0.0,
    customs_duty_amount NUMERIC(12, 4) DEFAULT 0.0,
    customs_fee FIXED(12, 4) DEFAULT 0.0,
    local_delivery_cost NUMERIC(12, 4) DEFAULT 0.0,
    marketing_costs NUMERIC(12, 4) DEFAULT 0.0,
    estimated_selling_price NUMERIC(12, 4) NOT NULL,
    selling_currency VARCHAR(3) NOT NULL DEFAULT 'EGP',
    gross_profit NUMERIC(12, 4),
    estimated_net_profit NUMERIC(12, 4),
    profit_margin NUMERIC(8, 2),
    currency_conversion_date TIMESTAMP WITH TIME ZONE,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    calculated_by VARCHAR(100) NOT NULL,
    calculation_notes TEXT,

    CONSTRAINT fk_profit_calc_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT fk_profit_calc_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_profit_calc_product ON profit_calculations (product_id);
CREATE INDEX IF NOT EXISTS idx_profit_calc_profit_margin ON profit_calculations (profit_margin DESC);
CREATE INDEX IF NOT EXISTS idx_profit_calc_net_profit ON profit_calculations (estimated_net_profit DESC);
CREATE INDEX IF NOT EXISTS idx_profit_calc_calculated_at ON profit_calculations (calculated_at DESC);

-- Daily reports table
CREATE TABLE IF NOT EXISTS daily_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'sent', 'failed')),
    total_products INTEGER DEFAULT 0,
    report_data JSONB,
    summary TEXT,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    telegram_message_id VARCHAR(50),
    telegram_chat_id VARCHAR(50),
    report_type VARCHAR(50) DEFAULT 'daily'
);

CREATE INDEX IF NOT EXISTS idx_reports_date ON daily_reports (report_date DESC);
CREATE INDEX IF NOT EXISTS idx_reports_status ON daily_reports (status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_reports_unique_date ON daily_reports (report_date);

-- Report items table
CREATE TABLE IF NOT EXISTS report_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    opportunity_score NUMERIC(5, 2),
    profit_margin NUMERIC(8, 2),
    profit_estimate NUMERIC(12, 4),
    ranking INTEGER,
    notes TEXT,

    CONSTRAINT fk_report_items_report FOREIGN KEY (report_id) REFERENCES daily_reports(id) ON DELETE CASCADE,
    CONSTRAINT fk_report_items_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_report_items_report ON report_items (report_id);
CREATE INDEX IF NOT EXISTS idx_report_items_product ON report_items (product_id);
CREATE INDEX IF NOT EXISTS idx_report_items_ranking ON report_items (ranking);

-- User accounts table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'analyst', 'viewer', 'bot')),
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users (is_active);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    default_category VARCHAR(50) REFERENCES categories(code),
    notification_channels JSONB DEFAULT '{"telegram": true, "email": false}',
    preferred_sources JSONB,
    price_alert_threshold NUMERIC(8, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Telegram notifications table
CREATE TABLE IF NOT EXISTS telegram_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    message_type VARCHAR(50) NOT NULL CHECK (message_type IN ('report', 'alert', 'opportunity', 'status')),
    chat_id VARCHAR(50) NOT NULL,
    message_id VARCHAR(50),
    content JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed', 'delivered')),
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    retry_count INTEGER DEFAULT 0,

    CONSTRAINT fk_telegram_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_tg_notif_chat_id ON telegram_notifications (chat_id);
CREATE INDEX IF NOT EXISTS idx_tg_notif_status ON telegram_notifications (status);
CREATE INDEX IF NOT EXISTS idx_tg_notif_type_time ON telegram_notifications (message_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tg_notif_user ON telegram_notifications (user_id);

-- Session tokens table (for API authentication)
CREATE TABLE IF NOT EXISTS session_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,

    CONSTRAINT fk_session_tokens_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_session_tokens_user ON session_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_session_tokens_expires ON session_tokens (expires_at);
CREATE INDEX IF NOT EXISTS idx_session_tokens_token_hash ON session_tokens (token_hash);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_audit_log_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log (table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action_time ON audit_log (action, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log (created_at DESC);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamps trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitors_updated_at BEFORE UPDATE ON competitors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on user-sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE telegram_notifications ENABLE ROW LEVEL SECURITY;

-- Users can only access their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (id = auth.uid());

-- Users can update own profile
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (id = auth.uid());

-- Users can view own preferences
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING (user_id = auth.uid());

-- Users can update own preferences
CREATE POLICY "Users can update own preferences" ON user_preferences
    FOR ALL USING (user_id = auth.uid());

-- Users can view their telegram notifications
CREATE POLICY "Users can view own notifications" ON telegram_notifications
    FOR SELECT USING (
        auth.uid() IS NULL OR user_id = auth.uid()
    );

-- Users can insert their own telegram notifications
CREATE POLICY "Users can insert notifications" ON telegram_notifications
    FOR INSERT WITH CHECK (
        auth.uid() IS NULL OR user_id = auth.uid()
    );

-- Users can only view audit logs they created or their records
CREATE POLICY "Users can view related audit logs" ON audit_log
    FOR SELECT USING (
        auth.uid() = user_id OR auth.role() = 'admin'
    );

-- Admins can access all data
CREATE POLICY "Admins can access all users" ON users
    FOR ALL USING (auth.role() = 'admin');

CREATE POLICY "Admins can access all session tokens" ON session_tokens
    FOR ALL USING (auth.role() = 'admin');

CREATE POLICY "Admins can access all audit logs" ON audit_log
    FOR ALL USING (auth.role() = 'admin');

-- Auth users can manage their own sessions
CREATE POLICY "Users can manage own sessions" ON session_tokens
    FOR ALL USING (user_id = auth.uid());

-- Admins can manage all sessions
CREATE POLICY "Admins can manage all sessions" ON session_tokens
    FOR ALL USING (auth.role() = 'admin');

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for product summary with latest scores and prices
CREATE OR REPLACE VIEW v_product_summary AS
SELECT
    p.id as product_id,
    p.normalized_name,
    p.brand,
    p.category_code,
    p.image_url,
    p.created_at,
    COALESCE(ms.total_score, 0) as opportunity_score,
    ms.confidence_score,
    mp.price as egypt_price,
    mp.currency as egypt_currency,
    COUNT(DISTINCT po.id) as observation_count,
    MAX(hp.price) as highest_price,
    MIN(hp.price) as lowest_price,
    COUNT(DISTINCT sp.id) as supplier_count
FROM products p
LEFT JOIN opportunity_scores ms ON p.id = ms.product_id
LEFT JOIN market_prices mp ON p.id = mp.product_id AND mp.is_current = TRUE
LEFT JOIN source_observations po ON p.id = po.product_id
LEFT JOIN historical_prices hp ON p.id = hp.product_id
LEFT JOIN supplier_products sp ON p.id = sp.product_id
WHERE p.is_active = TRUE
GROUP BY p.id, ms.id, mp.id
ORDER BY ms.total_score DESC NULLS LAST, p.created_at DESC;