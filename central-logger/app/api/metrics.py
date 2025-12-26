"""
Metrics API for dashboard analytics
Provides aggregated statistics and insights
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.db.database import get_db
from app.auth.api_key_auth import get_current_client
from app.services.log_service import LogService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics/overview", response_model=dict)
async def get_overview_metrics(
    client_id: str = Depends(get_current_client),
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze")
):
    """
    Get overview metrics for dashboard
    
    Returns:
    - Total tickets processed
    - Success rate (%)
    - Average execution time
    - Error count
    - Total logs
    
    Parameters:
    - days: Lookback period (1-90 days)
    
    Security:
    - Returns metrics only for authenticated client
    """
    try:
        metrics = LogService.get_overview_metrics(
            db=db,
            client_id=client_id,
            days=days
        )
        
        return {
            "data": metrics,
            "client_id": client_id
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch overview metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch metrics"
        )


@router.get("/metrics/categories", response_model=dict)
async def get_category_breakdown(
    client_id: str = Depends(get_current_client),
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze")
):
    """
    Get ticket breakdown by category
    
    Returns count and success rate per category
    """
    try:
        # This can be extended with more sophisticated queries
        # For now, returning a simple structure
        from datetime import datetime, timedelta
        from app.db.models import WorkflowLog
        from sqlalchemy import func
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query category breakdown
        results = db.query(
            WorkflowLog.category,
            func.count(WorkflowLog.id).label('count'),
            func.sum(
                func.case(
                    (WorkflowLog.status == 'SUCCESS', 1),
                    else_=0
                )
            ).label('success_count')
        ).filter(
            WorkflowLog.client_id == client_id,
            WorkflowLog.executed_at >= start_date
        ).group_by(
            WorkflowLog.category
        ).all()
        
        categories = []
        for result in results:
            total = result.count
            success = result.success_count or 0
            categories.append({
                "category": result.category or "uncategorized",
                "count": total,
                "success_count": success,
                "success_rate": round((success / total * 100), 2) if total > 0 else 0
            })
        
        return {
            "data": categories,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch category metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch category metrics"
        )
