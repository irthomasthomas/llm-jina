import httpx
import os
import json
import logging
import sys
from typing import List, Dict, Any, Union, Optional
from urllib.parse import quote_plus
import base64

logger = logging.getLogger("llm_jina.api")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Constants
JINA_API_KEY = os.environ.get("JINA_API_KEY")  # Get your Jina AI API key for free: https://jina.ai/?sui=apikey
DEFAULT_TIMEOUT = 60

class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

def jina_request(url: str, data: Optional[Dict[str, Any]] = None, 
                method: str = "POST", timeout: int = DEFAULT_TIMEOUT,
                headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Make a request to the Jina AI API with proper error handling.
    
    Args:
        url: The API endpoint URL
        data: The request payload (for POST) or URL parameters (for GET)
        method: HTTP method (POST/GET)
        timeout: Request timeout in seconds
        headers: Additional headers to include
        
    Returns:
        The JSON response from the API
        
    Raises:
        APIError: With detailed information about the error
    """
    if not JINA_API_KEY:
        raise APIError("JINA_API_KEY environment variable is not set")

    default_headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Accept": "application/json"
    }
    
    # Add content-type for POST requests with JSON body
    if method.upper() == "POST" and data is not None:
        default_headers["Content-Type"] = "application/json"
    
    # Merge custom headers if provided
    if headers:
        default_headers.update(headers)

    try:
        logger.debug(f"Making {method} request to {url}")
        with httpx.Client(timeout=timeout) as client:
            if method.upper() == "POST":
                response = client.post(url, json=data, headers=default_headers)
            else:  # GET
                # For GET, we use URL parameters if data is provided
                if data:
                    response = client.get(url, params=data, headers=default_headers)
                else:
                    response = client.get(url, headers=default_headers)
                    
            logger.debug(f"Response status: {response.status_code}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}"
        try:
            error_body = e.response.json()
            error_msg += f": {error_body}"
        except:
            error_msg += f": {e.response.text}"
            
        if e.response.status_code == 404:
            raise APIError(f"API endpoint not found: {url}")
        elif e.response.status_code == 401:
            raise APIError("Authentication failed. Please check your JINA_API_KEY.")
        elif e.response.status_code == 422:
            raise APIError(f"Invalid parameters: {error_msg}")
        else:
            raise APIError(error_msg)
    except httpx.TimeoutException:
        raise APIError(f"Request timed out after {timeout}s. Try increasing the timeout.")
    except Exception as e:
        raise APIError(f"Unexpected error: {str(e)}")

def jina_embed(text: Union[str, List[str]], model: str = "jina-embeddings-v3", 
               normalized: bool = True) -> Dict[str, Any]:
    """
    Generate embeddings for text using Jina AI Embeddings API.
    Updated to match the current API specification.
    
    Args:
        text: The text to embed (string or list of strings)
        model: The model to use for embeddings (jina-embeddings-v3 or jina-clip-v2)
        normalized: Whether to return normalized embeddings
        
    Returns:
        Full API response including embeddings and metadata
    """
    url = "https://api.jina.ai/v1/embeddings"
    
    # API requires input as an array of strings
    input_text = [text] if isinstance(text, str) else text
    
    # Build the request with proper parameters
    data = {
        "model": model,
        "input": input_text,
        "normalized": normalized
    }
    
    logger.debug(f"Generating embeddings with model {model}")
    try:
        response = jina_request(url, data, method="POST", timeout=45)
        return response
    except APIError as e:
        # Add more context to the error
        if "not found" in str(e).lower() and model != "jina-embeddings-v3":
            # Suggest using the newer model if the specified one wasn't found
            raise APIError(f"Model '{model}' not found. Try using 'jina-embeddings-v3' instead.")
        raise

def jina_search(query: str, site: Optional[str] = None) -> Dict[str, Any]:
    """
    Search the web using Jina AI Search API.
    Updated to match the current API specification.
    
    Args:
        query: The search query
        site: Optional site restriction
        
    Returns:
        The search results
    """
    # New format is https://s.jina.ai/QUERY
    # If site is specified, add it to the query
    if site:
        query = f"site:{site} {query}"
    
    encoded_query = quote_plus(query)
    url = f"https://s.jina.ai/{encoded_query}"
    
    logger.debug(f"Searching for: {query}")
    
    # Search uses GET method now
    try:
        return jina_request(url, method="GET", timeout=90)
    except APIError as e:
        # If the direct query fails, we could try to fall back to the old method
        # But for now, just raise the error
        raise

def jina_read(url_to_read: str) -> Dict[str, Any]:
    """
    Extract content from a URL using Jina AI Reader API.
    Updated to match the current API specification.
    
    Args:
        url_to_read: The URL to read
        
    Returns:
        The extracted content
    """
    # New format is https://r.jina.ai/URL
    encoded_url = quote_plus(url_to_read)
    url = f"https://r.jina.ai/{encoded_url}"
    
    logger.debug(f"Reading content from: {url_to_read}")
    
    # Reader uses GET method
    try:
        return jina_request(url, method="GET", timeout=90)
    except APIError as e:
        # If the GET method fails, we could try to fall back to the old method
        # But for now, just raise the error
        raise

def jina_rerank(query: str, documents: List[str], 
               model: str = "jina-reranker-v2-base-multilingual", 
               top_n: Optional[int] = None) -> Dict[str, Any]:
    """
    Rerank documents based on relevance to a query.
    
    Args:
        query: The search query
        documents: List of text documents to rerank
        model: Model to use for reranking
        top_n: Number of top results to return (defaults to all)
        
    Returns:
        List of reranked documents with scores
    """
    url = "https://api.jina.ai/v1/rerank"
    
    # Build request according to the specification
    data = {
        "model": model,
        "query": query,
        "documents": documents
    }
    
    if top_n is not None:
        data["top_n"] = top_n
    
    try:
        return jina_request(url, data, method="POST", timeout=45)
    except Exception as e:
        raise APIError(f"Reranking failed: {str(e)}")

def jina_classify(input_data: Union[List[str], List[Dict[str, str]]], 
                 labels: List[str], 
                 model: str = "jina-embeddings-v3") -> Dict[str, Any]:
    """
    Classify text or images into provided labels.
    
    Args:
        input_data: List of texts or image objects to classify
        labels: List of possible labels
        model: Model to use for classification
        
    Returns:
        Classification results with prediction scores
    """
    url = "https://api.jina.ai/v1/classify"
    
    # Build request according to the specification
    data = {
        "model": model,
        "input": input_data,
        "labels": labels
    }
    
    try:
        return jina_request(url, data, method="POST", timeout=45)
    except Exception as e:
        raise APIError(f"Classification failed: {str(e)}")

def jina_segment(text: str, tokenizer: str = "cl100k_base",
                return_tokens: bool = False, return_chunks: bool = False,
                max_chunk_length: int = 1000) -> Dict[str, Any]:
    """
    Split text into segments.
    
    Args:
        text: The text to segment
        tokenizer: Tokenizer to use
        return_tokens: Whether to return tokens
        return_chunks: Whether to return chunks
        max_chunk_length: Maximum characters per chunk
        
    Returns:
        Segmentation results
    """
    url = "https://api.jina.ai/v1/segment"
    
    # Build request according to the specification
    data = {
        "content": text,
        "tokenizer": tokenizer,
        "return_tokens": return_tokens,
        "return_chunks": return_chunks,
        "max_chunk_length": max_chunk_length
    }
    
    try:
        return jina_request(url, data, method="POST", timeout=30)
    except Exception as e:
        raise APIError(f"Segmentation failed: {str(e)}")

def jina_ground(statement: str, sites: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Verify factual accuracy of a statement.
    
    Args:
        statement: The statement to verify
        sites: Optional list of sites to use as references
        
    Returns:
        Verification results
    """
    # This is now using g.jina.ai according to documentation
    encoded_statement = quote_plus(statement)
    url = f"https://g.jina.ai/{encoded_statement}"
    
    # Add sites if provided
    if sites:
        site_param = ",".join(sites)
        url += f"?sites={quote_plus(site_param)}"
    
    try:
        return jina_request(url, method="GET", timeout=60)
    except Exception as e:
        raise APIError(f"Fact-checking failed: {str(e)}")

# Compatibility aliases for backward compatibility
def rerank_documents(*args, **kwargs):
    return jina_rerank(*args, **kwargs)

def segment_text(*args, **kwargs):
    return jina_segment(*args, **kwargs)
