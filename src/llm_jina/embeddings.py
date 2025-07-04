"""
Jina AI Embeddings API implementation and LLM plugin integration.
"""
import llm
from typing import List
from .client import JinaClient

@llm.hookimpl
def register_embedding_models(register):
    """Register the Jina embedding models."""
    register(JinaEmbeddings("jina-embeddings-v2-base-en"), aliases=("jina-v2",))
    register(JinaEmbeddings("jina-embeddings-v3"), aliases=("jina-v3",))
    register(JinaEmbeddings("jina-embeddings-v4"), aliases=("jina-v4",))
    register(JinaEmbeddings("jina-clip-v1"), aliases=("jina-clip",))

class JinaEmbeddings(llm.EmbeddingModel):
    """Jina AI embedding model."""

    def __init__(self, model_id: str):
        self.model_id = model_id
        self._client = None

    @property
    def client(self) -> JinaClient:
        if self._client is None:
            self._client = JinaClient()
        return self._client

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts."""
        response = self.client.post(
            "https://api.jina.ai/v1/embeddings",
            data={"input": texts, "model": self.model_id}
        )
        if "data" not in response or not isinstance(response["data"], list):
            raise ValueError("Invalid response format from Jina API")
        
        embeddings = sorted(response["data"], key=lambda e: e["index"])
        return [result["embedding"] for result in embeddings]
