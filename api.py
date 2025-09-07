import requests
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import os
from pathlib import Path

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
    # API logs errors to user-specific file
    file_handler.setLevel(logging.ERROR)
    console_handler.setLevel(logging.INFO)
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


class API:
    def __init__(self, base_currency="USD", username=None):
        self.base_currency = base_currency
        self.logger = setup_logging(
            username) if username else logging.getLogger('shared')
        load_dotenv()
        self.api_code = os.getenv("API_CODE")
        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_code}/latest/{self.base_currency}"

    def get_exchange_rate(self, to_currency):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            data = response.json()
            rate = data["conversion_rates"].get(to_currency)
            last_updated = data.get("time_last_update_utc", "N/A")
            result = data.get("result", "N/A")
            if rate is None:
                self.logger.error(
                    f"Exchange rate for {to_currency} not found.")
            self.logger.info(f"Time last updated: {last_updated}")
            self.logger.info(f"API result status: {result}")
            return rate, last_updated, result
        except requests.RequestException as e:
            self.logger.exception(f"Error fetching exchange rate: {e}")
            return None
