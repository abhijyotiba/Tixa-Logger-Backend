"""
SQLAlchemy models for database tables
"""
from sqlalchemy import Column, String, Float, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.db.database import Base


class WorkflowLog(Base):
    """
    Main table for storing workflow execution logs
    Uses JSONB for flexible schema evolution
    """
    __tablename__ = "workflow_logs"

    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant & environment
    client_id = Column(String(255), nullable=False, index=True)
    environment = Column(String(50), nullable=False, index=True)
    workflow_version = Column(String(50))

    # Execution metadata
    ticket_id = Column(String(255), index=True)
    executed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    execution_time_seconds = Column(Float)

    # Status & categorization
    status = Column(String(50), index=True)  # SUCCESS, ERROR, PARTIAL
    category = Column(String(100), index=True)
    resolution_status = Column(String(100))

    # Flexible JSON storage
    metrics = Column(JSONB)  # Confidence, iterations, tool_calls, etc.
    payload = Column(JSONB)  # Full trace data

    # Audit
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_client_executed', 'client_id', 'executed_at'),
        Index('idx_client_status', 'client_id', 'status'),
        Index('idx_environment_executed', 'environment', 'executed_at'),
    )

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "client_id": self.client_id,
            "environment": self.environment,
            "workflow_version": self.workflow_version,
            "ticket_id": self.ticket_id,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "execution_time_seconds": self.execution_time_seconds,
            "status": self.status,
            "category": self.category,
            "resolution_status": self.resolution_status,
            "metrics": self.metrics,
            "payload": self.payload,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
