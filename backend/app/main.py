from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import engine, Base
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup: Create database tables
    logger.info("Starting AdjustR backend...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")

    yield

    # Shutdown
    logger.info("Shutting down AdjustR backend...")


app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Property Damage Assessment Tool",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AdjustR API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": "1.0.0"
    }


# Import and include routers
from app.routers import upload, analysis

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])

# Additional routers will be added as we build them
# from app.routers import reports
# app.include_router(reports.router, prefix="/api", tags=["reports"])
