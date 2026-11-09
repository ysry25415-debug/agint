"""
Database migration utilities for Product Hunter AI.
Provides functions to run migrations and manage database schema.
"""

import os
from pathlib import Path
from typing import List, Optional
from sqlalchemy import text, create_engine, inspect
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "backend" / "migrations"


class MigrationRunner:
    """Manages database migrations."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.inspected = False
        self._inspector = None

    @property
    def inspector(self):
        if not self._inspector:
            self._inspector = inspect(self.engine)
        return self._inspector

    def get_table_names(self) -> List[str]:
        """Get list of existing table names."""
        return self.inspector.get_table_names()

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        return table_name in self.get_table_names()

    def run_migration_file(self, migration_path: Path) -> bool:
        """
        Execute a SQL migration file.

        Args:
            migration_path: Path to the .sql file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(migration_path, 'r') as f:
                sql_content = f.read()

            with self.engine.connect() as conn:
                # Split by semicolons for multiple statements
                statements = [
                    s.strip() for s in sql_content.split(';')
                    if s.strip() and not s.strip().startswith('--')
                ]

                for statement in statements:
                    if statement:
                        try:
                            conn.execute(text(statement))
                            conn.commit()
                        except Exception as stmt_error:
                            logger.error(f"Statement failed: {stmt_error}")
                            conn.rollback()
                            raise

            logger.info(f"Migration {migration_path.name} completed successfully")
            return True

        except Exception as e:
            logger.error(f"Migration {migration_path.name} failed: {e}")
            return False

    def run_pending_migrations(self) -> dict:
        """
        Run all pending migrations.

        Returns:
            Dict with migration results
        """
        results = {
            'total': 0,
            'applied': 0,
            'skipped': 0,
            'failed': 0,
            'errors': []
        }

        # Get all migration files in order
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        for migration_file in migration_files:
            results['total'] += 1

            # Check if this is an initial migration vs incremental
            if migration_file.name == "001_initial_schema.sql":
                # For initial schema, create tables if they don't exist
                if not self.table_exists('products'):
                    success = self.run_migration_file(migration_file)
                else:
                    results['skipped'] += 1
                    continue
            else:
                # Other migrations can be applied normally
                success = self.run_migration_file(migration_file)

            if success:
                results['applied'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(str(migration_file.name))

        return results

    def check_schema_version(self) -> Optional[int]:
        """Check current schema version."""
        # This would be implemented with a schema_versions table
        # For now, check if key tables exist
        key_tables = ['products', 'sources', 'opportunity_scores']
        existing = [t for t in key_tables if self.table_exists(t)]

        if len(existing) == len(key_tables):
            return 3  # Latest schema version
        return None

    def verify_integrity(self) -> dict:
        """
        Verify database integrity.

        Returns:
            Dict with integrity check results
        """
        results = {
            'tables_ok': True,
            'indexes_ok': True,
            'rls_enabled': True,
            'issues': []
        }

        expected_tables = [
            'products', 'product_variants', 'sources', 'source_observations',
            'historical_prices', 'market_prices', 'competitors',
            'competitor_products', 'suppliers', 'supplier_products',
            'opportunity_scores', 'daily_reports', 'report_items',
            'agent_executions', 'profit_calculations', 'users',
            'user_preferences', 'telegram_notifications', 'session_tokens',
            'audit_log', 'categories', 'trend_history'
        ]

        existing_tables = self.get_table_names()

        for table in expected_tables:
            if table not in existing_tables:
                results['tables_ok'] = False
                results['issues'].append(f"Missing table: {table}")

        return results


def create_database_views(session: Session) -> None:
    """Create database views if they don't exist."""
    views_sql = """
    CREATE OR REPLACE VIEW v_product_summary AS
    SELECT
        p.id as product_id,
        p.normalized_name,
        p.brand,
        c.name as category_name,
        p.image_url,
        p.created_at,
        COALESCE(ms.total_score, 0) as opportunity_score,
        COUNT(DISTINCT po.id) as observation_count
    FROM products p
    LEFT JOIN opportunity_scores ms ON p.id = ms.product_id
    LEFT JOIN categories c ON p.category_code = c.code
    LEFT JOIN source_observations po ON p.id = po.product_id
    WHERE p.is_active = TRUE
    GROUP BY p.id, c.name, ms.total_score
    ORDER BY ms.total_score DESC NULLS LAST
    LIMIT 100;
    """

    session.execute(text(views_sql))
    session.commit()


def init_database(database_url: str) -> bool:
    """
    Initialize the database with migrations.

    Args:
        database_url: Database connection string

    Returns:
        True if successful
    """
    runner = MigrationRunner(database_url)

    try:
        # Check current state
        schema_version = runner.check_schema_version()
        integrity = runner.verify_integrity()

        if schema_version is None:
            logger.info("Database needs initialization")

            # Run all migrations
            results = runner.run_pending_migrations()

            logger.info(f"Migration results: {results}")

            if results['failed'] > 0:
                logger.error(f"Migrations failed: {results['errors']}")
                return False

            return True

        elif schema_version >= 3:
            logger.info("Database is up to date")
            return True

        else:
            logger.warning(f"Schema version {schema_version} needs updating")
            results = runner.run_pending_migrations()

            if results['failed'] > 0:
                logger.error(f"Migrations failed: {results['errors']}")
                return False

            return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


# SQL function to record migration versions
RECORDS_MIGRATION_VERSION = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    checksum VARCHAR(64)
);
"""

RECORDS_MIGRATION_APPLIED = """
INSERT INTO schema_migrations (version, name, checksum)
VALUES (:version, :name, :checksum)
ON CONFLICT (version) DO NOTHING;
"""

if __name__ == "__main__":
    import sys
    from backend.app.core.config import settings

    database_url = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

    success = init_database(database_url)
    sys.exit(0 if success else 1)