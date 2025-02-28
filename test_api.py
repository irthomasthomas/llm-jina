#!/usr/bin/env python3
"""
Test script for Jina AI API endpoints
This script isolates API calls to help debug connectivity issues
"""

import os
import json
import httpx
import argparse
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def test_jina_request(endpoint: str, data: Dict[str, Any], timeout: int = 60):
    """
    Test a request to a Jina AI API endpoint with detailed logging
    
    Args:
        endpoint: The API endpoint URL
        data: The request payload
        timeout: Request timeout in seconds
    """
    api_key = os.environ.get("JINA_API_KEY")
    if not api_key:
        logger.error("JINA_API_KEY environment variable is not set")
        return
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "llm-jina-test/0.1.0"
    }
    
    logger.info(f"Testing endpoint: {endpoint}")
    logger.info(f"Request payload: {json.dumps(data, indent=2)}")
    
    try:
        with httpx.Client(timeout=timeout) as client:
            logger.info(f"Making request with {timeout}s timeout...")
            response = client.post(endpoint, json=data, headers=headers)
            
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    # Try to parse as JSON but also keep the raw response
                    json_response = response.json()
                    logger.info(f"Response: {json.dumps(json_response, indent=2)}")
                    return json_response
                except json.JSONDecodeError:
                    logger.warning("Response is not valid JSON")
                    logger.info(f"Raw response: {response.text[:500]}...")
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
    """Test the embeddings endpoint"""
    logger.info("Testing embeddings API...")
    
    # Original endpoint
    endpoint = "https://api.jina.ai/v1/embeddings"
    data = {
        "model": "jina-embedding-v2",
        "input": ["This is a test of the embedding functionality"]
    }
    
    result = test_jina_request(endpoint, data, timeout=45)
    
    # If original fails, try alternative endpoint
    if not result:
        logger.info("Trying alternative embedding endpoint...")
        alt_endpoint = "https://api.jina.ai/v1/embed"
        result = test_jina_request(alt_endpoint, data, timeout=45)
    
    return result

def test_search():
    """Test the search endpoint with increased timeout"""
    logger.info("Testing search API...")
    
    endpoint = "https://api.jina.ai/v1/search"
    data = {
        "query": "what is Jina AI",
        "site": "jina.ai",
        "with_links": True,
        "with_images": False
    }
    
    # Try with a longer timeout for search
    return test_jina_request(endpoint, data, timeout=120)

def test_reader():
    """Test the reader endpoint"""
    logger.info("Testing reader API...")
    
    url_to_read = "https://jina.ai/blog"
    endpoint = f"https://r.jina.ai/reader?url={url_to_read}"
    
    # Reader might use GET instead of POST
    api_key = os.environ.get("JINA_API_KEY")
    if not api_key:
        logger.error("JINA_API_KEY environment variable is not set")
        return
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "llm-jina-test/0.1.0"
    }
    
    try:
        with httpx.Client(timeout=60) as client:
            logger.info(f"Making GET request to {endpoint}...")
            response = client.get(endpoint, headers=headers)
            
            logger.info(f"Status code: {response.status_code}")
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    logger.info(f"Response: {json.dumps(json_response, indent=2)}")
                    return json_response
                except json.JSONDecodeError:
                    logger.warning("Response is not valid JSON")
                    logger.info(f"Raw response: {response.text[:500]}...")
            else:
                response.raise_for_status()
    except Exception as e:
        logger.error(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Test Jina AI API endpoints')
    parser.add_argument('endpoint', choices=['embed', 'search', 'reader', 'all'], 
                        help='Which endpoint to test')
    args = parser.parse_args()
    
    if args.endpoint == 'embed' or args.endpoint == 'all':
        test_embed()
    
    if args.endpoint == 'search' or args.endpoint == 'all':
        test_search()
        
    if args.endpoint == 'reader' or args.endpoint == 'all':
        test_reader()
        
if __name__ == "__main__":
    main()
