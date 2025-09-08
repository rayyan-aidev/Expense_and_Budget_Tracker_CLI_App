# 🧾 Expense Tracker

A modular, beginner-friendly **Command-Line Interface (CLI) Expense Tracker** for managing personal finances.  
Track expenses, set budgets, generate reports, and convert currencies — all from the terminal!  
Supports multiple users with isolated data and includes a robust test suite for reliability.

---

## 🚀 Features

### 👤 Multi-User Support
- Isolated data storage in `users/<username>/`
- Track login streaks for user engagement

### 💸 Expense Management
- Add, view, update, and delete expenses (amount, category, date, description)
- JSON-based storage for persistence

### 💰 Budget Setup
- Configure budgets  
- Convert income across currencies using an external API

### 📊 Report Generation
- Brief and detailed reports for daily, weekly, monthly, or yearly periods
- Asynchronous processing with `Multithreading_Multiprocessing.py`

### 📜 Logging System
- User-specific logs (`tracker.log`, 5MB, 3 backups)
- Shared error log (`tracker.log`, 10MB, 5 backups) using `RotatingFileHandler`

### 🧪 Comprehensive Testing
- Functional tests for all core features
- Performance tests for scalability using **pytest-benchmark** and **psutil**

---

## 🗂️ Project Structure

expense-tracker/
├── main.py # CLI entry point and menu logic
├── report.py # Generates brief and detailed reports
├── setup.py # Configures budgets and currencies
├── transaction.py # Manages expense operations
├── Multithreading_Multiprocessing.py # Async file I/O and report processing
├── api.py # Currency conversion via external API
├── user_profile.py # User profile and streak tracking
├── test_api.py # Tests for API functionality
├── test_main.py # Tests for CLI menu navigation
├── test_multithreading_multiprocessing.py # Tests for async operations
├── test_setup.py # Tests for budget setup
├── test_transaction.py # Tests for expense operations
├── test_performance.py # Performance tests for scalability
├── test_report.py # Tests for report generation
├── README.md # Project documentation
├── LICENSE # MIT License
├── requirements.txt # Project dependencies
├── .env # API key (not tracked)
├── tracker.log # Shared error log
├── test_performance.log # Test-specific log for debugging
├── users/
│ ├── <username>/
│ │ ├── expenses.json # User expenses
│ │ ├── setup.json # Budget and currency settings
│ │ ├── user_details.json # User profile and streak
│ │ ├── tracker.log # User-specific log
│ │ ├── detailed_report_<period>.json # Detailed reports

---

## 🛠️ Technologies Used

- **Python 3.6+**
- **Built-in modules:** `json`, `os`, `pathlib`, `datetime`, `time`, `threading`, `multiprocessing`, `logging`
- **External modules:**
  - `requests` (API calls)
  - `python-dotenv` (environment variables for API key)
  - `pytest`, `pytest-benchmark`, `psutil` (testing)
- **File-based persistence:** JSON storage

---

## 🧑‍🏫 How It Works

1. Run `main.py` to start the CLI.
2. Log in with a username (no password required).
3. Use the menu to:
   - Set up budgets and currencies  
   - Add, view, or manage expenses  
   - Generate reports (brief or detailed)  
   - View user profile and login streak  
4. Tests ensure functionality and performance (see Testing section).

---

## 📌 Requirements

- Python 3.6 or higher
- Install dependencies:

```bash
pip install requests python-dotenv pytest pytest-benchmark psutil
```

---

## 🧰 Setup Instructions

1. Clone the Repository
```bash
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker
```
2. Install Dependencies
```bash
pip install -r requirements.txt
```
3. Set Up API Key
Create a .env file in the project root:
API_KEY=your_api_key_here
4. Run the Application
```bash
python main.py
```

---

## 🧪 Testing
### Functional Tests

- **Files**:
test_api.py, test_main.py, test_multithreading_multiprocessing.py,
test_setup.py, test_transaction.py, test_report.py

- Coverage: API calls, expense operations, budget setup, async file I/O, menu navigation, report generation.

- Run:
```bash
pytest -v
```

---

### Performance Tests

- Files: test_performance.py, test_report.py

- Coverage: Execution time and memory usage for expense operations, report generation, concurrent users.

- Run:
```bash
pytest test_performance.py test_report.py -v --benchmark-enable
```
- Debugging:
```bash
cat test_performance.log
pytest test_performance.py::test_concurrent_users_performance -v --tb=long
```

---

## Contributing

1. Fork the repository
2. Create a feature branch:
```bash
git checkout -b feature/your-feature
```
3. Commit changes:
```bash
git commit -m "Add your feature"
```
4. Push and open a Pull Request.
✅ Include tests
✅ Follow PEP 8

---

## 📬 Contact

For questions or suggestions:
📧 Email: rayyanaqeel1310@gmail.com
💬 Or open a GitHub Issue

## 📄 License

This project is licensed under the **MIT License**.

## 🌟 Show Your Support

If you like this project:
- ⭐ Star the repo
- 🐛 Report bugs
- ✅ Suggest features
- 🔗 Share it!
