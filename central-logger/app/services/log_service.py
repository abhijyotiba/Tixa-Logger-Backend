"""
Log service - business logic for log operations
Separates DB operations from API layer
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from app.db.models import WorkflowLog
from app.utils.validators import LogIngestRequest

logger = logging.getLogger(__name__)


class LogService:
    """
    Service layer for log operations
    """
    
    @staticmethod
    def create_log(
        db: Session,
        client_id: str,
        log_data: LogIngestRequest
    ) -> WorkflowLog:
        """
        Insert a new log entry
        
        Args:
            db: Database session
            client_id: Authenticated client identifier
            log_data: Validated log payload
            
        Returns:
            Created log record
        """
        try:
            log_entry = WorkflowLog(
                client_id=client_id,
                environment=log_data.environment,
                workflow_version=log_data.workflow_version,
                ticket_id=log_data.ticket_id,
                executed_at=log_data.executed_at,
                execution_time_seconds=log_data.execution_time_seconds,
                status=log_data.status,
                category=log_data.category,
                resolution_status=log_data.resolution_status,
                metrics=log_data.metrics,
                payload=log_data.payload,
            )
            
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            
            logger.info(f"Log created: {log_entry.id} for client {client_id}")
            return log_entry
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create log: {e}", exc_info=True)
            raise
    
    @staticmethod
    def get_log_by_id(
        db: Session,
        log_id: str,
        client_id: Optional[str] = None
    ) -> Optional[WorkflowLog]:
        """
        Get a single log by ID
        
        Args:
            db: Database session
            log_id: Log UUID
            client_id: Optional client filter for tenant isolation
            
        Returns:
            Log record or None
        """
        query = db.query(WorkflowLog).filter(WorkflowLog.id == log_id)
        
        if client_id:
            query = query.filter(WorkflowLog.client_id == client_id)
        
        return query.first()
    
    @staticmethod
    def get_logs(
        db: Session,
        client_id: Optional[str] = None,
        environment: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        ticket_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[WorkflowLog], int]:
        """
        Query logs with filters and pagination
        
        Returns:
            Tuple of (logs, total_count)
        """
        query = db.query(WorkflowLog)
        
        # Apply filters
        if client_id:
            query = query.filter(WorkflowLog.client_id == client_id)
        
        if environment:
            query = query.filter(WorkflowLog.environment == environment)
        
        if status:
            query = query.filter(WorkflowLog.status == status)
        
        if category:
            query = query.filter(WorkflowLog.category == category)
        
        if ticket_id:
            query = query.filter(WorkflowLog.ticket_id == ticket_id)
        
        if start_date:
            query = query.filter(WorkflowLog.executed_at >= start_date)
        
        if end_date:
            query = query.filter(WorkflowLog.executed_at <= end_date)
        
        # Get total count
        total = query.count()
        
        # Apply ordering and pagination
        logs = query.order_by(desc(WorkflowLog.executed_at)).offset(skip).limit(limit).all()
        
        return logs, total
    
    @staticmethod
    def get_overview_metrics(
        db: Session,
        client_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get overview metrics for dashboard
        
        Args:
            db: Database session
            client_id: Optional client filter
            days: Number of days to look back
            
        Returns:
            Dictionary with metric values
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(WorkflowLog).filter(WorkflowLog.executed_at >= start_date)
        
        if client_id:
            query = query.filter(WorkflowLog.client_id == client_id)
        
        all_logs = query.all()
        
        if not all_logs:
            return {
                "total_tickets": 0,
                "success_rate": 0,
                "avg_execution_time": 0,
                "error_count": 0,
                "total_logs": 0
            }
        
        total = len(all_logs)
        success = len([l for l in all_logs if l.status == "SUCCESS"])
        errors = len([l for l in all_logs if l.status in ["ERROR", "FAILED"]])
        
        # Calculate average execution time
        execution_times = [l.execution_time_seconds for l in all_logs if l.execution_time_seconds]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            "total_tickets": total,
            "success_rate": round((success / total * 100), 2) if total > 0 else 0,
            "avg_execution_time": round(avg_time, 2),
            "error_count": errors,
            "total_logs": total,
            "period_days": days
        }
