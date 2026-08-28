import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services.firestore_service import firestore_service
from api.health import router as health_router
from api.routes import router as api_router
from api.websocket import router as ws_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("archon.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown routines."""
    logger.info("==================================================")
    logger.info("  ARCHON Enterprise Operations Fleet Initializing ")
    logger.info("  All Things Agentic Hackathon | Track 1          ")
    logger.info("==================================================")
    
    # Initialize Firestore collections and seed datasets
    await firestore_service.initialize()
    logger.info("Firestore service initialized with campus topology.")
    logger.info("Agent Registry booted with 7 specialist manifests.")
    logger.info("Model Armor Firewall active.")
    logger.info("Agent Gateway Policy Engine active.")
    
    yield
    
    logger.info("ARCHON Enterprise Operations Fleet shutting down gracefully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Incident Intelligence & Operational Resilience Platform for Campus Operations.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Next.js frontend and cloud deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(health_router, tags=["Health"])
app.include_router(ws_router, tags=["WebSocket"])
app.include_router(api_router, prefix=settings.API_V1_STR, tags=["API v1"])


@app.get("/")
async def root():
    return {
        "platform": "ARCHON Enterprise Incident Intelligence Platform",
        "tagline": "Institutional Intelligence That Never Forgets",
        "version": settings.VERSION,
        "track": "Fortified Enterprise Fleet",
        "health_check": "/health",
        "api_docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
