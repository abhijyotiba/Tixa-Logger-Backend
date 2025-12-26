"""
Central Logger - Main FastAPI Application
Provider-side log collection and analytics service
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api import ingest, read_logs, metrics
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Central Logger API",
    description="Log collection and analytics service for workflow monitoring",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT
    }

# Include routers
app.include_router(ingest.router, prefix="/api/v1", tags=["Ingestion"])
app.include_router(read_logs.router, prefix="/api/v1", tags=["Logs"])
app.include_router(metrics.router, prefix="/api/v1", tags=["Metrics"])

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.SERVICE_NAME} in {settings.ENVIRONMENT} mode")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.SERVICE_NAME}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
