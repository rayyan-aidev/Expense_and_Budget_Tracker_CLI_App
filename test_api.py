import pytest
from api import API


@pytest.fixture
def api_instance():
    return API(base_currency="USD")


def test_get_exchange_rate_valid(api_instance):
    rate, last_updated, result = api_instance.get_exchange_rate("PKR")
    assert rate is not None
    assert isinstance(rate, (int, float))
    assert rate > 0
    assert result == "success"
