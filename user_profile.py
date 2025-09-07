import os
from pathlib import Path
import json
import time
import logging

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


def user_profile():
    BASE_DIR = Path(__file__).resolve().parent
    file_path = BASE_DIR / "user_profile.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                user_data = json.load(file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            print("User profile file is empty or corrupted. PLease create a new profile.")
            logger.exception("Error reading user profile file.")
            user_data = {}
    else:
        user_data = {}

    print("\nUser Profile:")
    if not user_data:
        print("No user data found.")
    else:
        for key, value in user_data.items():
            print(f"{key}: {value}")
