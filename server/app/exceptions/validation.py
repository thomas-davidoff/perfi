from .base import CustomException


class ValidationError(CustomException):
    msg = "Validation error"
    code = 400


class PasswordTooSimpleError(ValidationError):
    msg = "Password is too simple"


class InvalidEmailError(ValidationError):
    msg = "Invalid email"


class UserAlreadyExistsError(ValidationError):
    msg = "User already exists"
