from .base import CustomException


class ValidationError(CustomException):
    pass


class UnauthorizedAccessError(CustomException):
    """
    This error is meant to represent cases where a user has identified a correct
    resource id that is NOT theirs.

    Catch this one specifically
    """

    code = 403
    pass
