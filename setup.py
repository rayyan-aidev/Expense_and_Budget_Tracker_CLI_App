import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from api import API

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handler (file + console)
file_handler = logging.FileHandler("tracker.log")
console_handler = logging.StreamHandler()

# Set levels
file_handler.setLevel(logging.INFO)
console_handler.setLevel(logging.DEBUG)

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
setup_file_path = BASE_DIR / "setup.json"


class Setup:
    def __init__(self, budget, income, default_currency="PKR", income_currency="PKR"):
        self.budget = budget
        self.income = income
        self.default_currency = default_currency
        self.income_currency = income_currency

    def convert_income(self):
        api = API(base_currency=self.income_currency)
        rate, last_updated, result = api.get_exchange_rate(
            self.default_currency)
        if rate:
            converted_income = self.income * rate
            logger.info(
                f"Income converted to {self.default_currency}: {converted_income}")
            return converted_income
        else:
            logger.error("Conversion failed.")
            return None

    def set_budget(self, converted_income):
        with open(setup_file_path, "w") as file:
            json.dump({
                "budget": self.budget,
                "income": converted_income,
                "default_currency": self.default_currency
            }, file, indent=4)
