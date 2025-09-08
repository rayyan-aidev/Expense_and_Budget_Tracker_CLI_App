import pytest
import time
from unittest.mock import patch
from io import StringIO
import main
from pathlib import Path
import psutil
from api import API

BASE_DIR = Path(__file__).resolve().parent
TEST_USER = "test_user"
TEST_USER_DIR = BASE_DIR / "users" / TEST_USER


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Create user directory and clean up after tests."""
    TEST_USER_DIR.mkdir(parents=True, exist_ok=True)
    yield
    for file in TEST_USER_DIR.glob("*"):
        file.unlink()
    TEST_USER_DIR.rmdir()
    (BASE_DIR / "users").rmdir()


def test_menu_navigation_performance(capsys, benchmark):
    """Test performance of navigating the main menu to add an expense and generate a report."""
    inputs = iter([
        "test_user",  # login username
        "1",  # Setup
        "1000",  # Budget
        "5000",  # Income
        "PKR",  # Default currency
        "USD",  # Income currency
        "2",  # Add expense
        "Test Expense",  # Name
        "100",  # Amount
        "Test Category",  # Category
        "",  # Date (use today)
        "Test Description",  # Description
        "4",  # Generate report
        "monthly",  # Time period
        "",  # Category (all)
        "6"  # Exit
    ])

    with patch("builtins.input", lambda _: next(inputs)), \
            patch("login.login_screen", return_value=(True, TEST_USER)), \
            patch.object(API, "get_exchange_rate", return_value=(280.0, "2025-06-01", "success")):
        def run_main():
            main

        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        benchmark(run_main)
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        captured = capsys.readouterr()
        assert "Expense added successfully" in captured.out
        assert "Generating reports in background" in captured.out
        assert benchmark.stats.stats.mean < 2.0  # Menu navigation < 2s
        assert end_memory - start_memory < 20  # Memory increase < 20MB
