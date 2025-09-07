# fastapi-templates/crud-operations/generic_crud_router.py

import logging
from typing import List, Any, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ValidationError

# --- TODO: Replace these placeholder imports with your actual modules ---
# from ..dependencies import data_loader
# from ..models import EntityCreate, EntityUpdate, EntityInDB

# --- Mock objects for the template to be self-contained ---
class MockDAL:
    async def create_item(self, item: BaseModel) -> Dict[str, Any]: return {"ID": getattr(item, 'ID', 0), "_id": "mock_id"}
    async def get_all_data(self) -> List[Dict[str, Any]]: return []
    async def get_item_by_id(self, item_id: int) -> Dict[str, Any]: return {}
    async def update_item(self, item_id: int, item_update: BaseModel) -> Dict[str, Any]: return {}
    async def delete_item(self, item_id: int) -> bool: return True

class EntityCreate(BaseModel): ID: int
class EntityUpdate(BaseModel): pass
class EntityInDB(BaseModel): pass

data_loader = MockDAL()
# --- End of Mock objects ---


logger = logging.getLogger(__name__)

# You can customize the prefix and tags for each use case
router = APIRouter(
    prefix="/items",
    tags=["Items CRUD"]
)

# --- Helper Function for validation ---
def validate_entity_id(entity_id: int):
    """Validates that entity_id is a positive integer."""
    if entity_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Entity ID must be a positive integer",
        )

# --- CREATE ---
@router.post("/", response_model=EntityInDB, status_code=status.HTTP_201_CREATED)
async def create_entity(entity: EntityCreate):
    """ Creates a new entity. """
    try:
        logger.info(f"Attempting to create entity with ID {entity.ID}")
        created_entity = await data_loader.create_item(entity)
        return created_entity
    except ValueError as e: # From DAL: Duplicate ID
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except RuntimeError as e: # From DAL: DB connection error
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating entity: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

# --- READ ALL ---
@router.get("/", response_model=List[EntityInDB])
async def read_all_entities():
    """ Retrieves all entities. """
    try:
        return await data_loader.get_all_data()
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

# --- READ ONE ---
@router.get("/{entity_id}", response_model=EntityInDB)
async def read_entity_by_id(entity_id: int):
    """ Retrieves a single entity by its ID. """
    validate_entity_id(entity_id)
    try:
        entity = await data_loader.get_item_by_id(entity_id)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity with ID {entity_id} not found")
        return entity
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

# --- UPDATE ---
@router.put("/{entity_id}", response_model=EntityInDB)
async def update_entity(entity_id: int, entity_update: EntityUpdate):
    """ Updates an existing entity. """
    validate_entity_id(entity_id)
    try:
        updated_entity = await data_loader.update_item(entity_id, entity_update)
        if updated_entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity with ID {entity_id} not found")
        return updated_entity
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

# --- DELETE ---
@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(entity_id: int):
    """ Deletes an entity by its ID. """
    validate_entity_id(entity_id)
    try:
        success = await data_loader.delete_item(entity_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity with ID {entity_id} not found")
        return
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))