"""
Centralized error handling.

All API errors follow a consistent format.
Frontend can rely on predictable error responses.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError as FastAPIRequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.config import get_settings

# Logger for error tracking
logger = logging.getLogger("asaselfhosted")


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


class DomainValidationError(APIError):
    """
    Domain-level validation error.

    Used for internal validation logic (not HTTP request validation).
    FastAPI handles HTTP request validation separately.
    """

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
        )
        self.details = details


# Keep RequestValidationError as alias for backward compatibility
# TODO: Migrate all usages to DomainValidationError
RequestValidationError = DomainValidationError


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


class NotImplementedError(APIError):
    """Feature not implemented."""

    def __init__(self, message: str = "Feature not implemented"):
        super().__init__(
            message=message,
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            error_code="NOT_IMPLEMENTED",
        )


class SignatureVerificationError(APIError):
    """Invalid Ed25519 signature."""

    def __init__(self, message: str = "Invalid signature"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="SIGNATURE_INVALID",
        )


class KeyVersionMismatchError(APIError):
    """Key version mismatch."""

    def __init__(self, expected: int, received: int):
        super().__init__(
            message=f"Key version mismatch: expected {expected}, received {received}",
            status_code=status.HTTP_409_CONFLICT,
            error_code="KEY_VERSION_MISMATCH",
        )
        self.expected = expected
        self.received = received


class HeartbeatReplayError(APIError):
    """Duplicate heartbeat_id detected."""

    def __init__(self, heartbeat_id: str):
        super().__init__(
            message=f"Replay detected: heartbeat_id {heartbeat_id}",
            status_code=status.HTTP_409_CONFLICT,
            error_code="HEARTBEAT_REPLAY",
        )
        self.heartbeat_id = heartbeat_id


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
        if isinstance(exc, DomainValidationError) and hasattr(exc, "details") and exc.details:
            response_data["error"]["details"] = exc.details

        # Add request_id if available (for log correlation)
        # TODO: Generate request_id in middleware when ready
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            response_data["error"]["request_id"] = request_id

        return JSONResponse(
            status_code=exc.status_code,
            content=response_data,
        )

    @app.exception_handler(FastAPIRequestValidationError)
    async def fastapi_request_validation_error_handler(
        request: Request, exc: FastAPIRequestValidationError
    ) -> JSONResponse:
        """
        Handle FastAPI request validation errors.

        FastAPI raises this for invalid request bodies, query params, path params.
        Transforms into our API error format.
        """
        details: dict[str, str] = {}
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err.get("loc", []))
            details[field] = err.get("msg", "Invalid value")

        response_data = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": details,
            }
        }

        # Add request_id if available
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            response_data["error"]["request_id"] = request_id

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_data,
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_error_handler(
        request: Request, exc: PydanticValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors.

        Used for internal schema validation (not HTTP requests).
        FastAPI requests are handled by FastAPIRequestValidationError above.
        """
        details: dict[str, str] = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []))
            details[field] = error.get("msg", "Invalid value")

        response_data = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": details,
            }
        }

        # Add request_id if available
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            response_data["error"]["request_id"] = request_id

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_data,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Catch-all for unexpected errors.

        Logs full exception details but returns generic message to client.
        Never expose stack traces or internal details to clients.
        """
        # Log exception with full details (never expose details to client)
        settings = get_settings()
        log_extra = {
            "path": request.url.path,
            "method": request.method,
        }
        
        if settings.ENV == "local":
            # Keep it loud and obvious while developing
            logger.exception("Unhandled exception (local)", extra=log_extra, exc_info=exc)
        else:
            logger.exception("Unhandled exception", extra=log_extra, exc_info=exc)

        # TODO: Send to Sentry when configured

        response_data = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            }
        }

        # Add request_id if available (for log correlation)
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            response_data["error"]["request_id"] = request_id

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_data,
        )
