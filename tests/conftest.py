import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_env_setup():
    """Set up test environment with mock API key for all tests"""
    with patch.dict(os.environ, {"JINA_API_KEY": "test-jina-api-key-for-testing"}):
        yield
