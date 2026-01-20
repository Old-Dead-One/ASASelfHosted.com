"""
Base schemas and common patterns.

All API request/response schemas inherit from these base classes.
"""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Base schema with common configuration.

    All API schemas should inherit from this.
    """

    model_config = ConfigDict(
        # Validate assignment (raises on invalid assignment)
        validate_assignment=True,
        # Use enum values, not names
        use_enum_values=True,
        # Serialize by alias
        by_alias=True,
        # Extra fields are ignored (prevents injection via extra fields)
        extra="forbid",
    )


class ErrorResponse(BaseSchema):
    """
    Standard error response format.

    All API errors follow this structure.
    Frontend can rely on this format.
    """

    error: dict[str, str | dict]


class SuccessResponse(BaseSchema):
    """
    Standard success response wrapper.

    Use for operations that return simple success/failure.
    """

    success: bool
    message: str | None = None
