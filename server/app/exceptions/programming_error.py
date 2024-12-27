from .base import CustomException


class ProgrammingError(CustomException):
    msg = "Programming error"
    code = 500
