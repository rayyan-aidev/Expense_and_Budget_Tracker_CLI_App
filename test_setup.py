import pytest
from setup import Setup
import json


@pytest.fixture
def setup_instance():
    return Setup(budget=1000, income=5000, default_currency="PKR", income_currency="USD")


def test_convert_income(setup_instance):
    converted_income = setup_instance.convert_income()
    assert converted_income is not None
    assert isinstance(converted_income, float)
    assert converted_income > 0
    assert converted_income != setup_instance.income  # Should be converted


def test_set_budget(tmp_path, setup_instance):
    converted_income = setup_instance.convert_income()
    assert converted_income is not None
    setup_instance.set_budget(converted_income)

    setup_file_path = tmp_path / "setup.json"
    with open(setup_file_path, "r") as file:
        data = json.load(file)

    assert data["budget"] == setup_instance.budget
    assert data["income"] == converted_income
    assert data["default_currency"] == setup_instance.default_currency
