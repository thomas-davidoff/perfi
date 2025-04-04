from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.exc import (
    PerfiBaseException,
    NotFoundException,
    IntegrityConflictException,
    ValidationException,
    AuthenticationException,
    InvalidCredentialsException,
    TokenException,
    UserExistsException,
    InactiveUserException,
)


async def perfi_exception_handler(request: Request, exc: PerfiBaseException):
    """Handle all Perfi-specific exceptions."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = str(exc)

    # Map exception types to appropriate status codes
    if isinstance(exc, NotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, IntegrityConflictException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, ValidationException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, InvalidCredentialsException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, TokenException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, UserExistsException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, InactiveUserException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, AuthenticationException):
        status_code = status.HTTP_401_UNAUTHORIZED

    return JSONResponse(
        status_code=status_code,
        content={"error": detail},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )


def register_exception_handlers(app):
    app.add_exception_handler(PerfiBaseException, perfi_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
