from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
import time
from login import login_screen
from setup import Setup
from transaction import Expense

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

        def validate_currency(func):
            def wrapper(*args, **kwargs):
                default_currency, income_currency = func(*args, **kwargs)
                if not (default_currency) or not (default_currency.isalpha()):
                    logger.error("Invalid default currency.")
                    return None, None
                if not (income_currency) or not (income_currency.isalpha()):
                    logger.error("Invalid income currency.")
                    return None, None
                if len(default_currency) != 3 or len(income_currency) != 3:
                    logger.error("Currency codes must be 3 letters long.")
                    return None, None
                return default_currency, income_currency
            return wrapper

        @validate_currency
        def get_currency():
            default_currency = input(
                "Enter your default currency (e.g., PKR): ").strip().upper()
            income_currency = input(
                "Enter your income currency (e.g., USD): ").strip().upper()
            return default_currency, income_currency

        while True:
            print("----Expense Tracker----")
            choice = input(
                "1.Setup\n2.Add expense\n3.View or Change expenses\n4.Generate Report\n5.View User Profile\n6.Exit\n").strip()
            if choice == "1":
                try:
                    budget = float(input("Enter your budget: ").strip())
                    income = float(input("Enter your income: ").strip())
                    default_currency, income_currency = get_currency()
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
            elif choice == "2":
                name = input("Enter expense name: ").strip()
                try:
                    amount = float(input("Enter expense amount: ").strip())
                    category = input("Enter expense category: ").strip()
                    date_input = input(
                        "Enter expense date (DD-MM-YYYY) or leave blank for today: ").strip()
                    date = date_input if date_input else None
                    description = input(
                        "Enter expense description (optional): ").strip()
                    expense = Expense(
                        name, amount, category, date, description)
                    expense.add_expense()
                    remaining_budget = expense.check_budget()
                    if remaining_budget is not None:
                        print(
                            f"Expense added successfully. Remaining budget: {remaining_budget}")
                    else:
                        print(
                            "Expense added, but failed to retrieve remaining budget.")
                except ValueError:
                    print("Invalid amount. Please enter a numeric value.")
                    logger.exception("Invalid amount entered for expense.")
                    continue
            elif choice == "3":
                command = input(
                    "1.View all expenses\n2.Search expense by name\n3.Update expense\n4.Delete expense\n").strip()
                if command == "1":
                    Expense.list_expenses()
                elif command == "2":
                    name = input("Enter expense name to search: ").strip()
                    expense_data = Expense.load_expense(name)
                    if expense_data:
                        print(f"Expense found: {expense_data}")
                    else:
                        print("Expense not found.")
                elif command == "3":
                    name = input("Enter expense name to update: ").strip()
                    print("Enter new values (leave blank to keep current value):")
                    new_amount = input("New amount: ").strip()
                    new_category = input("New category: ").strip()
                    new_date = input("New date (DD-MM-YYYY): ").strip()
                    new_description = input(
                        "New description (optional): ").strip()
                    update_fields = {}
                    if new_amount:
                        try:
                            update_fields["amount"] = float(new_amount)
                        except ValueError:
                            print("Invalid amount. Please enter a numeric value.")
                            logger.exception(
                                "Invalid amount entered for update.")
                            continue
                    if new_category:
                        update_fields["category"] = new_category
                    if new_date:
                        update_fields["date"] = new_date
                    if new_description:
                        update_fields["description"] = new_description
                    if update_fields:
                        Expense.update_expense(name, **update_fields)
                        print("Expense updated successfully.")
                    else:
                        print("No updates provided.")
                elif command == "4":
                    name = input("Enter expense name to delete: ").strip()
                    Expense.delete_expense(name)
                    print("Expense deleted successfully.")
                else:
                    print("Invalid command.")
            elif choice == "4":
                pass
            elif choice == "5":
                pass
            elif choice == "6":
                print("Exiting the application. Goodbye!")
                time.sleep(0.3)
                break
            else:
                print("Invalid choice. Please try again.")
        print("Thank you for using the Expense Tracker.")
