"""
Reports API endpoints.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select, desc

from ...models.base import DailyReport, AgentExecution
from ...schemas.base import DailyReportOut, AgentExecutionOut, APIResponse
from ...core.database import get_db

reports_router = APIRouter(tags=["Reports"])


@reports_router.get("/reports/today", response_model=APIResponse)
async def get_todays_report(db: Session = Depends(get_db)):
    """Get today's daily report."""
    today = datetime.utcnow().date()

    query = select(DailyReport).where(
        DailyReport.report_date >= today,
        DailyReport.report_date < today + timedelta(days=1)
    )

    report = db.exec(query).first()

    if not report:
        return APIResponse(
            success=True,
            message="No report found for today",
            data=None,
        )

    return APIResponse(
        success=True,
        message="Today's report retrieved",
        data=report,
    )


@reports_router.get("/reports/history", response_model=APIResponse)
async def get_report_history(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """Get report history for the last N days."""
    query = select(DailyReport).order_by(desc(DailyReport.report_date)).limit(days)
    reports = db.exec(query).all()

    return APIResponse(
        success=True,
        message=f"Retrieved {len(reports)} reports",
        data=reports,
    )


@reports_router.get("/reports/{report_id}", response_model=APIResponse)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get a specific report by ID."""
    report = db.get(DailyReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return APIResponse(
        success=True,
        message="Report retrieved",
        data=report,
    )


@reports_router.get("/agents/executions", response_model=APIResponse)
async def get_agent_executions(
    agent_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get recent agent executions."""
    query = select(AgentExecution).order_by(desc(AgentExecution.started_at))

    if agent_type:
        query = query.where(AgentExecution.agent_type == agent_type)

    if status:
        query = query.where(AgentExecution.status == status)

    executions = db.exec(query.limit(limit)).all()

    return APIResponse(
        success=True,
        message=f"Retrieved {len(executions)} agent executions",
        data=executions,
    )