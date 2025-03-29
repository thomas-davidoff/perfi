from .base import CustomException


class RepositoryError(CustomException):
    """
    Base exception class that is intended to be raised at the repository layer.
    Should not be surfaced to users and thus has a generic 500 code
    Probably shouldn't even have an http code to begin with...

    But...

    It can be easily subclasses for errors like "resource not found" or "already exists"
    to be handled more gracefully by the service layer.

    try:
        ...
    except RepositoryError as e:
        raise SomeOtherError from e
    """

    code = 500
    msg = "Error with persistence or something like that"


class ResourceNotFound(RepositoryError):
    """
    Repository error to indicate that the resource requested was not found in the db.
    """

    code = 404
    msg = "Resource not found"
