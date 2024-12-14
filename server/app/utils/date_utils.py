from datetime import datetime, timezone


class StandardDate:
    DEFAULT_FORMAT = "%Y-%m-%d"

    def __init__(self, date_input):
        self.date = self._coerce_to_utc_date(date_input)

    def _coerce_to_utc_date(self, date_input):
        if isinstance(date_input, datetime):
            # Normalize to UTC if the datetime is naive or in a different timezone
            if date_input.tzinfo is None:
                return date_input.replace(tzinfo=timezone.utc)
            else:
                return date_input.astimezone(timezone.utc)
        elif isinstance(date_input, str):
            try:
                # Parse the date string as UTC midnight
                naive_date = datetime.strptime(
                    date_input.split("T")[0], self.DEFAULT_FORMAT
                )
                return naive_date.replace(tzinfo=timezone.utc)
            except ValueError as e:
                raise ValueError(f"Invalid date format: {e}")
        else:
            raise TypeError("Date input must be a datetime object or a string")

    def to_string(self, fmt=None):
        fmt = fmt or self.DEFAULT_FORMAT
        return self.date.strftime(fmt)

    def __repr__(self):
        return f"<StandardDate {self.to_string()}>"

    @property
    def month(self):
        return self.date.month

    @property
    def year(self):
        return self.date.year

    @property
    def day(self):
        return self.date.day
