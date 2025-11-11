"""
FastAPI application entry point for Structured Reasoning System.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from api import scenarios, auth, surface_analysis, deep_questions, counterfactuals, strategic_outcomes
from api import surface_analysis_v2  # Sprint 2 enhanced API
from api import deep_questions_v2  # Sprint 3 enhanced API
from api import scoring  # Sprint 4.5 scoring system
from api import trajectories  # Sprint 5 trajectory projection
from api import phase3_pipeline  # Sprint 4.5 Phase 2-3 pipeline
from utils.config import settings
from models.database import engine, Base

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Structured Reasoning System API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    yield

    # Shutdown
    logger.info("Shutting down Structured Reasoning System API")


# Initialize FastAPI app
app = FastAPI(
    title="Structured Reasoning System API",
    description="Multi-phase analytical framework for complex scenario analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Structured Reasoning System API",
        "version": "1.0.0",
        "description": "Multi-phase analytical framework for complex scenario analysis",
        "docs_url": "/docs",
        "health_check": "/health"
    }


# Include routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(scenarios.router, prefix=f"{settings.API_PREFIX}/scenarios", tags=["Scenarios"])
app.include_router(surface_analysis.router, prefix=f"{settings.API_PREFIX}/scenarios", tags=["Phase 1: Surface Analysis"])
app.include_router(surface_analysis_v2.router, prefix=f"{settings.API_PREFIX}/scenarios", tags=["Phase 1: Surface Analysis V2 (Sprint 2)"])
app.include_router(deep_questions.router, prefix=f"{settings.API_PREFIX}/scenarios", tags=["Phase 2: Deep Questions"])
app.include_router(deep_questions_v2.router, tags=["Phase 2: Deep Questions V2 (Sprint 3)"])
app.include_router(counterfactuals.router, prefix=f"{settings.API_PREFIX}/scenarios", tags=["Phase 3: Counterfactuals"])
app.include_router(strategic_outcomes.router, prefix=f"{settings.API_PREFIX}/counterfactuals", tags=["Phase 5: Strategic Outcomes"])
app.include_router(scoring.router, tags=["Sprint 4.5: Scoring System"])
app.include_router(trajectories.router, tags=["Sprint 5: Trajectory Projection"])
app.include_router(phase3_pipeline.router, tags=["Sprint 4.5: Phase 2-3 Pipeline"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
