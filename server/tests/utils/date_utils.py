import pytest
from datetime import datetime, timezone
from app.utils import StandardDate  # Replace 'your_module' with the actual module name


@pytest.mark.parametrize(
    "input_date, expected_date",
    [
        (
            datetime(2024, 9, 25, 15, 0, tzinfo=timezone.utc),
            datetime(2024, 9, 25, 15, 0, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 9, 25, 15, 0),
            datetime(2024, 9, 25, 15, 0, tzinfo=timezone.utc),
        ),
        ("2024-09-25", datetime(2024, 9, 25, 0, 0, tzinfo=timezone.utc)),
    ],
)
def test_standard_date_init(input_date, expected_date):
    std_date = StandardDate(input_date)
    assert std_date.date == expected_date


@pytest.mark.parametrize(
    "input_date",
    [
        "2024-13-25",
        "25-09-2024",
        "random_string",
    ],
)
def test_standard_date_init_invalid_string(input_date):
    with pytest.raises(ValueError, match="Invalid date format: .*"):
        StandardDate(input_date)


@pytest.mark.parametrize(
    "input_date",
    [
        12345,
        None,
        12.34,
    ],
)
def test_standard_date_init_invalid_type(input_date):
    with pytest.raises(
        TypeError, match="Date input must be a datetime object or a string"
    ):
        StandardDate(input_date)


@pytest.mark.parametrize(
    "input_date, expected_output",
    [
        (datetime(2024, 9, 25, 0, 0, tzinfo=timezone.utc), "2024-09-25"),
        ("2024-09-25", "2024-09-25"),
    ],
)
def test_to_string_default_format(input_date, expected_output):
    std_date = StandardDate(input_date)
    assert std_date.to_string() == expected_output


@pytest.mark.parametrize(
    "input_date, custom_format, expected_output",
    [
        (
            datetime(2024, 9, 25, 15, 30, tzinfo=timezone.utc),
            "%Y-%m-%d %H:%M:%S %Z",
            "2024-09-25 15:30:00 UTC",
        ),
        ("2024-09-25", "%d/%m/%Y", "25/09/2024"),
    ],
)
def test_to_string_custom_format(input_date, custom_format, expected_output):
    std_date = StandardDate(input_date)
    assert std_date.to_string(custom_format) == expected_output


@pytest.mark.parametrize(
    "input_date, expected_repr",
    [
        (datetime(2024, 9, 25, 0, 0, tzinfo=timezone.utc), "<StandardDate 2024-09-25>"),
        ("2024-09-25", "<StandardDate 2024-09-25>"),
    ],
)
def test_repr_method(input_date, expected_repr):
    std_date = StandardDate(input_date)
    assert repr(std_date) == expected_repr
