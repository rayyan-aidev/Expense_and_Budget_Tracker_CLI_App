from threading import Thread, Event
from multiprocessing import Process, Queue
import logging
from datetime import datetime
from pathlib import Path
import json

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

BASE_DIR = Path(__file__).resolve().parent


def process_report(time_period, category, report_type, result_queue):
    """Standalone function for report processing"""
    try:
        from report import Report
        report_obj = Report(time_period, category)
        if report_type == "brief":
            result = report_obj.brief_generate_report()
        else:
            result = report_obj.detailed_generate_report(
                no_save=True)  # Pass no_save=True
        result_queue.put((report_type, result))
    except Exception as e:
        logger.error(f"Error generating {report_type} report: {e}")
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
            with open(self.file_path, self.mode) as file:
                json.dump(data, file, indent=4)
            logger.info(f"Data saved to {self.file_path}")
        except Exception as e:
            logger.exception(f"Error saving data to {self.file_path}: {e}")
        finally:
            self.event.set()

    def read_from_file(self):
        try:
            with open(self.file_path, self.mode) as file:
                self.data = json.load(file)
            logger.info(f"Data read from {self.file_path}")
        except Exception as e:
            logger.exception(f"Error reading data from {self.file_path}: {e}")
            self.data = None
        finally:
            self.event.set()

    def background_fileIO(self, data=None):
        self.event.clear()
        if self.mode == "w":
            t = Thread(target=self.save_to_file, args=(data,))
            t.daemon = True
            t.start()
            self.event.wait(timeout=5)  # Wait up to 5 seconds for completion
            return True
        elif self.mode == "r":
            t = Thread(target=self.read_from_file)
            t.daemon = True
            t.start()
            self.event.wait(timeout=5)  # Wait up to 5 seconds for completion
            return self.data
        else:
            logger.error("Invalid mode. Use 'r' for read or 'w' for write.")
            return None

    def generate_reports(self, report_obj):
        try:
            # Create processes for both report types
            brief_process = Process(
                target=process_report,
                args=(report_obj.time_period, report_obj.category,
                      "brief", self.result_queue)
            )
            detailed_process = Process(
                target=process_report,
                args=(report_obj.time_period, report_obj.category,
                      "detailed", self.result_queue)
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
                report_handler = BackgroundTasks(
                    BASE_DIR /
                    f"detailed_report_{report_obj.time_period}.json", "w"
                )
                report_handler.background_fileIO(results["detailed"])

            return results
        except Exception as e:
            logger.error(f"Error in report generation: {e}")
            return None
