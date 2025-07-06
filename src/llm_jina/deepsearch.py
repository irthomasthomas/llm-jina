"""
Jina AI DeepSearch API implementation.
"""
from typing import Dict, Any, List, Optional
from .client import JinaClient

def deepsearch(
    query: str,
    history: Optional[List[Dict[str, str]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Perform a comprehensive investigation using Jina AI DeepSearch API."""
    client = JinaClient()
    
    messages = list(history) if history else []
    messages.append({"role": "user", "content": query})
    
    data = {
        "messages": messages,
        "stream": False,  # Use blocking mode for simplicity
    }
    data.update(kwargs) # Add any other API params
    
    response = client.post("https://deepsearch.jina.ai/v1/chat/completions", data=data)
    return response

