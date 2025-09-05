import pytest
from transaction import Expense
import json


@pytest.fixture
def expense():
    return Expense("Test Expense", 100, "Test", "2024-06-01", "Test Category")


def test_add_expense(expense):
    expense.add_expense()
    with open("expenses.json", "r") as file:
        expenses = json.load(file)
    assert "Test Expense" in expenses
    assert expenses["Test Expense"]["amount"] == 100


def test_load_expense(expense):
    expense.add_expense()
    loaded_expense = expense.load_expense("Test Expense")
    assert loaded_expense is not None
    assert loaded_expense["amount"] == 100


def test_update_expense(expense):
    expense.add_expense()
    expense.update_expense("Test Expense", amount=150)
    loaded_expense = expense.load_expense("Test Expense")
    assert loaded_expense["amount"] == 150


def test_delete_expense(expense):
    expense.add_expense()
    expense.delete_expense("Test Expense")
    loaded_expense = expense.load_expense("Test Expense")
    assert loaded_expense is None


def test_list_expenses(expense):
    expense.add_expense()
    expenses = list(expense.list_expenses())
    assert any("Test Expense" in exp for exp in expenses)


def test_check_budget(expense):
    expense.add_expense()
    remaining_budget = expense.check_budget()
    with open("expenses.json", "r") as file:
        data = json.load(file)
    initial_budget = data.get("budget_info", {}).get("initial_budget", 0)
    # Assuming initial budget is less than or equal to 100
    assert remaining_budget <= initial_budget
