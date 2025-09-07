# fastapi-templates/basic-structure/production-main-template.py

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status


# --- TODO: Replace these placeholder imports with your actual modules ---
# from .crud import generic_router
# from .dependencies import data_loader

# --- Mock objects for the template to be self-contained ---
class MockDAL:
    _is_connected = False

    async def connect(self): self._is_connected = True

    def disconnect(self): self._is_connected = False

    @property
    def collection(self): return self._is_connected


data_loader = MockDAL()
# --- End of Mock objects ---


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events with graceful degradation.
    This allows the app to start even if the database connection fails,
    making it suitable for monitoring and diagnostics in containerized environments.
    """
    logger.info("Application startup: attempting to connect to the database...")
    try:
        await data_loader.connect()
        logger.info("Database connection established successfully.")
    except Exception as e:
        logger.error(f"Failed to establish database connection on startup: {e}")
        logger.warning("Application is starting in a DEGRADED MODE (database connection failed).")

    yield

    logger.info("Application shutdown: disconnecting from the database...")
    data_loader.disconnect()
    logger.info("Database connection closed.")


app = FastAPI(
    lifespan=lifespan,
    title="Production-Ready API Service",
    version="2.0.0",
    description="A robust microservice template with advanced health checks and lifecycle management."
)


# --- TODO: Include your API routers here ---
# from .crud.generic_crud_router import router as items_router
# app.include_router(items_router, prefix="/api/v1/items", tags=["Items"])


@app.get("/", tags=["Health"])
def liveness_check():
    """
    Liveness Probe Endpoint.
    This endpoint is used by container orchestrators (like Kubernetes) to check if the
    application process is running and responsive. It should always return 200 OK
    as long as the server process is alive, regardless of dependency status.
    """
    return {"status": "alive", "service": app.title}


@app.get("/health", tags=["Health"])
def readiness_check():
    """
    Readiness Probe Endpoint.
    This endpoint is used to check if the application is ready to handle traffic.
    It should verify the status of critical dependencies (like the database).
    If a dependency is down, it should return a 503 Service Unavailable status,
    signaling the orchestrator to temporarily stop sending traffic to this instance.
    """
    is_db_connected = data_loader.collection is not None

    if not is_db_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable."
        )

    return {"status": "ready", "dependencies": {"database": "connected"}}