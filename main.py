from login import login_screen
from datetime import datetime, timedelta
import json
from pathlib import Path


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
                    print("No user profile found. Creating a new profile.")
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

        try:
            with open(user_profile_path, "r") as file:
                user_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Please login again.")
