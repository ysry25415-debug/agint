-- Product Hunter AI - Row Level Security Policies
-- Supabase RLS Configuration for User Data Protection

-- RLS must be enabled on each table before policies work
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE telegram_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- USER POLICIES
-- ============================================================================

-- Users can SELECT their own profile (for editing)
CREATE POLICY IF NOT EXISTS "users_can_select_own" ON users
FOR SELECT
USING (auth.uid() = id);

-- Users can UPDATE their own profile
CREATE POLICY IF NOT EXISTS "users_can_update_own" ON users
FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (
    -- Prevent changing email or role without authorization
    (auth.role() = 'admin' OR OLD.role = NEW.role) AND
    (
        OLD.email = NEW.email OR
        (auth.role() = 'admin' AND NEW.email IS NOT NULL)
    )
);

-- Users can INSERT their own profile during signup
CREATE POLICY IF NOT EXISTS "users_can_insert_own" ON users
FOR INSERT
WITH CHECK (
    -- Only admins or self-creation with valid email
    auth.role() = 'admin' OR
    (auth.role() = 'anon' AND NEW.email IS NOT NULL AND NEW.is_active = TRUE)
);

-- Users can DELETE their own account (soft delete)
CREATE POLICY IF NOT EXISTS "users_can_delete_own" ON users
FOR DELETE
USING (auth.uid() = id);

-- ============================================================================
-- USER PREFERENCES POLICIES
-- ============================================================================

-- Users can read their preferences
CREATE POLICY IF NOT EXISTS "preferences_can_select_own" ON user_preferences
FOR SELECT
USING (user_id = auth.uid());

-- Users can update their preferences
CREATE POLICY IF NOT EXISTS "preferences_can_update_own" ON user_preferences
FOR UPDATE
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());

-- Users can create preferences
CREATE POLICY IF NOT EXISTS "preferences_can_insert_own" ON user_preferences
FOR INSERT
WITH CHECK (user_id = auth.uid());

-- Users can delete their preferences
CREATE POLICY IF NOT EXISTS "preferences_can_delete_own" ON user_preferences
FOR DELETE
USING (user_id = auth.uid());

-- ============================================================================
-- SESSION TOKENS POLICIES
-- ============================================================================

-- Users can see their own sessions (for session management)
CREATE POLICY IF NOT EXISTS "sessions_can_select_own" ON session_tokens
FOR SELECT
USING (user_id = auth.uid());

-- Users can create sessions (login)
CREATE POLICY IF NOT EXISTS "sessions_can_insert_own" ON session_tokens
FOR INSERT
WITH CHECK (user_id = auth.uid());

-- Users can delete their own sessions (logout)
CREATE POLICY IF NOT EXISTS "sessions_can_delete_own" ON session_tokens
FOR DELETE
USING (user_id = auth.uid());

-- Admins can manage all sessions
CREATE POLICY IF NOT EXISTS "admin_session_full_access" ON session_tokens
FOR ALL
USING (auth.role() = 'admin');

-- Sessions expire automatically
CREATE POLICY IF NOT EXISTS "expired_sessions_not_accessible" ON session_tokens
FOR ALL
USING (expires_at > NOW());

-- ============================================================================
-- TELEGRAM NOTIFICATIONS POLICIES
-- ============================================================================

-- Users can see their own notifications
CREATE POLICY IF NOT EXISTS "notifications_can_select_own" ON telegram_notifications
FOR SELECT
USING (
    user_id = auth.uid() OR
    auth.role() = 'admin' OR
    user_id IS NULL  -- Allow for bot notifications without user
);

-- Users can create notifications (for testing)
CREATE POLICY IF NOT EXISTS "notifications_can_insert_own" ON telegram_notifications
FOR INSERT
WITH CHECK (
    user_id = auth.uid() OR
    auth.role() = 'admin' OR
    user_id IS NULL
);

