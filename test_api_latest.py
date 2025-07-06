#!/usr/bin/env python3
"""
Updated test script for Jina AI API endpoints
Based on latest documentation and API structure
"""

import os
import json
import httpx
import argparse
import logging
from urllib.parse import quote_plus
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def test_jina_request(endpoint: str, data: Dict[str, Any] = None, method: str = "POST", timeout: int = 60):
    """
    Test a request to a Jina AI API endpoint with detailed logging
    
    Args:
        endpoint: The API endpoint URL
        data: The request payload (for POST requests)
        method: HTTP method to use (GET or POST)
        timeout: Request timeout in seconds
    """
    api_key = os.environ.get("JINA_API_KEY")
    if not api_key:
        logger.error("JINA_API_KEY environment variable is not set")
        return
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "llm-jina-test/0.2.0"
    }
    
    if method == "POST" and data is not None:
        headers["Content-Type"] = "application/json"
        logger.info(f"Request payload: {json.dumps(data, indent=2)}")
    
    logger.info(f"Testing endpoint: {endpoint} with {method} method")
    
    try:
        with httpx.Client(timeout=timeout) as client:
            logger.info(f"Making request with {timeout}s timeout...")
            
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            else:  # POST
                response = client.post(endpoint, json=data, headers=headers)
            
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    # Try to parse as JSON but also keep the raw response
                    json_response = response.json()
                    logger.info(f"Response preview: {json.dumps(json_response, indent=2)[:1000]}...")
                    return json_response
                except json.JSONDecodeError:
                    logger.warning("Response is not valid JSON")
                    logger.info(f"Raw response preview: {response.text[:500]}...")
                    return response.text
            else:
                response.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error: {str(e)}")
    except httpx.TimeoutException as e:
        logger.error(f"Request timed out after {timeout}s")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

def test_embed():
    """Test the embeddings endpoint with updated model name"""
    logger.info("Testing embeddings API...")
    
    endpoint = "https://api.jina.ai/v1/embeddings"
    data = {
        "model": "jina-embeddings-v3",
        "input": ["This is a test of the embedding functionality"]
    }
    
    return test_jina_request(endpoint, data, timeout=45)

def test_search(query: str = "what is Jina AI"):
    """Test the search API with updated endpoint format"""
    logger.info("Testing search API...")
    
    # New format is https://s.jina.ai/QUERY
    encoded_query = quote_plus(query)
    endpoint = f"https://s.jina.ai/{encoded_query}"
    
    # Search uses GET method now
    return test_jina_request(endpoint, method="GET", timeout=120)

def test_reader(url: str = "https://jina.ai/blog"):
    """Test the reader endpoint with updated format"""
    logger.info("Testing reader API...")
    
    # New format is https://r.jina.ai/URL
    encoded_url = quote_plus(url)
    endpoint = f"https://r.jina.ai/{encoded_url}"
    
    # Reader uses GET method
    return test_jina_request(endpoint, method="GET", timeout=60)

def main():
    parser = argparse.ArgumentParser(description='Test Jina AI API endpoints')
    parser.add_argument('endpoint', choices=['embed', 'search', 'reader', 'all'], 
                        help='Which endpoint to test')
    parser.add_argument('--query', type=str, default="what is Jina AI",
                        help='Query string for search (default: "what is Jina AI")')
    parser.add_argument('--url', type=str, default="https://jina.ai/blog",
                        help='URL for reader (default: "https://jina.ai/blog")')
    args = parser.parse_args()
    
    if args.endpoint == 'embed' or args.endpoint == 'all':
        test_embed()
    
    if args.endpoint == 'search' or args.endpoint == 'all':
        test_search(args.query)
        
    if args.endpoint == 'reader' or args.endpoint == 'all':
        test_reader(args.url)
        
if __name__ == "__main__":
    main()
