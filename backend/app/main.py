"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api import auth, sessions, agent

# Initialize logging before anything else
setup_logging(
    log_level=settings.log_level,
    log_to_file=settings.log_to_file,
    log_file_path=settings.log_file_path,
    max_bytes=settings.log_max_bytes,
    backup_count=settings.log_backup_count,
)

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Phone Agent Web Backend starting...")
    logger.info(f"Debug mode: {'ON' if settings.debug else 'OFF'}")
    logger.info(f"Model API: {settings.model_base_url}")
    logger.info(f"AgentBay configured: {'YES' if settings.agentbay_api_key else 'NO'}")
    logger.info(f"Supabase configured: {'YES' if settings.supabase_url else 'NO'}")
    yield
    # Shutdown
    logger.info("Phone Agent Web Backend shutting down...")


# Disable docs in production (when DEBUG=false)
app = FastAPI(
    title="Phone Agent Web API",
    description="AI-powered phone automation with AgentBay cloud phones",
    version="1.0.0",
    lifespan=lifespan,
    # Disable OpenAPI docs in production
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Phone Agent Web API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

