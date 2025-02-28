import httpx
import os
import json
import logging
import sys
from typing import List, Dict, Any, Union, Optional
import base64
from urllib.parse import quote_plus
import requests

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
               normalized: bool = True) -> List[float]:
    """
    Generate embeddings for text using Jina AI Embeddings API.
    Updated to match the current API specification.
    
    Args:
        text: The text to embed (string or list of strings)
        model: The model to use for embeddings (jina-embeddings-v3 or jina-clip-v2)
        normalized: Whether to return normalized embeddings
        
    Returns:
        List of floating point values representing the embedding
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
        
        # Parse the response according to API spec
        if "data" in response and len(response["data"]) > 0:
            if "embedding" in response["data"][0]:
                return response["data"][0]["embedding"]
        
        # If we can't find the embedding in the expected format
        logger.error(f"Unexpected response format: {response}")
        raise APIError("Unexpected response format from embeddings API")
    except APIError as e:
        # Add more context to the error
        if "not found" in str(e).lower() and model != "jina-embeddings-v3":
            # Suggest using the newer model if the specified one wasn't found
            raise APIError(f"Model '{model}' not found. Try using 'jina-embeddings-v3' instead.")
        raise

def jina_search(query: str, site: Optional[str] = None, 
               with_links: bool = False, with_images: bool = False) -> Dict[str, Any]:
    """
    Search the web using Jina AI Search API.
    Updated to match the current API specification.
    
    Args:
        query: The search query
        site: Optional site restriction
        with_links: Whether to include links in results
        with_images: Whether to include images in results
        
    Returns:
        The search results
    """
    url = "https://api.jina.ai/v1/search"
    
    # Build request according to the specification
    data = {"query": query}
    
    if site:
        data["site"] = site
    if with_links:
        data["with_links"] = with_links
    if with_images:
        data["with_images"] = with_images
    
    # Add headers for site restriction and summaries if needed
    custom_headers = {}
    if site:
        custom_headers["X-Site"] = site
    if with_links:
        custom_headers["X-With-Links-Summary"] = "true"
    if with_images:
        custom_headers["X-With-Images-Summary"] = "true"
        
    # Search can be slow, use a longer timeout
    try:
        return jina_request(url, data, method="POST", timeout=90, headers=custom_headers)
    except APIError as e:
        if "not found" in str(e).lower():
            # Try the alternative search endpoint from metaprompt
            logger.debug("Trying alternative search endpoint at s.jina.ai")
            alt_url = "https://s.jina.ai/"
            alt_data = {"q": query, "options": "Default"}
            try:
                return jina_request(alt_url, alt_data, method="POST", timeout=90, headers=custom_headers)
            except:
                raise e
        raise

def jina_read(url_to_read: str, with_links: bool = False, 
              with_images: bool = False, engine: Optional[str] = None,
              timeout: Optional[int] = None, target_selector: Optional[str] = None,
              wait_for_selector: Optional[str] = None, remove_selector: Optional[str] = None,
              with_generated_alt: bool = False, no_cache: bool = False,
              with_iframe: bool = False, return_format: Optional[str] = None,
              token_budget: Optional[int] = None, retain_images: Optional[str] = None) -> str:
    """
    Extract content from a URL using Jina AI Reader API.
    
    Args:
        url_to_read: The URL to read
        with_links: Whether to include links in the result
        with_images: Whether to include images in the result
        engine: Specify the engine to retrieve/parse content ('readerlm-v2' or 'direct')
        timeout: Maximum time in seconds to wait for webpage to load
        target_selector: CSS selectors to focus on specific elements
        wait_for_selector: CSS selectors to wait for before returning
        remove_selector: CSS selectors to exclude from the response
        with_generated_alt: Whether to add alt text to images lacking captions
        no_cache: Whether to bypass cache for fresh retrieval
        with_iframe: Whether to include iframe content
        return_format: Format of the response ('markdown', 'html', 'text', 'screenshot', 'pageshot')
        token_budget: Maximum number of tokens to use for the request
        retain_images: Use 'none' to remove all images from response
        
    Returns:
        The extracted content
    """
    # According to docs, Reader API uses POST to https://r.jina.ai/
    base_url = "https://r.jina.ai/"
    
    # Prepare request body
    request_data = {"url": url_to_read}
    
    # Add optional format parameter
    if return_format:
        if return_format.lower() in ['markdown', 'html', 'text', 'screenshot', 'pageshot']:
            request_data["options"] = return_format.capitalize()
    
    # Add optional headers
    custom_headers = {}
    if with_links:
        custom_headers["X-With-Links-Summary"] = "true"
    if with_images:
        custom_headers["X-With-Images-Summary"] = "true"
    if engine:
        custom_headers["X-Engine"] = engine
    if timeout:
        custom_headers["X-Timeout"] = str(timeout)
    if target_selector:
        custom_headers["X-Target-Selector"] = target_selector
    if wait_for_selector:
        custom_headers["X-Wait-For-Selector"] = wait_for_selector
    if remove_selector:
        custom_headers["X-Remove-Selector"] = remove_selector
    if with_generated_alt:
        custom_headers["X-With-Generated-Alt"] = "true"
    if no_cache:
        custom_headers["X-No-Cache"] = "true"
    if with_iframe:
        custom_headers["X-With-Iframe"] = "true"
    if token_budget:
        custom_headers["X-Token-Budget"] = str(token_budget)
    if retain_images:
        custom_headers["X-Retain-Images"] = retain_images
    
    try:
        logger.debug(f"Making POST request to Reader API for URL: {url_to_read}")
        response = jina_request(base_url, request_data, method="POST", timeout=90, headers=custom_headers)
        
        # Parse the response according to API spec
        if "data" in response:
            if "content" in response["data"]:
                content_result = response["data"]["content"]
                
                # Add information about links and images if available
                if with_links and "links" in response["data"]:
                    content_result += "\n\n--- Links ---\n"
                    for label, url in response["data"]["links"].items():
                        content_result += f"{label}: {url}\n"
                
                if with_images and "images" in response["data"]:
                    content_result += "\n\n--- Images ---\n"
                    for label, url in response["data"]["images"].items():
                        content_result += f"{label}: {url}\n"
                
                return content_result
            
            # Return the full data object if content isn't available
            return response["data"]
        
        return response
    except APIError as e:
        # Add more context to the error
        if "ERR_BLOCKED_BY_CLIENT" in str(e):
            raise APIError(f"Access to the URL was blocked. This could be due to ad blockers or network restrictions: {url_to_read}")
        elif "422" in str(e):
            raise APIError(f"Invalid URL or parameters for Reader API: {str(e)}")
        raise APIError(f"Failed to read URL {url_to_read}: {str(e)}")

def jina_rerank(query: str, documents: List[str], 
               model: str = "jina-reranker-v2-base-multilingual", 
               top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Rerank documents based on relevance to a query.
    Updated to match the current API specification.
    
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
        response = jina_request(url, data, method="POST", timeout=45)
        
        # Parse and return results according to the API spec
        return response
    except Exception as e:
        raise APIError(f"Reranking failed: {str(e)}")

def jina_classify_text(texts: List[str], labels: List[str], 
                      model: str = "jina-embeddings-v3") -> List[Dict[str, Any]]:
    """
    Classify text into provided labels.
    Updated to match the current API specification.
    
    Args:
        texts: List of text snippets to classify
        labels: List of possible labels
        model: Model to use for classification (use jina-embeddings-v3 for text)
        
    Returns:
        Classification results with prediction scores
    """
    url = "https://api.jina.ai/v1/classify"
    
    # Build request according to the specification
    data = {
        "model": model,
        "input": texts,
        "labels": labels
    }
    
    try:
        response = jina_request(url, data, method="POST", timeout=45)
        return response
    except Exception as e:
        raise APIError(f"Classification failed: {str(e)}")

def jina_classify_images(images: List[str], labels: List[str]) -> List[Dict[str, Any]]:
    """
    Classify images into provided labels.
    Updated to match the current API specification.
    
    Args:
        images: List of base64-encoded images
        labels: List of possible labels
        
    Returns:
        Classification results with prediction scores
    """
    url = "https://api.jina.ai/v1/classify"
    
    # Format input as required by the API (list of image objects)
    input_data = [{"image": img} for img in images]
    
    # Build request according to the specification
    data = {
        "model": "jina-clip-v2",  # Must use clip model for images
        "input": input_data,
        "labels": labels
    }
    
    try:
        response = jina_request(url, data, method="POST", timeout=60)
        return response
    except Exception as e:
        raise APIError(f"Image classification failed: {str(e)}")

def jina_segment(text: str, tokenizer: str = "cl100k_base",
                return_tokens: bool = False, return_chunks: bool = False,
                max_chunk_length: int = 1000) -> Dict[str, Any]:
    """
    Split text into segments.
    Updated to match the current API specification.
    
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
        response = jina_request(url, data, method="POST", timeout=30)
        return response
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

