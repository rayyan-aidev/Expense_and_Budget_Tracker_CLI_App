def login_screen():
    import secrets
    import random
    import os
    import json
    import time
    import bcrypt
    import msvcrt
    from pathlib import Path

    print("This is the login window.")

    def password_make(password_choice):
        if password_choice == "1":
            password = []
            for i in range(secrets.randbelow(5) + 1):
                lower_letter = secrets.choice(lower_letters)
                password.append(lower_letter)
            for i in range(secrets.randbelow(5) + 1):
                upper_letter = secrets.choice(upper_letters)
                password.append(upper_letter)
            for i in range(secrets.randbelow(5) + 1):
                digit = secrets.choice(digits)
                password.append(digit)
            for i in range(secrets.randbelow(2) + 1):
                symbol = secrets.choice(symbols)
                password.append(symbol)
            random.shuffle(password)
            password = "".join(password)
        elif password_choice == "2":
            print("Enter your password: ", end="")
            password = ""
            while True:
                ch = msvcrt.getch()

                if ch in {b'\r', b'\n'}:
                    print()
                    break

                elif ch == b'\x08':
                    if password:
                        password = password[:-1]
                        print("\b \b", end="", flush=True)

                else:
                    password += ch.decode()
                    print("*", end="", flush=True)
        else:
            print("Please enter correct action.")
            return None
        return password

    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def password_strength_check(password):
        num_of_lower_letters = 0
        num_of_upper_letters = 0
        num_of_digits = 0
        num_of_symbols = 0
        for lower_letter in lower_letters:
            if lower_letter in password:
                num_of_lower_letters += 1
        for upper_letter in upper_letters:
            if upper_letter in password:
                num_of_upper_letters += 1
        for digit in digits:
            if digit in password:
                num_of_digits += 1
        for symbol in symbols:
            if symbol in password:
                num_of_symbols += 1
        if len(password) < 8:
            print("Password length too short.")
            return None
        elif num_of_lower_letters < 1:
            print("Include atleast one lowercase letter.")
            return None
        elif num_of_upper_letters < 1:
            print("Include atleast one uppercase character.")
            return None
        elif num_of_digits < 1:
            print("Include atleast one number.")
            return None
        elif num_of_symbols < 1:
            print("Include atleast one special character.")
            return None
        else:
            return password

    def make_username(username_choice):
        if username_choice == "1":
            username = []
            for i in range(random.randint(1, 5)):
                lower_letter = random.choice(lower_letters)
                username.append(lower_letter)
            for i in range(random.randint(1, 5)):
                upper_letter = random.choice(upper_letters)
                username.append(upper_letter)
            for i in range(random.randint(1, 5)):
                digit = random.choice(digits)
                username.append(digit)
            random.shuffle(username)
            username = "".join(username)
        elif username_choice == "2":
            username = input("Enter your username: ")
        else:
            print("Please enter correct action.")
            return None
        return username

    lower_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                     'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    upper_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                     'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    symbols = ["@", "!", "#", "&", "$", "%", "*", "_", "-",
               "(", ")", "+", "=", "[", "]", "{", "}", ";", ":", "'", ",", "<", ">", "?", "/", "|",]

    BASE_DIR = Path(__file__).resolve().parent
    # File path
    file_path = BASE_DIR / "login_details.json"
    user_details = {

    }
    while True:
        try:
            action = input(
                "1-Sign in\n2-Login\n3-Forgot password\n").lower().strip().replace(" ", "")
            if action == "1":
                username_choice = input(
                    "1-Random username\n2-Type in username\n ").strip()
                username = make_username(username_choice)
                if username is None:
                    continue
                password_choice = input(
                    "1-Random password\n2-Type in password\n ").strip()
                password = None
                while password is None:
                    password = password_make(password_choice)
                password = password_strength_check(password)
                while password is None:
                    password = password_make(password_choice)
                    password = password_strength_check(password)
                if not os.path.exists(file_path):
                    with open(file_path, "w") as f:
                        json.dump({}, f)
                with open(file_path, "r") as f:
                    try:
                        content = json.load(f)
                    except Exception:
                        content = {}
                    user_details = content
                while username in user_details:
                    print("Username not available.")
                    username_choice = input(
                        "1-Random username\n2-Type in username\n ").strip()
                    username = make_username(username_choice)
                    if username is None:
                        continue
                hashed_password = hash_password(password)
                user_details[username] = {"Password": hashed_password}
                print(f"Your new username is: {username}")
                print(f"Your new password is: {password}")
                print(
                    "Please remember your username and password. It is one-time view only.")
                with open(file_path, "w") as f:
                    json.dump(user_details, f, indent=4, sort_keys=True)
                print("Sign up successful.\n\n")
                time.sleep(1)
                return True, username
            elif action == "2":
                if not os.path.exists(file_path):
                    print("No users registered yet.")
                    continue
                with open(file_path, "r") as f:
                    try:
                        content = json.load(f)
                    except Exception:
                        content = {}
                    typed_username = input(
                        "Enter your username: ").strip()
                    print("Enter your password: ", end="")
                    typed_password = ""
                    while True:
                        ch = msvcrt.getch()

                        if ch in {b'\r', b'\n'}:
                            print()
                            break

                        elif ch == b'\x08':
                            if typed_password:
                                typed_password = typed_password[:-1]
                                print("\b \b", end="", flush=True)

                        else:
                            typed_password += ch.decode()
                            print("*", end="", flush=True)
                    for key, value in content.items():
                        if typed_username == key:
                            typed_username = key
                            password = value["Password"]
                            username = typed_username
                            break
                        else:
                            continue
                    else:
                        print("User not registered. Try signing up.")
                    if bcrypt.checkpw(typed_password.encode(), password.encode()):
                        print("Login successful.\n\n")
                        time.sleep(1)
                        return True, username
                    else:
                        print("Password doesn't match")
            elif action == "3":
                if not os.path.exists(file_path):
                    print("No users registered yet.")
                    continue
                try:
                    with open(file_path, "r") as f:
                        try:
                            content = json.load(f)
                        except Exception:
                            content = {}
                except Exception:
                    content = {}
                typed_username = input("Enter your username: ").strip()
                for key, value in content.items():
                    if typed_username == key:
                        password_choice = input(
                            "1-Random password\n2-Type in password\n ").strip()
                        password = None
                        while password is None:
                            password = password_make(password_choice)
                            password = password_strength_check(password)
                        hashed_password = hash_password(password)
                        content[typed_username] = {"Password": hashed_password}
                        with open(file_path, "w") as f:
                            json.dump(content, f, indent=4, sort_keys=True)
                        print("Password updated successfully.")
                        print(f"Your new password is: {password}")
                        print("Please remember your new password.\n")
                        print("Please login to continue.\n\n")
                        time.sleep(0.5)
                        continue
                else:
                    print("User not registered.")
            else:
                print("Please enter correct action.")

        except FileNotFoundError:
            print("File not found, Creating new file.")
            with open(file_path, "w") as f:
                json.dump({}, f)
