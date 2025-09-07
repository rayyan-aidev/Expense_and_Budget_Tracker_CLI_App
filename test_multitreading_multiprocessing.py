import pytest
import logging
from Multithreading_Multiprocessing import BackgroundTasks
import json


@pytest.fixture
def background_tasks_write():
    return BackgroundTasks("test.json", "w")


@pytest.fixture
def background_tasks_read():
    return BackgroundTasks("test.json", "r")


def test_save_to_file(background_tasks_write):
    data = {"key": "value"}
    background_tasks_write.save_to_file(data)
    with open("test.json", "r") as file:
        loaded_data = json.load(file)
    assert loaded_data == data


def test_read_from_file(background_tasks_read):
    data = {"key": "value"}
    with open("test.json", "w") as file:
        json.dump(data, file)
    loaded_data = background_tasks_read.read_from_file()
    assert loaded_data == data


def test_background_fileIO(background_tasks_write, background_tasks_read):
    data = {"key": "value"}
    background_tasks_write.background_fileIO(data)
    import time
    time.sleep(1)  # Wait for the thread to finish
    loaded_data = background_tasks_read.read_from_file()
    assert loaded_data == data
