"""
Light validation for incoming log payloads
Keep validation minimal - trust the client structure
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime


class LogIngestRequest(BaseModel):
    """
    Minimal validation for log ingestion
    Only check critical fields, store rest as-is in JSONB
    """
    
    # Required fields
    environment: str = Field(..., description="Environment (production/staging/development)")
    executed_at: datetime = Field(..., description="When workflow was executed")
    
    # Optional structured fields
    workflow_version: Optional[str] = None
    ticket_id: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    status: Optional[str] = None
    category: Optional[str] = None
    resolution_status: Optional[str] = None
    
    # Flexible JSON storage
    metrics: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None
    
    @validator('environment')
    def validate_environment(cls, v):
        allowed = ['production', 'staging', 'development']
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed = ['SUCCESS', 'ERROR', 'PARTIAL', 'FAILED']
            if v not in allowed:
                raise ValueError(f"status must be one of {allowed}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "environment": "production",
                "executed_at": "2025-12-24T10:30:00Z",
                "workflow_version": "1.0.0",
                "ticket_id": "TICKET-123",
                "execution_time_seconds": 5.2,
                "status": "SUCCESS",
                "category": "billing_issue",
                "resolution_status": "resolved",
                "metrics": {
                    "confidence": 0.95,
                    "react_iterations": 3,
                    "tools_used": 2
                },
                "payload": {
                    "trace": [],
                    "final_response": "..."
                }
            }
        }
