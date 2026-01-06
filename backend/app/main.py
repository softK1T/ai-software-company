"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import logging.config
from app.config import settings
from app.core.database import init_db
from app.api import templates, projects, runs, tasks, comments

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown."""
    # Startup
    logger.info("🚀 AI Software Company Platform starting...")
    init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 AI Software Company Platform shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Multi-agent AI platform for autonomous software company simulation",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global Exception Handlers
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": "ValueError"}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_type": type(exc).__name__}
    )


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ai-software-company",
        "version": settings.api_version,
        "debug": settings.debug,
    }


@app.get("/status", tags=["Health"])
async def status():
    """Detailed status endpoint."""
    return {
        "status": "operational",
        "service": "AI Software Company Platform",
        "version": settings.api_version,
        "database": "connected",
        "redis": "configured",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }


# ============================================================================
# API Routes
# ============================================================================

app.include_router(templates.router)
app.include_router(projects.router)
app.include_router(runs.router)
app.include_router(tasks.router)
app.include_router(comments.router)


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "service": "AI Software Company Platform",
        "version": settings.api_version,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "templates": "/api/templates",
            "projects": "/api/projects",
            "runs": "/api/runs",
            "tasks": "/api/tasks",
            "comments": "/api/comments",
            "health": "/health",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
