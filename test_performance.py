import pytest
import time
import json
import psutil
import os
from pathlib import Path
from transaction import Expense
from report import Report
from setup import Setup
from api import API
from user_profile import user_profile
from Multithreading_Multiprocessing import BackgroundTasks
from unittest.mock import patch

# Base directory for test data
BASE_DIR = Path(__file__).resolve().parent
TEST_USER = "test_user"
TEST_USER_DIR = BASE_DIR / "users" / TEST_USER
TEST_USER_2 = "test_user_2"
TEST_USER_2_DIR = BASE_DIR / "users" / TEST_USER_2


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Create user directories and clean up after tests."""
    TEST_USER_DIR.mkdir(parents=True, exist_ok=True)
    TEST_USER_2_DIR.mkdir(parents=True, exist_ok=True)
    yield
    # Clean up test files
    for user_dir in [TEST_USER_DIR, TEST_USER_2_DIR]:
        for file in user_dir.glob("*"):
            file.unlink()
        user_dir.rmdir()
    (BASE_DIR / "users").rmdir()


@pytest.fixture
def setup_expenses(request):
    """Create a specified number of expenses for a user."""
    num_expenses = request.param
    expense = Expense("Initial", 100, "Test", "01-06-2025", "Test", TEST_USER)
    expense.setup_file_path = TEST_USER_DIR / "expenses.json"

    # Initialize budget
    setup = Setup(10000, 50000, "PKR", "USD", TEST_USER)
    setup.setup_file_path = TEST_USER_DIR / "setup.json"
    with patch.object(API, "get_exchange_rate", return_value=(280.0, "2025-06-01", "success")):
        converted_income = setup.convert_income()
        setup.set_budget(converted_income)

    # Add expenses
    for i in range(num_expenses):
        expense.name = f"Expense_{i}"
        expense.add_expense()
    return expense


@pytest.mark.parametrize("setup_expenses", [10, 100], indirect=True)
def test_add_expense_performance(setup_expenses, benchmark):
    """Test performance of adding a single expense with varying dataset sizes."""
    expense = setup_expenses
    expense.name = f"Expense_{expense.amount + 1}"

    def add_expense():
        expense.add_expense()

    start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    benchmark(add_expense)
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

    assert benchmark.stats.stats.mean < 0.1  # Adding one expense < 100ms
    assert end_memory - start_memory < 10  # Memory increase < 10MB


@pytest.mark.parametrize("setup_expenses", [10, 100], indirect=True)
def test_list_expenses_performance(setup_expenses, benchmark):
    """Test performance of listing expenses with varying dataset sizes."""
    def list_expenses():
        list(Expense.list_expenses(TEST_USER))

    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    benchmark(list_expenses)
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024

    assert benchmark.stats.stats.mean < 1.0  # Listing < 1s even for 1000 expenses
    assert end_memory - start_memory < 20  # Memory increase < 20MB


@pytest.mark.parametrize("setup_expenses", [10, 100], indirect=True)
def test_report_generation_performance(setup_expenses, benchmark):
    """Test performance of generating brief and detailed reports."""
    report = Report("monthly", None, TEST_USER)
    report.expenses_file_path = TEST_USER_DIR / "expenses.json"
    report.setup_file_path = TEST_USER_DIR / "setup.json"
    report.detailed_report_path = TEST_USER_DIR / "detailed_report_monthly.json"

    def generate_reports():
        background_task = BackgroundTasks()
        background_task.generate_reports(report)

    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    benchmark(generate_reports)
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024

    assert benchmark.stats.stats.mean < 5.0  # Report generation < 5s
    assert end_memory - start_memory < 30  # Memory increase < 30MB


@pytest.mark.parametrize("num_expenses", [100])
def test_concurrent_users_performance(num_expenses, benchmark):
    """Test performance with two users adding expenses concurrently."""
    # Setup second user
    setup_2 = Setup(10000, 50000, "PKR", "USD", TEST_USER_2)
    setup_2.setup_file_path = TEST_USER_2_DIR / "setup.json"
    with patch.object(API, "get_exchange_rate", return_value=(280.0, "2025-06-01", "success")):
        converted_income = setup_2.convert_income()
        setup_2.set_budget(converted_income)

    expense_1 = Expense("Initial", 100, "Test",
                        "01-06-2025", "Test", TEST_USER)
    expense_1.setup_file_path = TEST_USER_DIR / "expenses.json"
    expense_2 = Expense("Initial", 100, "Test",
                        "01-06-2025", "Test", TEST_USER_2)
    expense_2.setup_file_path = TEST_USER_2_DIR / "expenses.json"

    def add_concurrent_expenses():
        from threading import Thread

        def add_for_user(expense, count):
            for i in range(count):
                expense.name = f"Expense_{i}"
                expense.add_expense()

        t1 = Thread(target=add_for_user, args=(expense_1, num_expenses))
        t2 = Thread(target=add_for_user, args=(expense_2, num_expenses))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    benchmark(add_concurrent_expenses)
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024

    # Concurrent adding < 2s for 100 expenses
    assert benchmark.stats.stats.mean < 2.0
    assert end_memory - start_memory < 15  # Memory increase < 15MB


def test_api_performance(benchmark):
    """Test performance of API calls with mocked response."""
    api = API(base_currency="USD", username=TEST_USER)

    with patch.object(API, "get_exchange_rate", return_value=(280.0, "2025-06-01", "success")):
        def call_api():
            api.get_exchange_rate("PKR")

        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        benchmark(call_api)
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        assert benchmark.stats.stats.mean < 0.05  # API call < 50ms (mocked)
        assert end_memory - start_memory < 5  # Memory increase < 5MB


@pytest.mark.parametrize("num_entries", [10, 100])
def test_user_profile_performance(num_entries, benchmark):
    """Test performance of loading user profile with varying data sizes."""
    user_dir = TEST_USER_DIR
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / "user_details.json"

    # Create user profile with varying data sizes
    user_data = {"username": TEST_USER,
                 "login_time": "2025-06-01", "streak": 1}
    for i in range(num_entries):
        user_data[f"extra_field_{i}"] = f"data_{i}"
    with open(file_path, "w") as f:
        json.dump(user_data, f)

    def load_profile():
        user_profile(TEST_USER)

    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    benchmark(load_profile)
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024

    assert benchmark.stats.stats.mean < 0.1  # Profile loading < 100ms
    assert end_memory - start_memory < 10  # Memory increase < 10MB
