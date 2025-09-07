import logging
from pathlib import Path
from Multithreading_Multiprocessing import BackgroundTasks
from datetime import datetime, timedelta
import json
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


class Report:
    def __init__(self, time_period, category=None):
        self.time_period = time_period
        self.category = category
        self._initialize_paths()

    def _initialize_paths(self):
        self.expenses_file_path = BASE_DIR / "expenses.json"
        self.setup_file_path = BASE_DIR / "setup.json"
        self.detailed_report_path = BASE_DIR / \
            f"detailed_report_{self.time_period}.json"

    def brief_generate_report(self):
        try:
            with open(self.expenses_file_path, 'r') as f:
                expenses_data = json.load(f)
            with open(self.setup_file_path, 'r') as f:
                setup_data = json.load(f)
            if not expenses_data:
                logger.warning("No expenses data found.")
                return None

            if not setup_data:
                logger.warning("No setup data found.")
                return None

            # Determine the start date based on the time period
            end_date = datetime.now()
            if self.time_period.lower() == "d":
                start_date = end_date - timedelta(days=1)
            elif self.time_period.lower() == "w":
                start_date = end_date - timedelta(weeks=1)
            elif self.time_period.lower() == "m":
                start_date = end_date - timedelta(days=30)
            elif self.time_period.lower() == "y":
                start_date = end_date - timedelta(days=365)
            else:
                logger.error("Invalid time period specified.")
                return None

            # Filter expenses based on date and category
            filtered_expenses = {}
            total_expense = 0
            for name, details in expenses_data.items():
                if name == "budget_info":
                    continue
                expense_date = datetime.strptime(details["date"], "%d-%m-%Y")
                if start_date <= expense_date <= end_date:
                    if self.category is None or details["category"] == self.category:
                        filtered_expenses[name] = details
                        total_expense += details["amount"]

            brief_report = {
                "time_period": self.time_period,
                "category": self.category,
                "total_expense": total_expense,
                "remaining_budget": setup_data.get("budget", 0) - total_expense,
                "expenses": filtered_expenses
            }

            logger.info(f"Report generated for {self.time_period} period.")
            return brief_report

        except Exception as e:
            logger.exception(f"Error generating report: {e}")
            return None

    def detailed_generate_report(self, no_save=False):
        try:
            with open(self.expenses_file_path, 'r') as f:
                expenses_data = json.load(f)
            with open(self.setup_file_path, 'r') as f:
                setup_data = json.load(f)
            if not expenses_data:
                logger.warning("No expenses data found.")
                return None

            if not setup_data:
                logger.warning("No setup data found.")
                return None

            # Determine the start date based on the time period
            end_date = datetime.now()
            if self.time_period.lower() == "d":
                start_date = end_date - timedelta(days=1)
            elif self.time_period.lower() == "w":
                start_date = end_date - timedelta(weeks=1)
            elif self.time_period.lower() == "m":
                start_date = end_date - timedelta(days=30)
            elif self.time_period.lower() == "y":
                start_date = end_date - timedelta(days=365)
            else:
                logger.error("Invalid time period specified.")
                return None

            # Filter expenses based on date and category
            filtered_expenses = {}
            total_expense = 0
            for name, details in expenses_data.items():
                if name == "budget_info":
                    continue
                expense_date = datetime.strptime(details["date"], "%d-%m-%Y")
                if start_date <= expense_date <= end_date:
                    if self.category is None or details["category"] == self.category:
                        filtered_expenses[name] = details
                        total_expense += details["amount"]

            detailed_report = {
                "time_period": self.time_period,
                "category": self.category,
                "total_expense": total_expense,
                "remaining_budget": setup_data.get("budget", 0) - total_expense,
                "expenses": filtered_expenses,
                "budget_info": expenses_data.get("budget_info", {})
            }

            logger.info(
                f"Detailed report generated for {self.time_period} period.")
            if not no_save:
                report_handler = BackgroundTasks(
                    BASE_DIR / f"detailed_report_{self.time_period}.json", "w")
                report_handler.background_fileIO(detailed_report)

            return detailed_report

        except Exception as e:
            logger.exception(f"Error generating detailed report: {e}")
            return None
