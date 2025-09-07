import os
from pathlib import Path
import json
import time
import logging
from logging.handlers import RotatingFileHandler

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


def user_profile(username):
    logger = setup_logging(username)
    user_dir = BASE_DIR / "users" / username
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / "user_details.json"

    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                user_data = json.load(file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            logger.exception("Error reading user profile file.")
            print("User profile file is empty or corrupted. Please create a new profile.")
            user_data = {}
    else:
        user_data = {}
        logger.warning(f"No user profile file found for {username}.")

    print("\nUser Profile:")
    if not user_data:
        print("No user data found.")
    else:
        for key, value in user_data.items():
            print(f"{key}: {value}")
    logger.info(f"Displayed user profile for {username}.")
