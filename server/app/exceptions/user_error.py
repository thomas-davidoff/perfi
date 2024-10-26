from .base import CustomException


class UserError(CustomException):
    msg = "User error"
    code = 422


class MissingPayload(UserError):
    msg = "Invalid or missing JSON body"


class MissingLoginData(UserError):
    msg = "Missing username or password"


class MissingRegistrationData(UserError):
    msg = "Must provide username, email, and password"
