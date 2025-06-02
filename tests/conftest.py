import pytest
import time
import requests


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    """Wait for API to be ready before running tests"""
    max_retries = 30
    retry_interval = 1

    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            pass

        if i < max_retries - 1:
            time.sleep(retry_interval)

    pytest.fail("API did not become ready in time")
