import click
import json
import llm
import os
from typing import List, Dict, Any, Union
import httpx
import base64

# Get your Jina AI API key for free: https://jina.ai/?sui=apikey
JINA_API_KEY = os.environ.get("JINA_API_KEY")

@llm.hookimpl
def register_commands(cli):
    @cli.group()
    def jina():
        """Commands for interacting with Jina AI Search Foundation APIs"""
        pass

    @jina.command()
    @click.argument("query", type=str)
    @click.option("--site", help="Limit search to a specific domain")
    @click.option("--with-links", is_flag=True, help="Include links summary")
    @click.option("--with-images", is_flag=True, help="Include images summary")
    def search(query: str, site: str, with_links: bool, with_images: bool):
        """Search the web using Jina AI Search API"""
        results = jina_search(query, site, with_links, with_images)
        click.echo(json.dumps(results, indent=2))
        
    @jina.command()
    @click.option("--content", required=True, help="The text content to segment")
    @click.option("--tokenizer", default="cl100k_base", help="Tokenizer to use")
    @click.option("--return-tokens", is_flag=True, help="Return tokens in the response")
    @click.option("--return-chunks", is_flag=True, help="Return chunks in the response")
    @click.option("--max-chunk-length", type=int, default=1000, help="Maximum characters per chunk")
    def segment(content, tokenizer, return_tokens, return_chunks, max_chunk_length):
        """Segment text into tokens or chunks"""
        try:
            result = segment_text(content, tokenizer, return_tokens, return_chunks, max_chunk_length)
            click.echo(json.dumps(result, indent=2))
        except click.ClickException as e:
            click.echo(str(e), err=True)
        except Exception as e:
            click.echo(f"An unexpected error occurred: {str(e)}", err=True)

    @jina.command()
    @click.argument("url", type=str)
    @click.option("--with-links", is_flag=True, help="Include links summary")
    @click.option("--with-images", is_flag=True, help="Include images summary")
    def read(url: str, with_links: bool, with_images: bool):
        """Read and parse content from a URL using Jina AI Reader API"""
        content = jina_read(url, with_links, with_images)
        click.echo(json.dumps(content, indent=2))

    @jina.command()
    @click.argument("statement", type=str)
    @click.option("--sites", help="Comma-separated list of URLs to use as grounding references")
    def ground(statement: str, sites: str):
        """Verify the factual accuracy of a statement using Jina AI Grounding API"""
        result = jina_ground(statement, sites.split(",") if sites else None)
        click.echo(json.dumps(result, indent=2))

    @jina.command()
    @click.argument("text", type=str)
    @click.option("--model", type=str, default="jina-embeddings-v3", help="Model to use for embedding")
    def embed(text: str, model: str):
        """Generate embeddings for text using Jina AI Embeddings API"""
        embedding = jina_embed(text, model)
        click.echo(json.dumps(embedding, indent=2))
        
    @jina.command()
    @click.argument("query", type=str)
    @click.argument("documents", nargs=-1, required=True)
    @click.option("--model", default="jina-reranker-v2-base-multilingual", help="Reranking model to use")
    def rerank(query: str, documents: List[str], model: str):
        """Rerank a list of documents based on their relevance to a query"""
        try:
            result = rerank_documents(query, list(documents), model)
            click.echo(json.dumps(result, indent=2))
        except click.ClickException as e:
            click.echo(str(e), err=True)
        except Exception as e:
            click.echo(f"An unexpected error occurred: {str(e)}", err=True)
    
    @jina.command()
    @click.argument("prompt")
    @click.option("--model", default="claude-3.5-sonnet", help="Reranking model to use")
    def generate_code(prompt: str, model: str):
        """Generate Jina API code based on the given prompt"""
        try:
            metaprompt = jina_metaprompt()
            full_prompt = f"""Based on the following Jina AI API documentation and guidelines, please generate production-ready Python code for the following task:

{metaprompt}

Task: {prompt}

Please provide the complete Python code implementation that follows the above guidelines and best practices. Include error handling, proper API response parsing, and any necessary setup instructions.

Remember to:
1. Use environment variable JINA_API_KEY for authentication
2. Include proper error handling
3. Follow the integration guidelines
4. Parse API responses correctly
5. Include any necessary imports
6. Add setup/usage instructions as comments

Provide the code in a format ready to be saved to a .py file and executed."""
            
            response = llm.get_model(model).prompt(full_prompt)
            result = response.text()
            
            click.echo("=== Generated Jina AI Code ===")
            click.echo(result)
            click.echo("Note: Make sure to set your JINA_API_KEY environment variable before running the code.")
            click.echo("Get your API key at: https://jina.ai/?sui=apikey")
            
        except Exception as e:
            raise click.ClickException(f"Error generating code: {str(e)}")

    @jina.command()
    def metaprompt():
        """Display the Jina metaprompt"""
        click.echo(jina_metaprompt())

    @jina.command()
    @click.argument("input_text", nargs=-1, required=True)
    @click.option("--labels", required=True, help="Comma-separated list of labels for classification")
    @click.option("--model", default="jina-embeddings-v3", help="Model to use for classification (jina-embeddings-v3 for text, jina-clip-v1 for images)")
    @click.option("--image", is_flag=True, help="Treat input as image file paths")
    def classify(input_text: List[str], labels: str, model: str, image: bool) -> None:
        """Classify text or images using Jina AI Classifier API"""
        labels_list = [label.strip() for label in labels.split(",")]
        input_data = []

        if image:
            model = "jina-clip-v1"
            for img_path in input_text:
                try:
                    with open(img_path, "rb") as img_file:
                        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
                        input_data.append({"image": img_base64})
                except IOError as e:
                    click.echo(f"Error reading image file {img_path}: {str(e)}", err=True)
                    return
        else:
            model = "jina-embeddings-v3"
            input_data = list(input_text)

        try:
            result = jina_classify(input_data, labels_list, model)
            click.echo(json.dumps(result, indent=2))
        except Exception as e:
            click.echo(f"Error occurred while classifying: {str(e)}", err=True)

