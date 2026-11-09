"""
Sources API endpoints.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlmodel import Session, select

from ...models.base import Source
from ...schemas.base import SourceOut, APIResponse
from ...core.database import get_db

router = APIRouter(tags=["Sources"])


@router.get("/sources", response_model=APIResponse)
async def list_sources(
    type: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """
    List data sources with filtering.
    """
    query = select(Source)

    if type:
        query = query.where(Source.type == type)

    if active_only:
        query = query.where(Source.is_active == True)

    sources = db.exec(query).all()

    return APIResponse(
        success=True,
        message=f"Retrieved {len(sources)} sources",
        data=sources,
    )


@router.get("/sources/{source_id}", response_model=APIResponse)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    """Get a specific source by ID."""
    source = db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    return APIResponse(
        success=True,
        message="Source retrieved",
        data=source,
    )


@router.get("/sources/status", response_model=APIResponse)
async def get_source_status(db: Session = Depends(get_db)):
    """Get health status of all sources."""
    query = select(Source).where(Source.is_active == True)
    sources = db.exec(query).all()

    status_summary = {}
    for source in sources:
        key = source.type
        if key not in status_summary:
            status_summary[key] = {"healthy": 0, "degraded": 0, "down": 0}

        if source.status == "healthy":
            status_summary[key]["healthy"] += 1
        elif source.status == "degraded":
            status_summary[key]["degraded"] += 1
        else:
            status_summary[key]["down"] += 1

    return APIResponse(
        success=True,
        message="Source status retrieved",
        data=status_summary,
    )