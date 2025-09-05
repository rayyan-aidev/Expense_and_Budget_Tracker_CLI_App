from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
from login import login_screen
from setup import Setup

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handler (file + console)
file_handler = logging.FileHandler(f"{__name__}.log")
console_handler = logging.StreamHandler()

# Set levels
file_handler.setLevel(logging.ERROR)
console_handler.setLevel(logging.DEBUG)

# Format
formatter = logging.Formatter(
    "%(asctime)s -%(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

if __name__ == "__main__":
    login_successful, username = login_screen()

    if login_successful:
        BASE_DIR = Path(__file__).resolve().parent
        # File path
        user_profile_path = BASE_DIR / "user_details.json"
        today = datetime.now().date()
        try:
            with open(user_profile_path, "r") as file:
                user_data = json.load(file)
                if not user_data:
                    logger.info(
                        "No user data found. Initializing new user profile.")
                    user_data = {"username": username, "login_time": today.strftime(
                        "%Y-%m-%d"), "streak": 1}
                last_login = datetime.strptime(
                    user_data.get("login_time", ""), "%Y-%m-%d").date()
                streak = user_data.get("streak", 1)
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            last_login = None
            streak = 1

        if last_login is not None:
            if today == last_login:
                print(f"Welcome back! Your current streak is {streak}.")
            elif today == last_login + timedelta(days=1):
                streak += 1
                print(f"Streak increased! Your current streak is {streak}.")
            else:
                streak = 1
                print("Streak reset. Welcome back! Your current streak is 1.")
        else:
            print("Welcome! Starting your streak.")

        user_data = {
            "username": username,
            "login_time": today.strftime("%Y-%m-%d"),
            "streak": streak
        }

        with open(user_profile_path, "w") as file:
            json.dump(user_data, file, indent=4)
        logger.info(f"{username} logged in successfully.")

        while True:
            print("----Expense Tracker----")
            choice = input(
                "1.Setup\n2.Add expense\n3.View expenses\n4.Generate Report\n5.View User Profile\n6.Exit\n").strip()
            if choice == "1":
                try:
                    budget = float(input("Enter your budget: ").strip())
                    income = float(input("Enter your income: ").strip())
                    default_currency = input(
                        "Enter your default currency (e.g., PKR): ").strip().upper()
                    income_currency = input(
                        "Enter your income currency (e.g., USD): ").strip().upper()
                    setup = Setup(budget, income,
                                  default_currency, income_currency)
                    converted_income = setup.convert_income()
                    if converted_income:
                        setup.set_budget(converted_income)
                        print("Setup completed successfully.")
                    else:
                        print("Setup failed due to conversion error.")
                except ValueError:
                    print(
                        "Invalid input. Please enter numeric values for budget and income.")
                    logger.exception("Invalid input during setup.")
