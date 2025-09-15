"""Dummy test for OpenHands Server."""

import pytest

from openhands_server import __version__


def test_version() -> None:
    """Test that the version is correctly set."""
    assert __version__ == "0.1.0"


def test_dummy_functionality() -> None:
    """Dummy test to ensure the test framework is working."""
    assert 1 + 1 == 2


def test_import_main() -> None:
    """Test that the main module can be imported."""
    from openhands_server.main import main

    assert callable(main)


@pytest.mark.parametrize(
    "input_value,expected",
    [
        (1, 2),
        (2, 3),
        (10, 11),
    ],
)
def test_parametrized_dummy(input_value: int, expected: int) -> None:
    """Parametrized dummy test."""
    assert input_value + 1 == expected
