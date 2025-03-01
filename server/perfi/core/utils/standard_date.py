from datetime import datetime, timezone


class StandardDate:
    DEFAULT_FORMAT = "%Y-%m-%d"
    SUPPORTED_FORMATS = [
        "%Y-%m-%d",  # standard
        "%m/%d/%Y",  # US
        "%d/%m/%Y",  # other
    ]

    def __init__(self, date_input):
        self.date = self._coerce_to_utc_date(date_input)

    def _coerce_to_utc_date(self, date_input) -> datetime:
        if isinstance(date_input, datetime):
            if date_input.tzinfo is None:
                return date_input.replace(tzinfo=timezone.utc)
            return date_input.astimezone(timezone.utc)
        elif isinstance(date_input, str):
            for fmt in self.SUPPORTED_FORMATS:
                try:
                    naive_date = datetime.strptime(date_input.split("T")[0], fmt)
                    return naive_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
            raise ValueError(f"Invalid date format: {date_input}")
        else:
            raise TypeError("Date input must be a datetime object or a string")

    def to_string(self, fmt=None) -> str:
        fmt = fmt or self.DEFAULT_FORMAT
        return self.date.strftime(fmt)

    def __repr__(self) -> str:
        return self.to_string()

    @property
    def month(self) -> int:
        return self.date.month

    @property
    def year(self) -> int:
        return self.date.year

    @property
    def day(self) -> int:
        return self.date.day
