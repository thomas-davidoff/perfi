from uuid import UUID
from app.exceptions import ValidationError, ProgrammingError


def to_uuid(uuid_or_str) -> UUID:
    if isinstance(uuid_or_str, UUID):
        return uuid_or_str

    elif isinstance(uuid_or_str, str):
        try:
            return UUID(uuid_or_str)
        except (TypeError, ValueError) as e:
            raise ValidationError(
                msg=f"id must be a valid uuid. You passed {uuid_or_str}"
            )

    raise ProgrammingError(
        f"uuid_or_str must be a UUID instance or a string. You passed {str(type(uuid_or_str))}"
    )
