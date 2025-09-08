
import pytest
import json
import time
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from report import Report
from transaction import Expense
from setup import Setup
from unittest.mock import patch

# Base directory for test data
BASE_DIR = Path(__file__).resolve().parent
TEST_USER = "test_user"
TEST_USER_DIR = BASE_DIR / "users" / TEST_USER


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Create user directory and clean up after tests."""
    try:
        TEST_USER_DIR.mkdir(parents=True, exist_ok=True)
        yield
        # Clean up test files
        for file in TEST_USER_DIR.glob("*"):
            try:
                file.unlink()
            except Exception:
                pass
        try:
            TEST_USER_DIR.rmdir()
            (BASE_DIR / "users").rmdir()
        except Exception:
            pass
    except Exception as e:
        pytest.fail(f"Setup/teardown failed: {e}")


@pytest.fixture
def setup_expenses(request):
    """Create a specified number of expenses for a user."""
    num_expenses = request.param
    expense = Expense("Initial", 100, "Food", "01-06-2025", "Test", TEST_USER)
    expense.setup_file_path = TEST_USER_DIR / "expenses.json"

    # Initialize budget
    setup = Setup(10000, 50000, "PKR", "USD", TEST_USER)
    setup.setup_file_path = TEST_USER_DIR / "setup.json"
    # Mock currency conversion
    with patch.object(Setup, "convert_income", return_value=1400000.0):
        setup.set_budget(1400000.0)

    # Add expenses across multiple dates and categories
    expenses = {}
    base_date = datetime(2025, 6, 1)
    for i in range(num_expenses):
        date = (base_date + timedelta(days=i % 30)).strftime("%d-%m-%Y")
        category = "Food" if i % 2 == 0 else "Travel"
        expense.name = f"Expense_{i}"
        expense.amount = 100 * (i % 5 + 1)
        expense.category = category
        expense.date = date
        expense.add_expense()
        expenses[f"Expense_{i}"] = {
            "amount": expense.amount,
            "category": expense.category,
            "date": expense.date,
            "description": expense.description
        }

    # Manually write expenses to ensure consistency
    with open(TEST_USER_DIR / "expenses.json", "w") as f:
        json.dump(expenses, f, indent=4)

    return expense


@pytest.mark.parametrize("time_period,expected_count,expected_total", [
    ("daily", 1, 100),  # 01-06-2025 has 1 expense
    ("monthly", 30, 3000),  # June 2025 has ~30 expenses
    ("yearly", 30, 3000),  # 2025 has all expenses
])
def test_brief_generate_report(setup_expenses, time_period, expected_count, expected_total):
    """Test brief report generation for different time periods."""
    report = Report(time_period, None, TEST_USER)
    report.expenses_file_path = TEST_USER_DIR / "expenses.json"
    report.setup_file_path = TEST_USER_DIR / "setup.json"

    result = report.brief_generate_report()
    assert result is not None
    # Approximate due to date distribution
    assert result["count"] >= expected_count
    # Approximate due to varying amounts
    assert result["total"] >= expected_total
    assert result["currency"] == "PKR"
    assert isinstance(result["average"], float)


@pytest.mark.parametrize("time_period,category", [
    ("monthly", None),
    ("monthly", "Food"),
    ("weekly", None),
])
def test_detailed_generate_report(setup_expenses, time_period, category):
    """Test detailed report generation for different time periods and categories."""
    report = Report(time_period, category, TEST_USER)
    report.expenses_file_path = TEST_USER_DIR / "expenses.json"
    report.setup_file_path = TEST_USER_DIR / "setup.json"
    report.detailed_report_path = TEST_USER_DIR / \
        f"detailed_report_{time_period}.json"

    result = report.detailed_generate_report(no_save=False)
    assert result is not None
    assert isinstance(result, dict)

    # Verify saved report
    with open(report.detailed_report_path, "r") as f:
        saved_report = json.load(f)
    assert saved_report == result

    # Check category filtering
    if category:
        for date, expenses in result.items():
            for expense in expenses:
                assert expense["category"] == category


def test_empty_expenses():
    """Test report generation with no expenses."""
    report = Report("monthly", None, TEST_USER)
    report.expenses_file_path = TEST_USER_DIR / "expenses.json"
    report.setup_file_path = TEST_USER_DIR / "setup.json"

    # Create empty expenses file
    with open(report.expenses_file_path, "w") as f:
        json.dump({}, f)

    brief_result = report.brief_generate_report()
    assert brief_result == {"total": 0, "count": 0,
                            "average": 0, "currency": "PKR"}

    detailed_result = report.detailed_generate_report(no_save=True)
    assert detailed_result == {}


@pytest.mark.parametrize("setup_expenses", [10, 100], indirect=True)
def test_brief_report_performance(setup_expenses, benchmark):
    """Test performance of brief report generation."""
    report = Report("monthly", None, TEST_USER)
    report.expenses_file_path = TEST_USER_DIR / "expenses.json"
    report.setup_file_path = TEST_USER_DIR / "setup.json"

    def generate_brief():
        report.brief_generate_report()

    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    benchmark(generate_brief)
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024

    assert benchmark.stats.stats.mean < 1.0  # Brief report < 1s
    assert end_memory - start_memory < 20  # Memory increase < 20MB


@pytest.mark.parametrize("setup_expenses", [10, 100], indirect=True)
def test_detailed_report_performance(setup_expenses, benchmark):
    """Test performance of detailed report generation."""
    report = Report("monthly", None, TEST_USER)
    report.expenses_file_path = TEST_USER_DIR / "expenses.json"
    report.setup_file_path = TEST_USER_DIR / "setup.json"
    report.detailed_report_path = TEST_USER_DIR / f"detailed_report_monthly.json"

    def generate_detailed():
        report.detailed_generate_report(no_save=True)

    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    benchmark(generate_detailed)
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024

    assert benchmark.stats.stats.mean < 2.0  # Detailed report < 2s
    assert end_memory - start_memory < 30  # Memory increase < 30MB
