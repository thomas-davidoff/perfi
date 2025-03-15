# # password_utils.py
# import bcrypt

# def hash_password(plain_password):
#     salt = bcrypt.gensalt()
#     return bcrypt.hashpw(plain_password.encode(), salt)

# def verify_password_hash(plain_password, hashed_password):
#     return bcrypt.checkpw(plain_password.encode(), hashed_password)

import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hash a plain text password.

    Args:
        password (str): Plain text password to hash.

    Returns:
        bytes: The hashed password.
    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12, prefix=b"2b")
    return bcrypt.hashpw(password=pwd_bytes, salt=salt)


def verify_password(plain_password: str, hashed_password: str) -> bool:
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
