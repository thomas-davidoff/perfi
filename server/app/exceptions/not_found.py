from .base import CustomException


class ResourceNotFoundError(CustomException):
    code = 404
    msg = "Resource Not Found"
