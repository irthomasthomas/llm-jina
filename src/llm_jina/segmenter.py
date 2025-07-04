"""
Jina AI Segmenter API implementation.
"""
from typing import Dict, Any, Optional
from .client import JinaClient

def segment(content: str, **kwargs) -> Dict[str, Any]:
    """Segment text using Jina AI Segmenter API."""
    client = JinaClient()
    data = {"content": content}
    data.update(kwargs)
    
    response = client.post("https://segment.jina.ai/", data=data)
    return response

