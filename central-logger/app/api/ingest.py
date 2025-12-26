"""
Log Ingestion API
POST endpoint for receiving logs from clients
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.db.database import get_db
from app.auth.api_key_auth import get_current_client
from app.utils.validators import LogIngestRequest
from app.services.log_service import LogService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/logs",
    status_code=status.HTTP_201_CREATED,
    response_model=dict
)
async def ingest_log(
    log_data: LogIngestRequest,
    client_id: str = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Ingest a workflow execution log
    
    This is the CORE endpoint - must be:
    - Fast
    - Reliable
    - Non-blocking
    
    Steps:
    1. Authenticate (dependency)
    2. Validate payload (Pydantic)
    3. Insert to DB
    4. Return 201
    
    Security:
    - API key required (X-API-Key header)
    - Client isolation enforced
    
    Error handling:
    - 401: Invalid API key
    - 400: Bad payload
    - 500: Database error
    """
    try:
        # Create log entry
        log_entry = LogService.create_log(db, client_id, log_data)
        
        logger.info(
            f"Log ingested successfully",
            extra={
                "log_id": str(log_entry.id),
                "client_id": client_id,
                "ticket_id": log_data.ticket_id,
                "status": log_data.status
            }
        )
        
        return {
            "status": "success",
            "log_id": str(log_entry.id),
            "message": "Log ingested successfully"
        }
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Failed to ingest log: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest log"
        )


@router.post(
    "/logs/batch",
    status_code=status.HTTP_201_CREATED,
    response_model=dict
)
async def ingest_logs_batch(
    logs: list[LogIngestRequest],
    client_id: str = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Batch ingestion endpoint (optional, for future use)
    
    Accepts multiple logs in single request
    """
    if len(logs) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 logs per batch"
        )
    
    try:
        created_ids = []
        
        for log_data in logs:
            log_entry = LogService.create_log(db, client_id, log_data)
            created_ids.append(str(log_entry.id))
        
        logger.info(f"Batch ingested: {len(created_ids)} logs for client {client_id}")
        
        return {
            "status": "success",
            "count": len(created_ids),
            "log_ids": created_ids
        }
        
    except Exception as e:
        logger.error(f"Batch ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch ingestion failed"
        )
