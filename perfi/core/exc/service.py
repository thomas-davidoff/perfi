from .base import CustomException


class ServiceError(CustomException):
    """
    Base exception for service layer errors.
    """
