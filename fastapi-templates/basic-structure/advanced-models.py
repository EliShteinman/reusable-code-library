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


class RankEnum(str, Enum):
    """Military ranks enumeration for validation."""
    PRIVATE = "Private"
    CORPORAL = "Corporal"
    SERGEANT = "Sergeant"
    LIEUTENANT = "Lieutenant"
    CAPTAIN = "Captain"
    MAJOR = "Major"
    COLONEL = "Colonel"
    GENERAL = "General"
    CHIEF_OF_STAFF = "Chief of Staff"
    PRIME_MINISTER = "Prime Minister"


class BaseEntityModel(BaseModel):
    """
    Base model for all entities with common fields and configurations.
    """

    class Config:
        # Enable ORM mode for SQLAlchemy/MongoDB compatibility
        from_attributes = True
        # Allow population by field name or alias
        populate_by_name = True
        # Use enum values in JSON
        use_enum_values = True
        # Validate on assignment
        validate_assignment = True
        # JSON encoding configuration
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

    @validator('*', pre=True)
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for optional fields."""
        if isinstance(v, str) and len(v.strip()) == 0:
            return None
        return v


class SoldierBase(BaseEntityModel):
    """
    Base soldier model with comprehensive validation.
    """
    first_name: NonEmptyStr = Field(
        ...,
        description="Soldier's first name",
        example="John",
        max_length=50
    )
    last_name: NonEmptyStr = Field(
        ...,
        description="Soldier's last name",
        example="Doe",
        max_length=50
    )
    phone_number: PositiveInt = Field(
        ...,
        description="Soldier's phone number",
        example=5551234,
        ge=1000000,  # Minimum 7 digits
        le=9999999999  # Maximum 10 digits
    )
    rank: RankEnum = Field(
        ...,
        description="Military rank",
        example=RankEnum.PRIVATE
    )

    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        """Validate name fields."""
        if not v.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValueError('Name must contain only letters, spaces, hyphens, and apostrophes')
        return v.title()  # Capitalize first letter of each word

    @validator('phone_number')
    def validate_phone(cls, v):
        """Validate phone number format."""
        phone_str = str(v)
        if len(phone_str) < 7 or len(phone_str) > 10:
            raise ValueError('Phone number must be between 7-10 digits')
        return v


class SoldierCreate(SoldierBase):
    """
    Model for creating a new soldier with ID validation.
    """
    ID: PositiveInt = Field(
        ...,
        description="Unique soldier identifier",
        example=12345,
        ge=1,
        le=999999
    )

    @validator('ID')
    def validate_id_range(cls, v):
        """Validate ID is in acceptable range."""
        if v < 1 or v > 999999:
            raise ValueError('Soldier ID must be between 1 and 999999')
        return v


class SoldierUpdate(BaseEntityModel):
    """
    Model for updating soldier information with partial updates.
    """
    first_name: Optional[NonEmptyStr] = Field(
        None,
        description="Updated first name",
        max_length=50
    )
    last_name: Optional[NonEmptyStr] = Field(
        None,
        description="Updated last name",
        max_length=50
    )
    phone_number: Optional[PositiveInt] = Field(
        None,
        description="Updated phone number",
        ge=1000000,
        le=9999999999
    )
    rank: Optional[RankEnum] = Field(
        None,
        description="Updated military rank"
    )

    @validator('first_name', 'last_name')
    def validate_updated_name(cls, v):
        """Validate updated name fields."""
        if v is not None:
            if not v.replace(' ', '').replace('-', '').replace("'", '').isalpha():
                raise ValueError('Name must contain only letters, spaces, hyphens, and apostrophes')
            return v.title()
        return v

    @validator('phone_number')
    def validate_updated_phone(cls, v):
        """Validate updated phone number."""
        if v is not None:
            phone_str = str(v)
            if len(phone_str) < 7 or len(phone_str) > 10:
                raise ValueError('Phone number must be between 7-10 digits')
        return v

    @root_validator
    def validate_at_least_one_field(cls, values):
        """Ensure at least one field is provided for update."""
        if not any(v is not None for v in values.values()):
            raise ValueError('At least one field must be provided for update')
        return values


class SoldierInDB(SoldierBase):
    """
    Complete soldier model as stored in database with metadata.
    """
    id: PyObjectId = Field(
        alias="_id",
        description="MongoDB document ID",
        example="507f1f77bcf86cd799439011"
    )
    ID: PositiveInt = Field(
        ...,
        description="Unique soldier identifier",
        example=12345
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Record creation timestamp",
        example="2023-01-15T10:30:00Z"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Last update timestamp",
        example="2023-01-20T14:45:00Z"
    )
    version: Optional[int] = Field(
        1,
        description="Document version for optimistic locking",
        ge=1
    )

    class Config(SoldierBase.Config):
        # MongoDB-specific configuration
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "ID": 12345,
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": 5551234,
                "rank": "Private",
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-20T14:45:00Z",
                "version": 1
            }
        }


class SoldierResponse(SoldierInDB):
    """
    Soldier model for API responses with additional computed fields.
    """
    full_name: Optional[str] = Field(
        None,
        description="Computed full name",
        example="John Doe"
    )
    display_rank: Optional[str] = Field(
        None,
        description="Formatted rank for display",
        example="Pvt. John Doe"
    )

    @validator('full_name', always=True)
    def compute_full_name(cls, v, values):
        """Compute full name from first and last name."""
        if 'first_name' in values and 'last_name' in values:
            return f"{values['first_name']} {values['last_name']}"
        return v

    @validator('display_rank', always=True)
    def compute_display_rank(cls, v, values):
        """Compute display rank with abbreviation."""
        rank_abbrevs = {
            RankEnum.PRIVATE: "Pvt.",
            RankEnum.CORPORAL: "Cpl.",
            RankEnum.SERGEANT: "Sgt.",
            RankEnum.LIEUTENANT: "Lt.",
            RankEnum.CAPTAIN: "Capt.",
            RankEnum.MAJOR: "Maj.",
            RankEnum.COLONEL: "Col.",
            RankEnum.GENERAL: "Gen.",
            RankEnum.CHIEF_OF_STAFF: "CoS",
            RankEnum.PRIME_MINISTER: "PM"
        }

        if 'rank' in values and 'first_name' in values and 'last_name' in values:
            abbrev = rank_abbrevs.get(values['rank'], values['rank'])
            return f"{abbrev} {values['first_name']} {values['last_name']}"
        return v


class SoldierSearchRequest(BaseEntityModel):
    """
    Model for soldier search requests with filtering options.
    """
    first_name: Optional[str] = Field(
        None,
        description="Search by first name (partial match)",
        max_length=50
    )
    last_name: Optional[str] = Field(
        None,
        description="Search by last name (partial match)",
        max_length=50
    )
    rank: Optional[Union[RankEnum, List[RankEnum]]] = Field(
        None,
        description="Filter by rank(s)"
    )
    phone_prefix: Optional[str] = Field(
        None,
        description="Search by phone number prefix",
        max_length=4
    )
    id_range: Optional[Dict[str, int]] = Field(
        None,
        description="Search by ID range (min/max)",
        example={"min": 1000, "max": 9999}
    )
    limit: Optional[conint(ge=1, le=1000)] = Field(
        100,
        description="Maximum number of results"
    )
    offset: Optional[conint(ge=0)] = Field(
        0,
        description="Number of results to skip"
    )

    @validator('id_range')
    def validate_id_range(cls, v):
        """Validate ID range parameters."""
        if v is not None:
            if 'min' in v and 'max' in v and v['min'] > v['max']:
                raise ValueError('Minimum ID must be less than or equal to maximum ID')
        return v


class SoldierSearchResponse(BaseEntityModel):
    """
    Response model for soldier search results.
    """
    soldiers: List[SoldierResponse] = Field(
        default_factory=list,
        description="List of matching soldiers"
    )
    total_count: int = Field(
        0,
        description="Total number of matching records",
        ge=0
    )
    limit: int = Field(
        100,
        description="Applied result limit",
        ge=1
    )
    offset: int = Field(
        0,
        description="Applied result offset",
        ge=0
    )
    has_more: bool = Field(
        False,
        description="Whether more results are available"
    )

    @validator('has_more', always=True)
    def compute_has_more(cls, v, values):
        """Compute if more results are available."""
        if 'total_count' in values and 'limit' in values and 'offset' in values:
            return values['offset'] + values['limit'] < values['total_count']
        return v


class BulkOperationRequest(BaseEntityModel):
    """
    Model for bulk operations on soldiers.
    """
    operation: str = Field(
        ...,
        description="Bulk operation type",
        regex=r"^(create|update|delete)$"
    )
    soldiers: List[Union[SoldierCreate, SoldierUpdate, int]] = Field(
        ...,
        description="List of soldiers or IDs for bulk operation",
        min_items=1,
        max_items=100
    )

    @root_validator
    def validate_operation_data(cls, values):
        """Validate that operation matches data types."""
        operation = values.get('operation')
        soldiers = values.get('soldiers', [])

        if operation == 'create':
            for item in soldiers:
                if not isinstance(item, dict) or 'ID' not in item:
                    raise ValueError('Create operation requires soldier data with ID')
        elif operation == 'delete':
            for item in soldiers:
                if not isinstance(item, int):
                    raise ValueError('Delete operation requires soldier IDs')

        return values


class BulkOperationResponse(BaseEntityModel):
    """
    Response model for bulk operations.
    """
    operation: str = Field(..., description="Performed operation")
    total_requested: int = Field(..., description="Total items requested", ge=0)
    successful: int = Field(..., description="Successfully processed items", ge=0)
    failed: int = Field(..., description="Failed items", ge=0)
    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of errors for failed items"
    )
    results: List[Union[SoldierResponse, str]] = Field(
        default_factory=list,
        description="Results for successful operations"
    )


# API Response Models
class APIResponse(BaseEntityModel):
    """
    Standard API response wrapper.
    """
    success: bool = Field(True, description="Operation success status")
    message: str = Field("", description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="List of errors")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class HealthCheckResponse(BaseEntityModel):
    """
    Health check response model.
    """
    status: str = Field(..., description="Health status", regex=r"^(healthy|unhealthy|unknown)$")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Check timestamp")
    dependencies: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Dependency health status"
    )
    uptime_seconds: Optional[int] = Field(None, description="Service uptime in seconds")


# Error Models
class ValidationErrorDetail(BaseEntityModel):
    """
    Detailed validation error information.
    """
    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Validation error message")
    invalid_value: Optional[Any] = Field(None, description="The invalid value provided")


class APIErrorResponse(BaseEntityModel):
    """
    Standard API error response.
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[List[ValidationErrorDetail]] = Field(
        None,
        description="Detailed validation errors"
    )
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")