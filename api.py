import requests
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handler (file + console)
file_handler = logging.FileHandler(f"{__name__}.log")
console_handler = logging.StreamHandler()

# Set levels
file_handler.setLevel(logging.ERROR)
console_handler.setLevel(logging.INFO)
# Format
formatter = logging.Formatter(
    "%(asctime)s -%(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class API:
    def __init__(self, base_currency="USD"):
        self.base_currency = base_currency
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
                logger.error(f"Exchange rate for {to_currency} not found.")
            logger.info(f"Time last updated: {last_updated}")
            logger.info(f"API result status: {result}")
            return rate, last_updated, result
        except requests.RequestException as e:
            logger.error(f"Error fetching exchange rate: {e}")
            return None
