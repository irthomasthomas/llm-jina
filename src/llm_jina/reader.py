"""
Jina AI Reader API implementation.
"""
from typing import Dict, Any, Optional
from .client import JinaClient

def read(url: str, return_format: str = "markdown", **kwargs) -> Dict[str, Any]:
    """Read and parse content from a URL using Jina AI Reader API."""
    client = JinaClient()
    headers = {"X-Return-Format": return_format}
    
    # Forward any other kwargs as headers, converting bools to "true"
    for key, value in kwargs.items():
        if value is not None:
            header_key = f"X-{key.replace('_', '-')}"
            if isinstance(value, bool):
                headers[header_key] = "true"
            else:
                headers[header_key] = str(value)
                
    response = client.post("https://r.jina.ai/", data={"url": url}, headers=headers)
    return response

