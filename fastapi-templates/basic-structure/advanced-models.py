# fastapi-templates/basic-structure/advanced-models.py
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import conint, constr

# Type aliases for better code readability
PyObjectId = str
PositiveInt = conint(gt=0)
NonEmptyStr = constr(min_length=1, strip_whitespace=True)


# TODO: Customize this Enum with your own statuses/categories
class StatusEnum(str, Enum):
    """Enumeration for entity statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class BaseEntityModel(BaseModel):
    """
    Base model for all entities with common fields and configurations.
    """
    class Config:
        from_attributes = True
        populate_by_name = True
        use_enum_values = True
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

    @validator('*', pre=True)
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for optional fields."""
        if isinstance(v, str) and len(v.strip()) == 0:
            return None
        return v


# TODO: Define the base fields for your entity
class EntityBase(BaseEntityModel):
    """
    Base model for the entity with core, validated fields.
    """
    name: NonEmptyStr = Field(..., description="Entity's primary name", example="Sample Entity", max_length=100)
    description: Optional[str] = Field(None, description="A short description of the entity", example="This is a sample entity for demonstration.")
    status: StatusEnum = Field(..., description="The current status of the entity", example=StatusEnum.ACTIVE)

    @validator('name')
    def capitalize_name(cls, v):
        """Example validator: capitalize the name."""
        return v.title()


# TODO: Define the fields required for creating a new entity
class EntityCreate(EntityBase):
    """
    Model for creating a new entity. Includes a unique business identifier.
    """
    external_id: PositiveInt = Field(..., description="Unique business identifier", example=12345)

    @validator('external_id')
    def validate_id_range(cls, v):
        if v < 1 or v > 999999:
            raise ValueError('External ID must be between 1 and 999,999')
        return v


# TODO: Define the fields that are updatable
class EntityUpdate(BaseEntityModel):
    """
    Model for updating an entity. All fields are optional.
    """
    name: Optional[NonEmptyStr] = Field(None, description="Updated name", max_length=100)
    description: Optional[str] = Field(None, description="Updated description")
    status: Optional[StatusEnum] = Field(None, description="Updated status")

    @root_validator
    def validate_at_least_one_field(cls, values):
        """Ensure at least one field is provided for update."""
        if not any(v is not None for v in values.values()):
            raise ValueError('At least one field must be provided for update')
        return values


class EntityInDB(EntityBase):
    """
    Complete entity model as stored in the database, including metadata.
    """
    id: PyObjectId = Field(alias="_id", description="MongoDB document ID", example="507f1f77bcf86cd799439011")
    external_id: PositiveInt = Field(..., description="Unique business identifier", example=12345)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    version: int = Field(1, description="Document version for optimistic locking", ge=1)


class EntityResponse(EntityInDB):
    """
    Entity model for API responses, can include additional computed fields.
    """
    display_name: Optional[str] = Field(None, description="Computed display name", example="[Active] Sample Entity")

    @validator('display_name', always=True)
    def compute_display_name(cls, v, values):
        """Example of a computed field for API responses."""
        if 'status' in values and 'name' in values:
            return f"[{values['status'].title()}] {values['name']}"
        return v


# --- Supporting Models for Search and Bulk Operations ---

class SearchRequest(BaseEntityModel):
    """Model for search requests with filtering and pagination."""
    query: Optional[str] = Field(None, description="Generic search query string")
    status: Optional[List[StatusEnum]] = Field(None, description="Filter by a list of statuses")
    limit: conint(ge=1, le=500) = 100
    offset: conint(ge=0) = 0


class SearchResponse(BaseEntityModel):
    """Response model for search results."""
    items: List[EntityResponse] = Field(default_factory=list)
    total_count: int = Field(0, ge=0)
    limit: int
    offset: int


class BulkOperationResponse(BaseEntityModel):
    """Response model for bulk operations."""
    operation: str
    total_requested: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)