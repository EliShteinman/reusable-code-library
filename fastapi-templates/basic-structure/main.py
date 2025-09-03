# fastapi-templates/basic-structure/main.py
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List


# Import placeholder - להחליף לפי הצורך
# from .core.dependencies import data_loader
# from .crud import items
# from . import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On application startup, initialize the database connection.
    On shutdown, resources will be released.
    """
    print("Application startup: Initializing database connection...")
    # data_loader.connect()  # להסיר הערה לפי הצורך
    yield
    print("Application shutdown: Releasing database connection resources...")
    # data_loader.close()  # להסיר הערה לפי הצורך


# Create the main FastAPI application instance
app = FastAPI(
    title="Data Service",  # לשנות לפי הצורך
    description="A service to fetch and manage data",  # לשנות לפי הצורך
    version="1.0.0",
    lifespan=lifespan,
)


# Include routers (להסיר הערה לפי הצורך)
# app.include_router(items.router)

@app.get(
    "/",
    summary="Health Check",
    description="A simple health check endpoint to verify the service is running.",
    tags=["Monitoring"],
)
def health_check():
    """
    Returns a 200 OK with a status message.
    This is used by Kubernetes/OpenShift liveness and readiness probes.
    """
    return {"status": "ok"}


@app.get(
    "/data",
    # response_model=List[models.Item],  # להסיר הערה ולהתאים לפי הצורך
    summary="Get all data",
    description="Fetch all records from the database.",
    tags=["Data"],
)
def get_all_data():
    """
    Returns all data from the database.
    Template - needs to be adapted for specific use case.
    """
    try:
        # all_data = data_loader.get_all_data()  # להסיר הערה לפי הצורך
        # if isinstance(all_data, dict) and "error" in all_data:
        #     raise HTTPException(status_code=500, detail=all_data["error"])
        # return all_data

        # Placeholder response
        return {"message": "Template - implement data fetching logic"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )