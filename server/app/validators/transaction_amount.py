import decimal
from app.exceptions import ValidationError


class TransactionAmount:
    def __init__(self, value):
        """
        Initialize a TransactionAmount instance and validate the value.

        Args:
            value: The value to validate as a valid transaction amount.

        Raises:
            ValidationError: If the value is invalid.
        """
        self._value = None  # Internal storage for the validated value
        self._validate(value)  # Validate and set the value

    def _validate(self, value):
        """
        Validate the transaction amount.

        Args:
            value: The value to validate.

        Raises:
            ValidationError: If the value is invalid.
        """
        try:

            # Convert to Decimal for precise arithmetic
            amount = decimal.Decimal(str(value))
        except (decimal.InvalidOperation, TypeError, ValueError):
            raise ValidationError("Amount must be a valid number.")

        # Check for two decimal places or less
        if amount.as_tuple().exponent < -2:
            raise ValidationError("Amount cannot have more than two decimal places.")

        # If all validations pass, store the value
        self._value = amount

    @property
    def value(self):
        """
        Get the validated transaction amount.

        Returns:
            decimal.Decimal: The validated transaction amount.
        """
        return self._value
