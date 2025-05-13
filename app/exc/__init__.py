from fastapi import status


class PerfiBaseException(Exception):
    """Base exception for all custom application exceptions"""

    pass


# Repository layer exceptions
class RepositoryException(PerfiBaseException):
    """Base exception for repository layer errors."""

    pass


class IntegrityConflictException(RepositoryException):
    """Exception for database integrity conflicts like duplicate entries."""

    status_code = status.HTTP_409_CONFLICT


class NotFoundException(RepositoryException):
    """Exception for when a requested resource doesn't exist."""

    status_code = status.HTTP_404_NOT_FOUND


# Service layer exceptions
class ServiceException(PerfiBaseException):
    """Base exception for service layer errors."""

    pass


class ValidationException(ServiceException):
    """Exception for validation errors in the service layer."""

    status_code = status.HTTP_400_BAD_REQUEST


# Authentication exceptions
class AuthenticationException(PerfiBaseException):
    """Base exception for authentication errors."""

    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidCredentialsException(AuthenticationException):
    """Exception for invalid credentials."""

    pass


class TokenException(AuthenticationException):
    """Base exception for token-related errors."""

    pass


class InvalidTokenException(TokenException):
    """Exception for invalid tokens."""

    pass


class ExpiredTokenException(TokenException):
    """Exception for expired tokens."""

    pass


class RevokedTokenException(TokenException):
    """Exception for revoked tokens."""

    pass


# Domain-specific exceptions
class UserException(PerfiBaseException):
    """Base exception for user-related errors."""

    pass


class UserExistsException(UserException):
    """Exception for when trying to create a user that already exists."""

    status_code = status.HTTP_409_CONFLICT


class InactiveUserException(UserException):
    """Exception for when an inactive user attempts to authenticate."""

    status_code = status.HTTP_403_FORBIDDEN


class AuthorizationException(PerfiBaseException):
    """Use for errors related to attempts to access data outside of the users scope"""

    status_code = status.HTTP_403_FORBIDDEN
