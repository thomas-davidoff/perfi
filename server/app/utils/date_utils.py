from datetime import datetime


class StandardDate:
    DEFAULT_FORMAT = "%Y-%m-%d"

    def __init__(self, date_input):
        self.date = self._coerce_to_date(date_input)

    def _coerce_to_date(self, date_input):
        if isinstance(date_input, datetime):
            return date_input
        elif isinstance(date_input, str):
            try:
                return datetime.strptime(date_input, self.DEFAULT_FORMAT)
            except ValueError as e:
                raise ValueError(f"Invalid date format: {e}")
        else:
            raise TypeError("Date input must be a datetime object or a string")

    def to_string(self, fmt=None):
        fmt = fmt or self.DEFAULT_FORMAT
        return self.date.strftime(fmt)

    def __repr__(self):
        return f"<StandardDate {self.to_string()}>"