def rerank_documents(query: str, documents: List[str], model: str = "jina-reranker-v2-base-multilingual") -> Dict[str, Any]:
    """
    Reranks documents based on their relevance to a query using Jina AI Reranker.
    
    Args:
        query: The query to rank documents against
        documents: List of document texts to be ranked
        model: Name of the reranking model to use
        
    Returns:
        Dictionary containing ranked documents with scores
        
    Raises:
        APIError: If the API call fails
    """
    try:
        logger.debug(f"Reranking {len(documents)} documents for query: '{query}'")
        # Use the existing jina_rerank function that handles API requests properly
        return jina_rerank(query, documents, model)
    except Exception as e:
        logger.error(f"Reranking failed: {str(e)}")
        raise APIError(f"An error occurred during reranking: {str(e)}")

def jina_metaprompt_api(prompt: str, api_key: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Submit a prompt to Jina AI's metaprompt API.
    
    Args:
        prompt: The prompt to send to the API
        api_key: Optional API key (will fall back to environment variable)
        **kwargs: Additional parameters to pass to the API
        
    Returns:
        The response from the metaprompt API
        
    Raises:
        APIError: If the API request fails
    """
    api_key = api_key or os.environ.get("JINA_API_KEY")
    if not api_key:
        raise APIError("JINA_API_KEY environment variable or api_key parameter required")
    
    try:
        response = requests.post(
            "https://api.jina.ai/metaprompt",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"prompt": prompt, **kwargs}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise APIError(f"Error calling Jina AI metaprompt API: {str(e)}")

def jina_metaprompt(prompt: str = None, api_key: Optional[str] = None, **kwargs) -> str:
    """
    Get a metaprompt from Jina AI or enhance a provided prompt.
    
    Args:
        prompt: Optional prompt to enhance (if None, returns the standard metaprompt)
        api_key: Optional API key (will fall back to environment variable)
        **kwargs: Additional parameters to pass to the API
        
    Returns:
        The metaprompt or enhanced prompt as a string
        
    Raises:
        APIError: If the API request fails
    """
    try:
        # If no prompt is provided, return the standard metaprompt
        if prompt is None:
            # This can be replaced with an actual API call if there's a specific
            # endpoint for retrieving the standard metaprompt
            return """You are an AI programming assistant.
When asked for your name, you must respond with "GitHub Copilot".
Follow the user's requirements carefully & to the letter.
First think step-by-step, gathering all requirements.
Then write the requested code.
Ensure the code is bug-free and follows best practices.
When providing explanations, be concise and clear."""
        
        # If a prompt is provided, enhance it using the metaprompt API
        response = jina_metaprompt_api(prompt, api_key, **kwargs)
        if "enhanced_prompt" in response:
            return response["enhanced_prompt"]
        elif "metaprompt" in response:
            return response["metaprompt"]
        else:
            logger.warning("Unexpected response format from metaprompt API")
            return response.get("result", str(response))
            
    except Exception as e:
        logger.error(f"Error in metaprompt: {str(e)}")
        # Fallback to returning the original prompt if enhancement fails
        if prompt:
            return prompt
        raise APIError(f"Failed to retrieve metaprompt: {str(e)}")
