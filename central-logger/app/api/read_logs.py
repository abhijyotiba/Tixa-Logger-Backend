"""
Read-only log APIs for dashboard
GET endpoints for querying stored logs
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from app.db.database import get_db
from app.auth.api_key_auth import get_current_client
from app.services.log_service import LogService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/logs", response_model=dict)
async def get_logs(
    client_id: str = Depends(get_current_client),
    db: Session = Depends(get_db),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ticket_id: Optional[str] = Query(None, description="Filter by ticket ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=settings.MAX_PAGE_SIZE, description="Items per page")
):
    """
    Get paginated list of logs
    
    Filters:
    - environment: production/staging/development
    - status: SUCCESS/ERROR/FAILED
    - category: Ticket category
    - ticket_id: Specific ticket
    - start_date, end_date: Date range
    
    Pagination:
    - page: Page number (1-indexed)
    - page_size: Items per page (max 100)
    
    Security:
    - Returns only logs for authenticated client
    - Tenant isolation enforced
    """
    try:
        skip = (page - 1) * page_size
        
        logs, total = LogService.get_logs(
            db=db,
            client_id=client_id,
            environment=environment,
            status=status,
            category=category,
            ticket_id=ticket_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=page_size
        )
        
        return {
            "data": [log.to_dict() for log in logs],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size
            },
            "filters": {
                "environment": environment,
                "status": status,
                "category": category,
                "ticket_id": ticket_id,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch logs"
        )


@router.get("/logs/{log_id}", response_model=dict)
async def get_log_detail(
    log_id: str,
    client_id: str = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Get detailed view of a single log
    
    Returns:
    - Full log entry with all metadata
    - Complete trace information
    - Metrics and payload
    
    Security:
    - Tenant isolation: only returns log if it belongs to authenticated client
    """
    try:
        log = LogService.get_log_by_id(db, log_id, client_id)
        
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log not found"
            )
        
        return {
            "data": log.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch log detail: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch log detail"
        )