-- Users can update their notifications
CREATE POLICY IF NOT EXISTS "notifications_can_update_own" ON telegram_notifications
FOR UPDATE
USING (
    user_id = auth.uid() OR
    auth.role() = 'admin'
);

-- Users can delete their notifications
CREATE POLICY IF NOT EXISTS "notifications_can_delete_own" ON telegram_notifications
FOR DELETE
USING (
    user_id = auth.uid() OR
    auth.role() = 'admin'
);

-- ============================================================================
-- AUDIT LOG POLICIES (RESTRICTED)
-- ============================================================================

-- Admins can view all audit logs
CREATE POLICY IF NOT EXISTS "admin_audit_full_access" ON audit_log
FOR SELECT
USING (auth.role() = 'admin');

-- Users can see logs they created or that affect their data
CREATE POLICY IF NOT EXISTS "user_audit_can_select" ON audit_log
FOR SELECT
USING (
    user_id = auth.uid() OR
    auth.role() = 'admin'
);

-- Only admins or system can insert audit logs
CREATE POLICY IF NOT EXISTS "audit_insert_only_admin" ON audit_log
FOR INSERT
WITH CHECK (
    auth.role() = 'admin' OR
    current_user = 'supabase_internal'
);

-- Only admins can delete audit logs
CREATE POLICY IF NOT EXISTS "audit_delete_only_admin" ON audit_log
FOR DELETE
USING (auth.role() = 'admin');

-- ============================================================================
-- SUPABASE AUTH TRIGGERS
-- ============================================================================

