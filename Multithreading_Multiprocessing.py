from threading import Thread, Event
from multiprocessing import Process
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


class BackgroundTasks:
    def __init__(self, file_path, mode):
        self.file_path = file_path
        self.mode = mode
        self.data = None
        self.event = Event()

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
