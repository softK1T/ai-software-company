"""Main FastAPI application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.core import seed
from app.core.database import SessionLocal
from app.api import templates, projects

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 AI Software Company Platform starting...")
    init_db()
    
    # Seed initial data
    db = SessionLocal()
    try:
        seed.seed_templates(db)
    except Exception as e:
        logger.error(f"Seeding error: {e}")
    finally:
        db.close()
    
    yield
    logger.info("🛑 AI Software Company Platform shutting down...")

app = FastAPI(
    title="AI Software Company Platform",
    description="Autonomous AI agents that build software projects",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(templates.router)
app.include_router(projects.router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-software-company"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Software Company Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
