"""
Centralized error handling.

All API errors follow a consistent format.
Frontend can rely on predictable error responses.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError


class APIError(Exception):
    """
    Base exception for all API errors.

    All API errors should use this or a subclass.
    Provides consistent error response format.
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        super().__init__(self.message)


class RequestValidationError(APIError):
    """Request validation failed."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
        )
        self.details = details


class NotFoundError(APIError):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
        )


class UnauthorizedError(APIError):
    """Authentication required or failed."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(APIError):
    """Permission denied."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class ConsentError(APIError):
    """
    Consent-related error.

    Used when operations require consent that is missing or revoked.
    This is a first-class error type due to consent-first architecture.
    """

    def __init__(self, message: str = "Consent required or revoked"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="CONSENT_REQUIRED",
        )


class RateLimitError(APIError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
        )


def setup_error_handlers(app: FastAPI) -> None:
    """
    Register global error handlers.

    All errors are transformed into consistent JSON responses.
    """

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        """
        Handle custom API errors.

        Returns consistent error format:
        {
            "error": {
                "code": "ERROR_CODE",
                "message": "Human-readable message",
                "details": {} // Optional, for validation errors
            }
        }
        """
        response_data = {
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            }
        }

        # Add details for validation errors
        if isinstance(exc, RequestValidationError) and hasattr(exc, "details") and exc.details:
            response_data["error"]["details"] = exc.details

        return JSONResponse(
            status_code=exc.status_code,
            content=response_data,
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_error_handler(
        request: Request, exc: PydanticValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors.

        Transforms Pydantic ValidationError into our API error format.
        """
        errors = exc.errors()
        details = {}
        for error in errors:
            field = ".".join(str(loc) for loc in error["loc"])
            details[field] = error["msg"]

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Catch-all for unexpected errors.

        In production, log full exception details but return generic message.
        Never expose stack traces or internal details to clients.
        """
        # TODO: Log full exception details to Sentry
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )
