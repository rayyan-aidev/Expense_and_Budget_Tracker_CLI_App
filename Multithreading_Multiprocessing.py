from threading import Thread, Event
from multiprocessing import Process, Queue
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
import json

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


def process_report(time_period, category, report_type, result_queue, username):
    """Standalone function for report processing"""
    logger = setup_logging(username)
    try:
        from report import Report
        report_obj = Report(time_period, category, username)
        if report_type == "brief":
            result = report_obj.brief_generate_report()
        else:
            result = report_obj.detailed_generate_report(
                no_save=True)  # Pass no_save=True
        result_queue.put((report_type, result))
    except Exception as e:
        logger.exception(f"Error generating {report_type} report: {e}")
        result_queue.put((report_type, None))


class BackgroundTasks:
    def __init__(self, file_path=None, mode=None):
        self.file_path = file_path
        self.mode = mode
        self.data = None
        self.event = Event()
        self.result_queue = Queue()

    def save_to_file(self, data):
        try:
            # Ensure the parent directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, self.mode) as file:
                json.dump(data, file, indent=4)
            # Logger not available here; logging done in calling context
        except Exception as e:
            # Use shared logger for errors in this context
            temp_logger = logging.getLogger('shared')
            temp_logger.exception(
                f"Error saving data to {self.file_path}: {e}")
        finally:
            self.event.set()

    def read_from_file(self):
        try:
            with open(self.file_path, self.mode) as file:
                self.data = json.load(file)
            # Logger not available here; logging done in calling context
        except Exception as e:
            # Use shared logger for errors in this context
            temp_logger = logging.getLogger('shared')
            temp_logger.exception(
                f"Error reading data from {self.file_path}: {e}")
            self.data = None
        finally:
            self.event.set()

    def background_fileIO(self, data=None):
        self.event.clear()
        if self.mode == "w":
            t = Thread(target=self.save_to_file, args=(data,))
            t.daemon = True
            t.start()
            self.event.wait(timeout=5)
            return True
        elif self.mode == "r":
            t = Thread(target=self.read_from_file)
            t.daemon = True
            t.start()
            self.event.wait(timeout=5)
            return self.data
        else:
            # Use shared logger for errors in this context
            temp_logger = logging.getLogger('shared')
            temp_logger.error(
                "Invalid mode. Use 'r' for read or 'w' for write.")
            return None

    def generate_reports(self, report_obj):
        logger = setup_logging(report_obj.username)
        try:
            # Create processes for both report types
            brief_process = Process(
                target=process_report,
                args=(report_obj.time_period, report_obj.category,
                      "brief", self.result_queue, report_obj.username)
            )
            detailed_process = Process(
                target=process_report,
                args=(report_obj.time_period, report_obj.category,
                      "detailed", self.result_queue, report_obj.username)
            )

            # Start processes
            brief_process.start()
            detailed_process.start()

            # Wait for processes to complete (with timeout)
            brief_process.join(timeout=10)
            detailed_process.join(timeout=10)

            # Collect results
            results = {}
            while not self.result_queue.empty():
                report_type, report_data = self.result_queue.get()
                results[report_type] = report_data

            # Save detailed report in the main process
            if results.get("detailed"):
                user_dir = BASE_DIR / "users" / report_obj.username
                user_dir.mkdir(parents=True, exist_ok=True)
                report_handler = BackgroundTasks(
                    user_dir /
                    f"detailed_report_{report_obj.time_period}.json", "w"
                )
                report_handler.background_fileIO(results["detailed"])

            return results
        except Exception as e:
            logger.exception(f"Error in report generation: {e}")
            return None
