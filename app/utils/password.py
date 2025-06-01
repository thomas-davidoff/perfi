import bcrypt
from sqlalchemy import LargeBinary
from config.settings import settings


def hash_password(password: str) -> bytes:
    """
    Hash a plain text password.

    Args:
        password (str): Plain text password to hash.

    Returns:
        bytes: The hashed password.
    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=settings.PWD_HASH_ROUNDS, prefix=b"2b")
    return bcrypt.hashpw(password=pwd_bytes, salt=salt)


def verify_password(plain_password: str, hashed_password: LargeBinary) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (bytes): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(
        password=plain_password.encode("utf-8"),
        hashed_password=hashed_password,
    )