-- Create user preferences when a new user is created
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Create default preferences for new user
    INSERT INTO user_preferences (user_id, default_category, notification_channels)
    VALUES (
        NEW.id,
        'smart_gadgets'::text,
        '{"telegram": true, "email": false}'::jsonb
    );

    -- Log user creation to audit log
    INSERT INTO audit_log (user_id, action, table_name, record_id, new_values)
    VALUES (NEW.id, 'user_created', 'users', NEW.id, row_to_json(NEW));

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Update user on profile change
CREATE OR REPLACE FUNCTION public.handle_user_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Log profile updates
    INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, new_values)
    VALUES (
        NEW.id,
        'user_updated',
        'users',
        NEW.id,
        row_to_json(OLD),
        row_to_json(NEW)
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_updated ON auth.users;
CREATE TRIGGER on_auth_user_updated
    AFTER UPDATE ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_user_update();

-- ============================================================================
-- SECURITY FUNCTIONS
-- ============================================================================

-- Function to check if user has admin role
CREATE OR REPLACE FUNCTION is_admin(user_uid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM users
        WHERE id = user_uid AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if user is viewing their own data
CREATE OR REPLACE FUNCTION is_self_or_admin(user_uid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM users
        WHERE id = user_uid AND (role = 'admin' OR id = auth.uid())
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to sanitize input for product names
CREATE OR REPLACE FUNCTION sanitize_product_name(input_name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN REGEXP_REPLACE(
        LOWER(TRIM(input_name)),
        '[^a-z0-9\s\-_]',
        '',
        'g'
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to calculate profit margin (helper)
CREATE OR REPLACE FUNCTION calculate_profit_margin(
    purchase_price NUMERIC,
    selling_price NUMERIC,
    costs JSONB DEFAULT '{}'
) RETURNS NUMERIC(8, 2) AS $$
DECLARE
    total_costs NUMERIC := COALESCE(costs->>'shipping', 0)::NUMERIC +
                          COALESCE(costs->>'customs', 0)::NUMERIC +
                          COALESCE(costs->>'delivery', 0)::NUMERIC +
                          COALESCE(costs->>'marketing', 0)::NUMERIC;
    net_profit NUMERIC;
BEGIN
    IF selling_price = 0 THEN
        RETURN 0;
    END IF;

    net_profit := selling_price - purchase_price - total_costs;
    RETURN ROUND((net_profit / selling_price) * 100, 2);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEW DEFINITIONS
-- ============================================================================

-- Main product view with scores and prices
CREATE OR REPLACE VIEW v_product_insights AS
SELECT
    p.id as product_id,
    p.normalized_name,
    p.brand,
    p.category_code,
    p.description,
    p.image_url,
    p.created_at as first_seen,
    COALESCE(ms.total_score, 0) as opportunity_score,
    ms.confidence_score,
    ms.demand_signals_score,
    ms.market_growth_score,
    ms.competition_score,
    ms.profit_potential_score,
    ms.sourcing_feasibility_score,
    ms.marketing_potential_score,
    ms.risk_seasonality_score,
    mp.price as current_egypt_price,
    mp.currency as price_currency,
    mp.url as price_source,
    COUNT(DISTINCT po.id) as source_observations,
    COUNT(DISTINCT sp.id) as available_suppliers,
    AVG(sp.price) as avg_supplier_price,
    MIN(sp.price) as min_supplier_price,
    MAX(po.likes) as max_likes,
    MAX(po.shares) as max_shares,
    -- Top source URL
    (SELECT url FROM source_observations so
     WHERE so.product_id = p.id
     ORDER BY so.discovery_time DESC
     LIMIT 1) as top_source_url
FROM products p
LEFT JOIN opportunity_scores ms ON p.id = ms.product_id
LEFT JOIN market_prices mp ON p.id = mp.product_id AND mp.is_current = TRUE
LEFT JOIN source_observations po ON p.id = po.product_id
LEFT JOIN supplier_products sp ON p.id = sp.product_id
WHERE p.is_active = TRUE
GROUP BY p.id, ms.id, mp.id
ORDER BY ms.total_score DESC NULLS LAST;

-- Trending products view
CREATE OR REPLACE VIEW v_trending_products AS
SELECT
    p.id,
    p.normalized_name,
    p.brand,
    p.category_code,
    ms.total_score,
    ms.scored_at,
    mp.price as egypt_price,
    mp.currency,
    mp.url as price_url,
    pc.estimated_net_profit,
    pc.profit_margin
FROM products p
INNER JOIN opportunity_scores ms ON p.id = ms.product_id
LEFT JOIN market_prices mp ON p.id = mp.product_id AND mp.is_current = TRUE
LEFT JOIN profit_calculations pc ON p.id = pc.product_id
WHERE p.is_active = TRUE
  AND ms.scored_at >= NOW() - INTERVAL '7 days'
  AND ms.total_score >= 75
ORDER BY ms.total_score DESC
LIMIT 50;

-- Admin dashboard statistics view
CREATE OR REPLACE VIEW v_admin_stats AS
SELECT
    (SELECT COUNT(*) FROM products WHERE is_active = TRUE) as total_products,
    (SELECT COUNT(*) FROM products WHERE is_active = FALSE) as archived_products,
    (SELECT COUNT(*) FROM opportunity_scores WHERE scored_at >= NOW() - INTERVAL '24 hours') as scores_today,
    (SELECT COUNT(*) FROM historical_prices WHERE recorded_at >= NOW() - INTERVAL '24 hours') as prices_tracked_today,
    (SELECT COUNT(*) FROM supplier_products) as total_supplier_products,
    (SELECT COUNT(*) FROM sources WHERE is_active = TRUE AND status = 'healthy') as healthy_sources,
    (SELECT COUNT(*) FROM sources WHERE is_active = TRUE) as total_active_sources,
    (SELECT COUNT(*) FROM agent_executions WHERE status = 'completed' AND started_at >= NOW() - INTERVAL '24 hours') as agents_completed_today,
    (SELECT ROUND(AVG(total_score)::numeric, 2) FROM opportunity_scores) as avg_opportunity_score,
    (SELECT MAX(profit_margin) FROM profit_calculations WHERE profit_margin IS NOT NULL) as max_profit_margin,
    -- Last refresh time
    (NOW()::text) as last_calculated;