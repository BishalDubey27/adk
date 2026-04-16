"""
FastAPI main application for Tech Sarathi backend.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from core.config import settings
from core.database import db
from api.routes import projects, tasks, escalations, audit, team

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting Tech Sarathi API")
    
    try:
        await db.connect()
        logger.info("Database connected")
    except Exception as e:
        logger.warning(f"Database connection failed: {e}. Running without database.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Tech Sarathi API")
    try:
        await db.disconnect()
        logger.info("Database disconnected")
    except Exception:
        pass


# Create FastAPI app
app = FastAPI(
    title="Tech Sarathi API",
    description="AI-Powered Project Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "service": "Tech Sarathi API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    try:
        # Test database connection
        await db.fetchval("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "environment": settings.environment
    }


# Include routers
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(escalations.router, prefix="/api/v1", tags=["escalations"])
app.include_router(audit.router, prefix="/api/v1", tags=["audit"])
app.include_router(team.router, prefix="/api/v1", tags=["team"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
