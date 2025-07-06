"""
Core HTTP client for Jina AI API interactions.
"""
import os
import requests
from typing import Dict, Any, Optional
from .exceptions import JinaAPIError

class JinaClient:
    """Central HTTP client for all Jina AI API endpoints."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise JinaAPIError("JINA_API_KEY environment variable is required.")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def post(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Makes a POST request to the Jina API."""
        try:
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)
                
            response = self.session.post(url, json=data, headers=request_headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise JinaAPIError(f"API request failed: {e}")
        except ValueError:
            raise JinaAPIError(f"Invalid JSON response from {url}: {response.text}")
