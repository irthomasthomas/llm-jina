"""
Jina AI Reranker API implementation.
"""
from typing import Dict, Any, List, Optional
from .client import JinaClient

def rerank(
    query: str,
    documents: List[str],
    model: str = "jina-reranker-v2-base-multilingual",
    top_n: Optional[int] = None,
    return_documents: bool = True
) -> Dict[str, Any]:
    """Rerank documents based on their relevance to a query."""
    client = JinaClient()
    
    data = {
        "model": model,
        "query": query,
        "documents": documents,
        "return_documents": return_documents
    }
    
    if top_n is not None:
        data["top_n"] = top_n
    
    response = client.post("https://api.jina.ai/v1/rerank", data=data)
    return response

