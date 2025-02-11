import httpx
import os
import json
from typing import List, Dict, Any, Union
import click
from .exceptions import APIError
import time

JINA_API_KEY = os.environ.get("JINA_API_KEY")  # Get your Jina AI API key for free: https://jina.ai/?sui=apikey

def jina_request(url: str, data: Dict[str, Any], headers: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Make a request to the Jina AI API.

    Args:
        url (str): The API endpoint URL.
        data (Dict[str, Any]): The request payload.
        headers (Dict[str, str], optional): Custom headers. Defaults to None.

    Returns:
        Dict[str, Any]: The JSON response from the API.

    Raises:
        APIError: If the API key is not set or the API request fails.
    """
    if not JINA_API_KEY:
        raise APIError("JINA_API_KEY environment variable is not set")

    default_headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if headers:
        default_headers.update(headers)

    try:
        with httpx.Client(timeout=10) as client:  # Increased timeout to 10 seconds
            response = client.post(url, json=data, headers=default_headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise APIError(f"Error calling Jina AI API: {str(e)}")

def jina_search(query: str, site: str = None, with_links: bool = False, with_images: bool = False) -> Dict[str, Any]:
    """
    Search the web using the Jina AI Search API.

    Args:
        query (str): The search query.
        site (str, optional): Limit search to a specific domain. Defaults to None.
        with_links (bool, optional): Include links summary. Defaults to False.
        with_images (bool, optional): Include images summary. Defaults to False.

    Returns:
        Dict[str, Any]: The search results.
    """
    url = "https://s.jina.ai/"
    headers = {"X-No-Cache": "true"}  # force no-cache retrieval
    if site:
        headers["X-Site"] = site
    if with_links:
        headers["X-With-Links-Summary"] = "true"
    if with_images:
        headers["X-With-Images-Summary"] = "true"

    data = {
        "q": query,
        "options": "Default"
    }

    response = jina_request(url, data, headers)
    return response["data"]

def jina_read(url: str, with_links: bool = False, with_images: bool = False) -> Dict[str, Any]:
    """
    Read and parse content from a URL using the Jina AI Reader API.

    Args:
        url (str): The URL to read.
        with_links (bool, optional): Include links summary. Defaults to False.
        with_images (bool, optional): Include images summary. Defaults to False.

    Returns:
        Dict[str, Any]: The parsed content.
    """
    api_url = "https://r.jina.ai/"
    headers = {
        "X-No-Cache": "true",
        "X-Engine": "readerlm-v2",
        "X-Return-Format": "text"
    }
    if with_links:
        headers["X-With-Links-Summary"] = "true"
    if with_images:
        headers["X-With-Images-Summary"] = "true"

    data = {
        "url": url,
        "options": "Default"
    }

    response = jina_request(api_url, data, headers)
    return response["data"]

def jina_ground(statement: str, sites: List[str] = None) -> Dict[str, Any]:
    """
    Verify the factual accuracy of a statement using the Jina AI Grounding API.

    Args:
        statement (str): The statement to verify.
        sites (List[str], optional): A list of URLs to use as grounding references. Defaults to None.

    Returns:
        Dict[str, Any]: The grounding results.
    """
    url = "https://g.jina.ai/"
    headers = {"X-No-Cache": "true"}
    if sites:
        headers["X-Site"] = ",".join(sites)

    data = {
        "statement": statement
    }

    response = jina_request(url, data, headers)
    return response["data"]

def jina_embed(text: str, model: str = "jina-embeddings-v3") -> Dict[str, Any]:
    """
    Generate embeddings for text using the Jina AI Embeddings API.

    Args:
        text (str): The text to embed.
        model (str, optional): The model to use for embedding. Defaults to "jina-embeddings-v3".

    Returns:
        Dict[str, Any]: The embedding results.
    """
    url = "https://api.jina.ai/v1/embeddings"
    data = {
        "input": [text],
        "model": model
    }

    response = jina_request(url, data)
    return response["data"]

def rerank_documents(query: str, documents: List[str], model: str = "jina-reranker-v2-base-multilingual") -> List[Dict[str, Any]]:
    """
    Rerank a list of documents based on their relevance to a given query.

    Args:
        query (str): The query string to compare documents against.
        documents (List[str]): A list of document strings to be reranked.
        model (str, optional): The reranking model to use. Defaults to "jina-reranker-v2-base-multilingual".

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing reranked documents and their scores.
        Each dictionary includes 'text' (the document), 'index' (original position), and 'score' (relevance score).

    Raises:
        click.ClickException: If there's an error in the API call.
    """
    url = "https://api.jina.ai/v1/rerank"
    data = {
        "model": model,
        "query": query,
        "documents": documents
    }
    response = jina_request(url, data)
    return response["results"]

def segment_text(content: str, tokenizer: str = "cl100k_base", return_tokens: bool = False,
                 return_chunks: bool = True, max_chunk_length: int = 1000,
                 head: int = None, tail: int = None) -> Dict[str, Any]:
    """
    Segment text into tokens or chunks using the Jina AI Segmenter API.

    Args:
        content (str): The text content to segment.
        tokenizer (str): The tokenizer to use. Default is "cl100k_base".
        return_tokens (bool): Whether to return tokens in the response. Default is False.
        return_chunks (bool): Whether to return chunks in the response. Default is True.
        max_chunk_length (int): Maximum characters per chunk. Only effective if 'return_chunks' is True. Default is 1000.
        head (int, optional): Number of tokens to include at the beginning. Default is None.
        tail (int, optional): Number of tokens to include at the end. Default is None.

    Returns:
        Dict[str, Any]: The response from the Jina AI Segmenter API.

    Raises:
        click.ClickException: If there's an error in the API call or response.
    """
    url = "https://segment.jina.ai/"
    data = {
        "content": content,
        "tokenizer": tokenizer,
        "return_tokens": return_tokens,
        "return_chunks": return_chunks,
        "max_chunk_length": max_chunk_length
    }
    if head is not None:
        data["head"] = head
    if tail is not None:
        data["tail"] = tail
    return jina_request(url, data)

def jina_classify(input_data: List[Union[str, Dict[str, str]]], labels: List[str], model: str) -> Dict[str, Any]:
    """
    Classify text or images using the Jina AI Classifier API.

    Args:
        input_data (List[Union[str, Dict[str, str]]]): The input data to classify.
        labels (List[str]): A list of labels for classification.
        model (str): The model to use for classification.

    Returns:
        Dict[str, Any]: The classification results.

    Raises:
        APIError: If an error occurs during classification.
    """
    url = "https://api.jina.ai/v1/classify"
    data = {
        "model": model,
        "input": input_data,
        "labels": labels
    }

    result = jina_request(url, data)
    if "200" in result and "data" in result["200"]:
        return result["200"]["data"]
    else:
        return result

def jina_metaprompt() -> str:
    """
    Retrieves the Jina metaprompt, either from a local cache or by fetching it remotely.

    Returns:
        str: The Jina metaprompt content.

    Raises:
        click.ClickException: If the metaprompt cannot be retrieved.
    """
    cache_file = "jina-metaprompt.md"
    one_day = 86400  # seconds in a day
    need_fetch = True
    if os.path.exists(cache_file):
        last_mod = os.path.getmtime(cache_file)
        if time.time() - last_mod < one_day:
            need_fetch = False
    if need_fetch:
        metaprompt_content = fetch_metaprompt_from_url()
        if metaprompt_content is not None:
            try:
                with open(cache_file, "w") as file:
                    file.write(metaprompt_content)
            except IOError as e:
                click.echo(f"Warning: Failed to update {cache_file}: {str(e)}")
            return metaprompt_content
    try:
        with open(cache_file, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise click.ClickException(f"{cache_file} not found")

def fetch_metaprompt_from_url() -> str:
    """
    Fetches the metaprompt content from a remote URL.

    Returns:
        str: The metaprompt content, or None if the fetch fails.
    """
    url = "https://docs.jina.ai"
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text
    except (httpx.RequestError, httpx.TimeoutException) as e:
        click.echo(f"Warning: Failed to fetch metaprompt from {url}: {str(e)}")
        return None