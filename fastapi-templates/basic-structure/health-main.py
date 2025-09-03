# fastapi-templates/basic-structure/health-main.py
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status

# Import your modules here
# from .crud import your_router
# from .dependencies import your_data_loader

# Configure logging with environment variable support
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Advanced lifecycle management with graceful failure handling.
    Based on the exam solution patterns.
    """
    # Startup phase
    logger.info("Application startup: initializing connections...")
    try:
        # Initialize your data connections here
        # await your_data_loader.connect()
        logger.info("All connections established successfully")
    except Exception as e:
        # Don't crash the app - allow it to start for diagnostic purposes
        logger.error(f"Failed to establish connections: {e}")
        logger.warning("Application starting in degraded mode")

    yield  # Application runs here

    # Shutdown phase
    logger.info("Application shutdown: cleaning up connections...")
    try:
        # Clean up connections here
        # your_data_loader.disconnect()
        logger.info("Cleanup completed successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# Create FastAPI application with comprehensive metadata
app = FastAPI(
    lifespan=lifespan,
    title="Advanced FastAPI Service",
    version="2.0.0",
    description="Production-ready microservice with health monitoring",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Include your routers here
# app.include_router(your_router)


@app.get(
    "/",
    summary="Basic Health Check",
    description="Liveness probe endpoint - checks if server is running",
    tags=["Health"],
    response_model=dict
)
def liveness_check():
    """
    Basic liveness check for Kubernetes/OpenShift liveness probes.
    Always returns 200 OK if the server process is running.
    """
    return {
        "status": "alive",
        "service": "Advanced FastAPI Service",
        "check_type": "liveness"
    }


@app.get(
    "/health",
    summary="Detailed Health Check",
    description="Readiness probe endpoint - checks if service is ready to handle traffic",
    tags=["Health"],
    responses={
        200: {"description": "Service is healthy and ready"},
        503: {"description": "Service is unhealthy (dependencies unavailable)"}
    }
)
def readiness_check():
    """
    Comprehensive readiness check for Kubernetes/OpenShift readiness probes.
    Returns 503 if any critical dependencies are unavailable.
    """
    health_status = {
        "status": "healthy",
        "service": "Advanced FastAPI Service",
        "version": "2.0.0",
        "check_type": "readiness",
        "timestamp": None,
        "dependencies": {}
    }

    # Add timestamp
    from datetime import datetime
    health_status["timestamp"] = datetime.utcnow().isoformat() + "Z"

    # Check database connectivity
    try:
        # Replace with your actual data loader check
        # db_status = "connected" if your_data_loader.collection is not None else "disconnected"
        db_status = "connected"  # Placeholder
        health_status["dependencies"]["database"] = {
            "status": db_status,
            "type": "mongodb"
        }

        # Check for unhealthy dependencies
        if db_status == "disconnected":
            health_status["status"] = "unhealthy"
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable"
            )

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Health check error: {e}")
        health_status["status"] = "unhealthy"
        health_status["dependencies"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed"
        )

    return health_status


@app.get(
    "/health/live",
    summary="Kubernetes Liveness Probe",
    description="Simplified liveness check for Kubernetes liveness probe",
    tags=["Health"]
)
def k8s_liveness():
    """
    Kubernetes-specific liveness probe.
    Used to determine if container should be restarted.
    """
    return {"alive": True}


@app.get(
    "/health/ready",
    summary="Kubernetes Readiness Probe",
    description="Readiness check for Kubernetes readiness probe",
    tags=["Health"]
)
def k8s_readiness():
    """
    Kubernetes-specific readiness probe.
    Used to determine if pod should receive traffic.
    """
    try:
        # Check critical dependencies
        # db_ready = your_data_loader.collection is not None
        db_ready = True  # Placeholder

        if not db_ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready"
            )

        return {"ready": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Readiness check failed"
        )


@app.get(
    "/health/startup",
    summary="Kubernetes Startup Probe",
    description="Startup check for Kubernetes startup probe",
    tags=["Health"]
)
def k8s_startup():
    """
    Kubernetes-specific startup probe.
    Used for slow-starting containers.
    """
    try:
        # Check if application has completed initialization
        # startup_complete = your_data_loader.client is not None
        startup_complete = True  # Placeholder

        if not startup_complete:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Application still starting"
            )

        return {"started": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Startup check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Startup check failed"
        )


@app.get(
    "/metrics",
    summary="Application Metrics",
    description="Basic application metrics for monitoring",
    tags=["Monitoring"]
)
async def get_metrics():
    """
    Basic metrics endpoint for monitoring systems.
    Can be extended with Prometheus metrics.
    """
    try:
        metrics = {
            "service": "Advanced FastAPI Service",
            "version": "2.0.0",
            "uptime_seconds": 0,  # Calculate actual uptime
            "status": "operational"
        }

        # Add database metrics if available
        try:
            # db_stats = await your_data_loader.get_collection_stats()
            # metrics["database"] = db_stats
            metrics["database"] = {"status": "connected"}  # Placeholder
        except Exception as e:
            metrics["database"] = {"status": "error", "error": str(e)}

        return metrics
    except Exception as e:
        logger.error(f"Metrics endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metrics"
        )


# Error handlers for better error responses
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return HTTPException(
        status_code=404,
        detail={
            "error": "Not Found",
            "message": f"The requested resource was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    logger.error(f"Internal server error on {request.url.path}: {exc}")
    return HTTPException(
        status_code=500,
        detail={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        log_level=LOG_LEVEL.lower()
    )