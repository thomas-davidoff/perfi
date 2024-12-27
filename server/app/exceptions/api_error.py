from .base import CustomException


class ApiError(CustomException):
    """
    These errors are intended to be raised and caught by Flask middleware.
    """

    code = 500
    msg = "Something went wrong."
