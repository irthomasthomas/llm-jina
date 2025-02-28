import pytest
import httpx
import os
from unittest.mock import patch, MagicMock
from llm_jina.api import (
    jina_request, jina_embed, jina_search, jina_read,
    jina_rerank, jina_classify_text, jina_classify_images,
    jina_segment, jina_ground, rerank_documents, APIError, 
    jina_metaprompt_api, JINA_API_KEY
)


@pytest.fixture
def mock_env():
    """Set up test environment variables"""
    original_env = os.environ.copy()
    os.environ["JINA_API_KEY"] = "test-api-key"
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_response():
    """Create a mock response object"""
    class MockResponse:
        def __init__(self, status_code=200, json_data=None, text=""):
            self.status_code = status_code
            self._json_data = json_data or {}
            self.text = text
        
        def json(self):
            return self._json_data
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise httpx.HTTPStatusError("Error", request=None, response=self)
    
    return MockResponse


def test_jina_request_success(mock_env, mock_response):
    """Test successful API request"""
    mock_data = {"result": "success"}
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response(
            json_data=mock_data
        )
        result = jina_request("https://api.jina.ai/test", {"param": "value"})
        assert result == mock_data


def test_jina_request_missing_api_key():
    """Test error when API key is missing"""
    # Save the current API key environment variable if it exists
    original_env = os.environ.copy()
    if "JINA_API_KEY" in os.environ:
        del os.environ["JINA_API_KEY"]
    
    # Patch the API key in the module to be None
    with patch('llm_jina.api.JINA_API_KEY', None):
        with pytest.raises(APIError) as excinfo:
            jina_request("https://api.jina.ai/test", {})
        assert "JINA_API_KEY environment variable is not set" in str(excinfo.value)
    
    # Restore the environment
    os.environ.clear()
    os.environ.update(original_env)


def test_jina_request_http_error(mock_env):
    """Test handling of HTTP errors"""
    with patch('httpx.Client') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.json.return_value = {"error": "Resource not found"}
        
        mock_client.return_value.__enter__.return_value.post.side_effect = httpx.HTTPStatusError(
            "Error", request=None, response=mock_response
        )
        
        with pytest.raises(APIError) as excinfo:
            jina_request("https://api.jina.ai/test", {})
        assert "API endpoint not found" in str(excinfo.value)


def test_jina_request_timeout(mock_env):
    """Test handling of request timeouts"""
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")
        with pytest.raises(APIError) as excinfo:
            jina_request("https://api.jina.ai/test", {})
        assert "Request timed out" in str(excinfo.value)


def test_jina_embed(mock_env, mock_response):
    """Test embedding function"""
    mock_embed_response = {
        "data": [
            {
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
            }
        ]
    }
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response(
            json_data=mock_embed_response
        )
        result = jina_embed("Test text")
        assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
        
        # Verify the correct parameters were sent
        args, kwargs = mock_client.return_value.__enter__.return_value.post.call_args
        assert kwargs["json"]["model"] == "jina-embeddings-v3"
        assert kwargs["json"]["input"] == ["Test text"]


def test_jina_search(mock_env, mock_response):
    """Test search function"""
    mock_search_response = {
        "results": [
            {"title": "Test Result", "url": "https://example.com"}
        ]
    }
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response(
            json_data=mock_search_response
        )
        result = jina_search("test query", site="example.com")
        assert result == mock_search_response
        
        # Verify the correct parameters were sent
        args, kwargs = mock_client.return_value.__enter__.return_value.post.call_args
        assert kwargs["json"]["query"] == "test query"
        assert kwargs["json"]["site"] == "example.com"


def test_jina_read(mock_env, mock_response):
    """Test URL reader function"""
    mock_read_response = {
        "data": {
            "content": "Webpage content here",
            "links": {"Link 1": "https://example.com/page1"},
            "images": {"Image 1": "https://example.com/image1.jpg"}
        }
    }
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response(
            json_data=mock_read_response
        )
        result = jina_read("https://example.com", with_links=True, with_images=True)
        assert "Webpage content here" in result
        assert "Link 1: https://example.com/page1" in result
        assert "Image 1: https://example.com/image1.jpg" in result


def test_jina_ground(mock_env, mock_response):
    """Test fact-checking function"""
    mock_ground_response = {
        "factuality_score": 0.85,
        "reasoning": "The statement is mostly accurate"
    }
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response(
            json_data=mock_ground_response
        )
        result = jina_ground("Jina AI was founded in 2022")
        assert result == mock_ground_response


def test_jina_segment(mock_env, mock_response):
    """Test text segmentation function"""
    mock_segment_response = {
        "chunks": ["Chunk 1", "Chunk 2"],
        "token_count": 42
    }
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response(
            json_data=mock_segment_response
        )
        result = jina_segment("Test text to segment", return_chunks=True)
        assert result == mock_segment_response


def test_jina_classify_text(mock_env, mock_response):
    """Test text classification function"""
    mock_classify_response = {
        "classifications": [
            {"label": "positive", "score": 0.85}
        ]
    }
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response(
            json_data=mock_classify_response
        )
        result = jina_classify_text(["Test text"], ["positive", "negative"])
        assert result == mock_classify_response
        
        # Verify the correct parameters were sent
        args, kwargs = mock_client.return_value.__enter__.return_value.post.call_args
        assert kwargs["json"]["model"] == "jina-embeddings-v3"
        assert kwargs["json"]["input"] == ["Test text"]
        assert kwargs["json"]["labels"] == ["positive", "negative"]


def test_jina_classify_images(mock_env, mock_response):
    """Test image classification function"""
    mock_classify_response = {
        "classifications": [
            {"label": "cat", "score": 0.92}
        ]
    }
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response(
            json_data=mock_classify_response
        )
        result = jina_classify_images(["base64_image_data"], ["cat", "dog"])
        assert result == mock_classify_response
        
        # Verify the correct parameters were sent
        args, kwargs = mock_client.return_value.__enter__.return_value.post.call_args
        assert kwargs["json"]["model"] == "jina-clip-v2"
        assert len(kwargs["json"]["input"]) == 1
        assert "image" in kwargs["json"]["input"][0]
        assert kwargs["json"]["labels"] == ["cat", "dog"]


def test_rerank_documents(mock_env, mock_response):
    """Test document reranking function"""
    mock_rerank_response = {
        "documents": [
            {"index": 1, "score": 0.92},
            {"index": 0, "score": 0.75}
        ]
    }
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response(
            json_data=mock_rerank_response
        )
        result = rerank_documents("test query", ["Doc 1", "Doc 2"])
        assert result == mock_rerank_response
