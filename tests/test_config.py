import os
import pytest
from config.environment import Environment, get_environment
from unittest.mock import MagicMock


@pytest.fixture
def clean_env():
    original_env = os.getenv("PERFI_ENV")
    if original_env is not None:
        del os.environ["PERFI_ENV"]
    yield
    if original_env is not None:
        os.environ["PERFI_ENV"] = original_env
    else:
        del os.environ["PERFI_ENV"]


def test_get_environment_raises_user_warning_without_env_set(
    clean_env: None, monkeypatch: pytest.MonkeyPatch
):
    mock_warning = MagicMock()
    monkeypatch.setattr("warnings.warn", mock_warning)

    get_environment()

    mock_warning.assert_called_once()


@pytest.mark.parametrize(
    "env_value,expected",
    [
        ("dev", Environment.DEVELOPMENT),
        ("test", Environment.TESTING),
        ("prod", Environment.PRODUCTION),
    ],
)
def test_environment_detection(clean_env, env_value, expected):
    os.environ["PERFI_ENV"] = env_value
    assert get_environment() == expected
