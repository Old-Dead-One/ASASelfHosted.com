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
        # Extra fields are forbidden (prevents injection via extra fields)
        extra="forbid",
        # Allow ORM-like objects and dicts to be converted
        from_attributes=True,
    )


class APIErrorBody(BaseSchema):
    """
    Error body structure.

    Matches the error format returned by error handlers in errors.py.
    """

    code: str
    message: str
    details: dict | None = None
    request_id: str | None = None


class ErrorResponse(BaseSchema):
    """
    Standard error response format.

    All API errors follow this structure.
    Frontend can rely on this format.
    """

    error: APIErrorBody


class SuccessResponse(BaseSchema):
    """
    Standard success response wrapper.

    Use for operations that return simple success/failure.
    """

    success: bool
    message: str | None = None
