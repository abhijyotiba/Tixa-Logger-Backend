"""
API Key Authentication
Simple, secure authentication for log ingestion
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from app.config import settings
from app.db.database import get_db

logger = logging.getLogger(__name__)


class APIKeyAuth:
    """
    API Key authentication handler
    Validates keys and resolves to client_id
    """
    
    def __init__(self):
        # In production, load from database
        # For now, using config/environment
        self.api_keys = settings.API_KEYS
    
    def get_client_id(self, api_key: str = Header(..., alias=settings.API_KEY_HEADER)) -> str:
        """
        Validate API key and return client_id
        Used as FastAPI dependency
        
        Args:
            api_key: API key from request header
            
        Returns:
            client_id: Authenticated client identifier
            
        Raises:
            HTTPException: 401 if invalid key
        """
        if not api_key:
            logger.warning("Missing API key in request")
            raise HTTPException(
                status_code=401,
                detail="API key required"
            )
        
        # Resolve client_id from API key
        client_id = self.api_keys.get(api_key)
        
        if not client_id:
            logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        
        logger.debug(f"Authenticated client: {client_id}")
        return client_id


# Global auth instance
api_key_auth = APIKeyAuth()


# FastAPI dependency
def get_current_client(
    api_key: str = Header(..., alias=settings.API_KEY_HEADER)
) -> str:
    """
    FastAPI dependency for authentication
    """
    return api_key_auth.get_client_id(api_key)
