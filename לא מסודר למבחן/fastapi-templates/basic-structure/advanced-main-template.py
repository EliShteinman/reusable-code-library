# fastapi-templates/basic-structure/production-main.py

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status


# --- Placeholder Imports ---
# from .crud import generic_router
# from .dependencies import data_loader
class MockDAL:
    async def connect(self): pass

    def disconnect(self): pass

    @property
    def collection(self): return True


data_loader = MockDAL()
# --- End of Placeholders ---

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Manages application startup and shutdown events with graceful degradation. """
    logger.info("Application startup: connecting to database...")
    try:
        await data_loader.connect()
        logger.info("Database connection established.")
    except Exception as e:
        # Don't crash the app - allow it to start for diagnostic purposes
        logger.error(f"Failed to establish database connection: {e}")
        logger.warning("Application starting in a degraded mode (DB connection failed).")

    yield

    logger.info("Application shutdown: disconnecting from database...")
    data_loader.disconnect()


app = FastAPI(
    lifespan=lifespan,
    title="Production-Ready API Service",
    version="2.0.0"
)


# app.include_router(generic_router, prefix="/api/v1/items", tags=["Items"])

@app.get("/", tags=["Health"])
def liveness_check():
    """ Basic liveness check for Kubernetes/OpenShift liveness probes. """
    return {"status": "alive"}


@app.get("/health", tags=["Health"])
def readiness_check():
    """
    Comprehensive readiness check for Kubernetes/OpenShift readiness probes.
    Returns 503 if any critical dependencies are unavailable.
    """
    is_db_connected = data_loader.collection is not None

    if not is_db_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable."
        )

    return {"status": "ready", "dependencies": {"database": "connected"}}