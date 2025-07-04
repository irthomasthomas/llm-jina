"""
Jina AI Search API implementation.
"""
from typing import Dict, Any, Optional
from .client import JinaClient

def search(query: str, num_results: Optional[int] = None, **kwargs) -> Dict[str, Any]:
    """Search the web using Jina AI Search API."""
    client = JinaClient()
    headers = {}
    
    for key, value in kwargs.items():
        if value is not None:
            header_key = f"X-{key.replace('_', '-')}"
            if isinstance(value, bool):
                headers[header_key] = "true"
            else:
                headers[header_key] = str(value)

    data = {"q": query}
    if num_results:
        data["num"] = num_results
    
    response = client.post("https://s.jina.ai/", data=data, headers=headers)
    return response

