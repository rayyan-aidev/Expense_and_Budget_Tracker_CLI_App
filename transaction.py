from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
from Multithreading_Multiprocessing import BackgroundTasks
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handler (file + console)
file_handler = logging.FileHandler("tracker.log")
console_handler = logging.StreamHandler()

# Set levels
file_handler.setLevel(logging.INFO)
console_handler.setLevel(logging.WARNING)

# Format
formatter = logging.Formatter(
    "%(asctime)s -%(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

BASE_DIR = Path(__file__).resolve().parent
# File path
setup_file_path = BASE_DIR / "expenses.json"


class Expense:
    def __init__(self, name, amount, category, date=None, description=""):
        self.name = name
        self.amount = amount
        self.category = category
        self.date = date if date else datetime.now().strftime("%d-%m-%Y")
        self.description = description

    def to_dict(self):
        return {
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "description": self.description
        }

    def set_budget(self):
        try:
            setup = BackgroundTasks(BASE_DIR/"setup.json", "r")
            setup_data = setup.background_fileIO()
            initial_budget = setup_data.get("budget", 0)
            income = setup_data.get("income", 0)

            # Load or create expenses file
            if setup_file_path.exists():
                expenses = BackgroundTasks(setup_file_path, "r")
                expenses_data = expenses.background_fileIO()
            else:
                expenses_data = {}

            current_month = datetime.now().strftime("%Y-%m")

            # Check if we need to reset monthly budget
            if "budget_info" not in expenses_data or expenses_data["budget_info"].get("month") != current_month:
                expenses_data["budget_info"] = {
                    "month": current_month,
                    "initial_budget": initial_budget,
                    "current_budget": initial_budget,
                    "income": income
                }

                expenses = BackgroundTasks(setup_file_path, "w")
                expenses.background_fileIO(expenses_data)
                logger.info(f"Monthly budget reset to: {initial_budget}")
        except Exception as e:
            logger.exception(f"Failed to set budget: {e}")
            return 0

    def add_expense(self):
        try:
            expenses_reader = BackgroundTasks(setup_file_path, "r")
            expenses = expenses_reader.background_fileIO() if setup_file_path.exists() else {}
            if expenses is None:
                expenses = {}

            # Initialize budget if not exists
            if "budget_info" not in expenses:
                self.set_budget()
                time.sleep(0.4)
                expenses_reader = BackgroundTasks(setup_file_path, "r")
                expenses = expenses_reader.background_fileIO()
                if expenses is None:
                    raise Exception("Failed to read expenses file")

            # Update current budget
            current_budget = expenses["budget_info"]["current_budget"]
            expenses["budget_info"]["current_budget"] = current_budget - self.amount

            # Save expense
            expense = self.to_dict()
            expenses[self.name] = expense

            expenses_handler = BackgroundTasks(setup_file_path, "w")
            expenses_handler.background_fileIO(expenses)

            logger.info(f"Expense saved and budget updated: {self.to_dict()}")
        except Exception as e:
            logger.error(f"Failed to save expense: {e}")

    @classmethod
    def load_expense(cls, expense_name):
        try:
            if setup_file_path.exists():
                expenses = BackgroundTasks(setup_file_path, "r")
                expenses_data = expenses.background_fileIO()
                if expenses_data:
                    expense_data = expenses_data.get(expense_name)
                    if expense_data:
                        logger.info(f"Expense loaded: {expense_data}")
                        return expense_data
                    else:
                        logger.warning(
                            f"No expense found with name: {expense_name}")
                        return None
            else:
                logger.warning("No expenses file found.")
                return None
        except Exception as e:
            logger.error(f"Failed to load expense: {e}")
            return None

    @classmethod
    def delete_expense(cls, expense_name):
        try:
            if setup_file_path.exists():
                with open(setup_file_path, "r") as file:
                    expenses = json.load(file)

                if expense_name in expenses and expense_name != "budget_info":
                    # Get the expense amount before deleting
                    deleted_amount = expenses[expense_name]["amount"]
                    # Update current budget by adding back the deleted expense amount
                    expenses["budget_info"]["current_budget"] += deleted_amount
                    # Delete the expense
                    del expenses[expense_name]
                    expenses_handler = BackgroundTasks(setup_file_path, "w")
                    expenses_handler.background_fileIO(expenses)
                    logger.info(f"Expense deleted: {expense_name}")
                else:
                    logger.warning(
                        f"No expense found with name: {expense_name}")
            else:
                logger.warning("No expenses file found.")
        except Exception as e:
            logger.error(f"Failed to delete expense: {e}")

    @classmethod
    def update_expense(cls, expense_name, **kwargs):
        try:
            expenses_reader = BackgroundTasks(setup_file_path, "r")
            expenses = expenses_reader.background_fileIO() if setup_file_path.exists() else None
            if expenses is None:
                logger.error("Failed to read expenses file")
                return

            if expense_name in expenses:
                old_amount = expenses[expense_name].get("amount", 0)
                new_amount = kwargs.get("amount", old_amount)

                # Update budget if amount changed
                if "amount" in kwargs:
                    expenses["budget_info"]["current_budget"] += (
                        old_amount - new_amount)

                # Update expense fields
                for key, value in kwargs.items():
                    if key in expenses[expense_name]:
                        expenses[expense_name][key] = value

                expenses_handler = BackgroundTasks(setup_file_path, "w")
                if not expenses_handler.background_fileIO(expenses):
                    logger.error("Failed to save updated expenses")
                    return
                logger.info(f"Expense updated: {expense_name} with {kwargs}")
            else:
                logger.warning(f"No expense found with name: {expense_name}")
        except Exception as e:
            logger.error(f"Failed to update expense: {e}")

    @classmethod
    def list_expenses(cls):
        try:
            if setup_file_path.exists():
                with open(setup_file_path, "r") as file:
                    expenses = json.load(file)
                for expense in expenses:
                    yield expense
            else:
                logger.warning("No expenses file found.")
                return {}
        except Exception as e:
            logger.exception(f"Failed to list expenses: {e}")
            return {}

    @classmethod
    def check_budget(cls):
        try:
            with open(setup_file_path, "r") as file:
                expenses = json.load(file)
                budget_info = expenses.get("budget_info", {})
                current_budget = budget_info.get("current_budget", 0)

            if current_budget < 0:
                logger.warning(f"Budget exceeded by {-current_budget}!")
            elif sum(
                    exp.get("amount", 0) for name, exp in expenses.items() if name != "budget_info"
            ) > budget_info.get("income", 0):
                logger.critical("Total expenses exceed the income!")
            else:
                logger.info(f"Remaining budget: {current_budget}")
            return current_budget
        except Exception as e:
            logger.exception(f"Failed to check budget: {e}")
            return 0
