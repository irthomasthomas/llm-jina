import pytest
import httpx
import time
from unittest.mock import patch, mock_open
import os
import builtins
from llm_jina.metaprompt import jina_metaprompt, fetch_metaprompt
import click


@pytest.fixture
def mock_response():
    """Mock httpx response with test metaprompt content"""
    class MockResponse:
        def __init__(self, status_code=200):
            self.status_code = status_code
            self.text = "# Jina Metaprompt Test\nThis is test content for the metaprompt."
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise httpx.HTTPStatusError("Error", request=None, response=self)
    
    return MockResponse()


def test_fetch_metaprompt_success(mock_response):
    """Test successful fetching of the metaprompt"""
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        result = fetch_metaprompt()
        assert result == mock_response.text
        assert "Jina Metaprompt Test" in result


def test_fetch_metaprompt_failure():
    """Test handling of fetch failure"""
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.RequestError("Network error", request=None)
        result = fetch_metaprompt()
        assert result is None


def test_jina_metaprompt_from_cache():
    """Test retrieving metaprompt from cache"""
    cache_content = "# Cached Metaprompt\nThis is from the cache."
    
    # Mock the file exists and was modified recently
    with patch('os.path.exists', return_value=True), \
         patch('os.path.getmtime', return_value=time.time() - 3600), \
         patch('builtins.open', mock_open(read_data=cache_content)):
        result = jina_metaprompt()
        assert result == cache_content
        assert "Cached Metaprompt" in result


def test_jina_metaprompt_fetch_and_cache(mock_response):
    """Test fetching metaprompt and caching it"""
    # Mock the file doesn't exist or is outdated
    with patch('os.path.exists', return_value=False), \
         patch('httpx.Client') as mock_client, \
         patch('builtins.open', mock_open()) as mock_file:
        
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        result = jina_metaprompt()
        
        assert result == mock_response.text
        mock_file.assert_called_with("jina-metaprompt.md", "w")
        mock_file().write.assert_called_once_with(mock_response.text)


def test_jina_metaprompt_error_handling():
    """Test error handling when metaprompt can't be fetched or found"""
    # Mock both remote fetch and cache file access fail
    with patch('os.path.exists', return_value=False), \
         patch('httpx.Client') as mock_client:
        
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.RequestError("Network error", request=None)
        
        with pytest.raises(click.ClickException) as excinfo:
            jina_metaprompt()
        
        assert "Failed to fetch metaprompt" in str(excinfo.value)
