from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.exc import (
    PerfiBaseException,
)


async def perfi_exception_handler(request: Request, exc: PerfiBaseException):
    """Handle all Perfi-specific exceptions."""
    detail = str(exc)

    return JSONResponse(
        status_code=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
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
