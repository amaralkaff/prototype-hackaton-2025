from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from utils.config import get_settings
from utils.logger import setup_logger

# Import API routes
from api.v1.routes import borrowers, loans, credit_scoring, photos, field_notes

settings = get_settings()
logger = setup_logger(settings.LOG_FILE, settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENV}")
    yield
    logger.info("Shutting down application")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multimodal AI-powered credit scoring system for micro-entrepreneurs",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "environment": settings.ENV,
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# API version info
@app.get(f"{settings.API_V1_PREFIX}/info")
async def api_info():
    """API information"""
    return {
        "api_version": "v1",
        "ml_model_version": settings.ML_MODEL_VERSION,
        "gemini_model": settings.GEMINI_MODEL,
        "gemini_vision_model": settings.GEMINI_VISION_MODEL,
        "features": [
            "Adaptive Credit Scoring Engine",
            "Income Reality Check",
            "Visual Socioeconomic Indicators",
            "Risk Explanation Layer",
            "Loan Recommendation Engine",
        ],
    }


# Include API routers
app.include_router(borrowers.router, prefix=settings.API_V1_PREFIX)
app.include_router(loans.router, prefix=settings.API_V1_PREFIX)
app.include_router(credit_scoring.router, prefix=settings.API_V1_PREFIX)
app.include_router(photos.router, prefix=settings.API_V1_PREFIX)
app.include_router(field_notes.router, prefix=settings.API_V1_PREFIX)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
