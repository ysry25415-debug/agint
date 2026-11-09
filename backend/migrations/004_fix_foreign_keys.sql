-- Product Hunter AI - Schema Fix Migration
-- Fixes erroneous foreign key constraints in initial schema

-- ============================================================================
-- FIX 1: agent_executions - Remove erroneous FK to products
-- ============================================================================

-- The agent_executions should not have a FK to products
-- The constraint was incorrectly defined in 001_initial_schema.sql

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'agent_executions'::regclass
          AND contype = 'f'
          AND confrelid = 'products'::regclass
    ) THEN
        ALTER TABLE agent_executions
            DROP CONSTRAINT IF EXISTS fk_agent_executions;
        RAISE NOTICE 'Dropped erroneous FK: agent_executions -> products';
    END IF;
END $$;


-- ============================================================================
-- FIX 2: daily_reports - Remove erroneous FK to products
-- ============================================================================

-- The daily_reports should not have a FK to products
-- Reports are independent entities

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'daily_reports'::regclass
          AND contype = 'f'
          AND confrelid = 'products'::regclass
    ) THEN
        ALTER TABLE daily_reports
            DROP CONSTRAINT IF EXISTS fk_reports_id;
        RAISE NOTICE 'Dropped erroneous FK: daily_reports -> products';
    END IF;
END $$;


-- ============================================================================
-- ADDITIONAL INDEXES FOR PERFORMANCE
-- ============================================================================

-- Index for faster audit log queries by action
CREATE INDEX IF NOT EXISTS idx_audit_log_action_created_at ON audit_log (action, created_at DESC);

-- Index for user login tracking
CREATE INDEX IF NOT EXISTS idx_session_tokens_expires_at ON session_tokens (expires_at DESC);

-- Partial index for active users
CREATE INDEX IF NOT EXISTS idx_users_active_email ON users (email) WHERE is_active = TRUE;


-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- This migration:
-- ✅ Removed erroneous FK: agent_executions.id -> products.id
-- ✅ Removed erroneous FK: daily_reports.id -> products.id
-- ✅ Added performance indexes for audit logging and session management