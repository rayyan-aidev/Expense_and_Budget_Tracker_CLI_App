import logging
from logging.handlers import RotatingFileHandler
import json
from pathlib import Path
from datetime import datetime, timedelta
from api import API

# Shared logger for system-wide errors (configured once)
shared_logger = None


def setup_logging(username):
    global shared_logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    user_dir = BASE_DIR / "users" / username
    user_dir.mkdir(parents=True, exist_ok=True)

    # User-specific log with rotation
    file_handler = RotatingFileHandler(
        user_dir / "tracker.log", maxBytes=5*1024*1024, backupCount=3
    )
    console_handler = logging.StreamHandler()
    file_handler.setLevel(logging.INFO)
    console_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        "%(asctime)s -%(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Configure shared logger for ERROR and CRITICAL (only once)
    if shared_logger is None:
        shared_logger = logging.getLogger('shared')
        shared_logger.setLevel(logging.ERROR)
        shared_file_handler = RotatingFileHandler(
            BASE_DIR / "tracker.log", maxBytes=10*1024*1024, backupCount=5
        )
        shared_file_handler.setFormatter(formatter)
        shared_logger.handlers = [shared_file_handler]

    # Clear existing handlers to avoid duplicates
    logger.handlers = []
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    # Add shared handler for ERROR/CRITICAL
    logger.addHandler(shared_logger.handlers[0])
    return logger


BASE_DIR = Path(__file__).resolve().parent


class Setup:
    def __init__(self, budget, income, default_currency="PKR", income_currency="PKR", username=None):
        self.budget = budget
        self.income = income
        self.default_currency = default_currency
        self.income_currency = income_currency
        self.username = username
        self.logger = setup_logging(username)
        user_dir = BASE_DIR / "users" / self.username
        user_dir.mkdir(parents=True, exist_ok=True)
        self.setup_file_path = user_dir / "setup.json"

    def convert_income(self):
        api = API(base_currency=self.income_currency, username=self.username)
        rate, last_updated, result = api.get_exchange_rate(
            self.default_currency)
        if rate:
            converted_income = self.income * rate
            self.logger.info(
                f"Income converted to {self.default_currency}: {converted_income}")
            return converted_income
        else:
            self.logger.error("Conversion failed.")
            return None

    def set_budget(self, converted_income):
        with open(self.setup_file_path, "w") as file:
            json.dump({
                "budget": self.budget,
                "income": converted_income,
                "default_currency": self.default_currency
            }, file, indent=4)