def read_url(url: str, options: str = "Default") -> Dict[str, Any]:
    api_url = "https://r.jina.ai/"
    data = {
        "url": url,
        "options": options
    }
    headers = {
        "X-With-Links-Summary": "true",
        "X-With-Images-Summary": "true"
    }
    return jina_request(api_url, data, headers)


def fetch_metaprompt() -> str:
    url = "https://docs.jina.ai"
    try:
        with httpx.Client(timeout=3) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text
    except (httpx.RequestError, httpx.TimeoutException) as e:
        click.echo(f"Warning: Failed to fetch metaprompt from {url}: {str(e)}")
        return None

def jina_metaprompt() -> str:
    metaprompt_content = fetch_metaprompt()
    
    if metaprompt_content is None:
        try:
            with open("jina-metaprompt.md", "r") as file:
                return file.read()
        except FileNotFoundError:
            raise click.ClickException("jina-metaprompt.md file not found")
        except IOError as e:
            raise click.ClickException(f"Error reading jina-metaprompt.md: {str(e)}")
    else:
        try:
            with open("jina-metaprompt.md", "w") as file:
                file.write(metaprompt_content)
        except IOError as e:
            click.echo(f"Warning: Failed to update jina-metaprompt.md: {str(e)}")
        
        return metaprompt_content
    
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

def segment_text(content: str, tokenizer: str = "cl100k_base", return_tokens: bool = False, return_chunks: bool = True, max_chunk_length: int = 1000) -> Dict[str, Any]:
    """
    Segment text into tokens or chunks using the Jina AI Segmenter API.

    Args:
        content (str): The text content to segment.
        tokenizer (str): The tokenizer to use. Default is "cl100k_base".
        return_tokens (bool): Whether to return tokens in the response. Default is False.
        return_chunks (bool): Whether to return chunks in the response. Default is True.
        max_chunk_length (int): Maximum characters per chunk. Only effective if 'return_chunks' is True. Default is 1000.

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
    return jina_request(url, data)


def jina_request(url: str, data: Dict[str, Any], headers: Dict[str, str] = None) -> Dict[str, Any]:
    if not JINA_API_KEY:
        raise ValueError("JINA_API_KEY environment variable is not set")
    
    default_headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if headers:
        default_headers.update(headers)
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=data, headers=default_headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise click.ClickException(f"Error calling Jina AI API: {str(e)}")

def jina_search(query: str, site: str = None, with_links: bool = False, with_images: bool = False) -> Dict[str, Any]:
    url = "https://s.jina.ai/"
    headers = {}
    
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

    return jina_request(url, data, headers)

def jina_read(url: str, with_links: bool = False, with_images: bool = False) -> Dict[str, Any]:
    api_url = "https://r.jina.ai/"
    headers = {}
    
    if with_links:
        headers["X-With-Links-Summary"] = "true"
    if with_images:
        headers["X-With-Images-Summary"] = "true"

    data = {
        "url": url,
        "options": "Default"
    }

    return jina_request(api_url, data, headers)

def jina_ground(statement: str, sites: List[str] = None) -> Dict[str, Any]:
    url = "https://g.jina.ai/"
    headers = {}
    
    if sites:
        headers["X-Site"] = ",".join(sites)

    data = {
        "statement": statement
    }

    return jina_request(url, data, headers)

def jina_embed(text: str, model: str = "jina-embeddings-v3") -> Dict[str, Any]:
    url = "https://api.jina.ai/v1/embeddings"
    data = {
        "input": [text],
        "model": model
    }

    return jina_request(url, data)

def jina_classify(input_data: List[Union[str, Dict[str, str]]], labels: List[str], model: str) -> Dict[str, Any]:
    url = "https://api.jina.ai/v1/classify"
    data = {
        "model": model,
        "input": input_data,
        "labels": labels
    }

    try:
        return jina_request(url, data)
    except click.ClickException as e:
        raise click.ClickException(f"Error occurred while classifying: {str(e)}. Please check your input data and try again.")