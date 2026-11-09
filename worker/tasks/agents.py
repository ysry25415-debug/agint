"""
Celery tasks for running AI agents.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

from backend.app.core.database import SessionLocal, get_db
from backend.app.models.base import (
    AgentExecution, Product, Source, DailyReport,
    AgentType, ExecutionStatus
)
from backend.app.core.logging_config import get_logger

logger = get_logger(__name__)


def _log_execution(agent_type: str, status: str, **kwargs) -> None:
    """Log agent execution to database."""
    db = SessionLocal()
    try:
        execution = AgentExecution(
            agent_type=agent_type,
            status=status,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow() if status in ["completed", "failed", "retried"] else None,
            **kwargs
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
    except Exception as e:
        logger.error(f"Failed to log execution: {e}")
        db.rollback()
    finally:
        db.close()


def _run_agent(agent_type: AgentType, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute a specific agent with retry logic.

    This is a placeholder for actual agent implementation.
    Each agent will be implemented in its own module.
    """
    from worker.tasks.retry import execute_with_retry

    def _agent_action():
        # Import and execute the specific agent
        if agent_type == AgentType.GLOBAL_DISCOVERY:
            from worker.tasks.agents.global_discovery import run_global_discovery
            return run_global_discovery(data or {})

        elif agent_type == AgentType.SOCIAL_TRENDS:
            from worker.tasks.agents.social_trends import run_social_trends_analysis
            return run_social_trends_analysis(data or {})

        elif agent_type == AgentType.EGYPTIAN_MARKET:
            from worker.tasks.agents.egyptian_market import run_egyptian_market_analysis
            return run_egyptian_market_analysis(data or {})

        elif agent_type == AgentType.COMPETITOR_ANALYSIS:
            from worker.tasks.agents.competitor_analysis import run_competitor_analysis
            return run_competitor_analysis(data or {})

        elif agent_type == AgentType.SUPPLIER_DISCOVERY:
            from worker.tasks.agents.supplier_discovery import run_supplier_discovery
            return run_supplier_discovery(data or {})

        elif agent_type == AgentType.PROFIT_CALCULATION:
            from worker.tasks.agents.profit_calculation import run_profit_calculation
            return run_profit_calculation(data or {})

        elif agent_type == AgentType.PRODUCT_SCORING:
            from worker.tasks.agents.product_scoring import run_product_scoring
            return run_product_scoring(data or {})

        elif agent_type == AgentType.REPORT_GENERATION:
            from worker.tasks.agents.report_generation import run_report_generation
            return run_report_generation(data or {})

        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    return execute_with_retry(_agent_action, agent_type.value, max_retries=3)


async def run_daily_pipeline() -> Dict[str, Any]:
    """
    Execute the complete daily research pipeline.

    This orchestrates all agents in the correct order for daily product discovery.
    """
    start_time = datetime.utcnow()
    result = {"status": "started", "agents_executed": 0, "products_found": 0}

    try:
        logger.info("Starting daily research pipeline")

        # 1. Global Product Discovery
        discovery_result = _run_agent(AgentType.GLOBAL_DISCOVERY)
        result["agents_executed"] += 1

        # 2. Social Trends Analysis
        trends_result = _run_agent(AgentType.SOCIAL_TRENDS)
        result["agents_executed"] += 1

        # 3. Egyptian Market Research
        market_result = _run_agent(AgentType.EGYPTIAN_MARKET)
        result["agents_executed"] += 1

        # 4. Competitor Analysis
        competitor_result = _run_agent(AgentType.COMPETITOR_ANALYSIS)
        result["agents_executed"] += 1

        # 5. Supplier Discovery
        supplier_result = _run_agent(AgentType.SUPPLIER_DISCOVERY)
        result["agents_executed"] += 1

        # 6. Profit Calculation
        profit_result = _run_agent(AgentType.PROFIT_CALCULATION)
        result["agents_executed"] += 1

        # 7. Product Scoring
        scoring_result = _run_agent(AgentType.PRODUCT_SCORING)
        result["agents_executed"] += 1

        # 8. Daily Report Generation
        report_result = _run_agent(AgentType.REPORT_GENERATION)
        result["agents_executed"] += 1
        result["status"] = "completed"

        # Count total products found
        db = SessionLocal()
        try:
            products_count = db.query(Product).count()
            result["products_found"] = products_count
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Daily pipeline failed: {e}")
        result["status"] = "failed"
        result["error"] = str(e)

    return result


async def health_check_sources() -> Dict[str, Any]:
    """Check health of all data sources."""
    db = SessionLocal()
    try:
        sources = db.query(Source).filter(Source.is_active == True).all()
        results = {"total": len(sources), "healthy": 0, "degraded": 0, "down": 0}

        for source in sources:
            # Update source status based on last check
            # This would call the actual source connector
            if source.status == "healthy":
                results["healthy"] += 1
            elif source.status == "degraded":
                results["degraded"] += 1
            else:
                results["down"] += 1

        return results
    finally:
        db.close()


async def update_market_prices() -> Dict[str, Any]:
    """Update current market prices from Egyptian marketplaces."""
    result = {"updated_prices": 0, "sources_touched": []}

    # This would call the marketplace connectors
    # and update the market_prices table

    return result


async def generate_daily_report() -> Dict[str, Any]:
    """Generate the daily report for Telegram and Web."""
    result = {"status": "created"}

    # Get top opportunities
    # Create daily report record
    # Send to Telegram

    return result


# Celery task decorators
from celery import current_task


def execute_with_retry(func, task_name: str, max_retries: int = 3):
    """Execute a function with retry logic and logging."""
    attempt = 0
    last_error = None

    while attempt <= max_retries:
        try:
            result = func()
            if attempt > 0:
                logger.info(f"Task {task_name} succeeded on attempt {attempt + 1}")
            return result
        except Exception as e:
            attempt += 1
            last_error = e
            logger.warning(f"Task {task_name} failed on attempt {attempt}: {e}")

            if attempt > max_retries:
                logger.error(f"Task {task_name} failed after {max_retries} retries")
                raise

    return result