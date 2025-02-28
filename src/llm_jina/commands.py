import json
import base64
import os
from pathlib import Path
import click
from typing import List
from .api import (
    jina_search,
    jina_read,
    jina_ground,
    jina_embed,
    rerank_documents,
    jina_segment,
    jina_classify_text,  # Changed from jina_classify
    jina_classify_images,  # Added this import
    jina_metaprompt_api,  # Use the correct function from API
)
from .metaprompt import jina_metaprompt  # Import from metaprompt module
from .utils import logs_db_path
from .code_agent.generator import CodeGenerator
from .code_agent.refiner import CodeRefiner
from .code_agent.validator import validate_code_safety, CodeValidationError
from .exceptions import APIError
import sqlite_utils
import llm  # Added for logging functionality
import logging

logger = logging.getLogger(__name__)

def register_jina_commands(cli):
    @cli.group()
    def jina():
        """Commands for interacting with Jina AI."""
        pass

    @jina.command()
    @click.argument("text")
    @click.option("--model", "-m", default="jina-embeddings-v3", help="Model to use for embeddings")
    @click.option("--normalize/--no-normalize", default=True, help="Whether to normalize embeddings")
    def embed(text, model, normalize):
        "Generate embeddings for text using Jina AI API"
        result = jina_embed(text, model=model, normalized=normalize)
        print(f"Generated embedding with {len(result)} dimensions")
        print(result[:5], "...", result[-5:])

    @jina.command()
    @click.argument("query")
    @click.option("--site", "-s", help="Optional site restriction")
    @click.option("--links/--no-links", default=False, help="Include links in results")
    @click.option("--images/--no-images", default=False, help="Include images in results")
    def search(query, site, links, images):
        "Search using Jina AI API"
        result = jina_search(query, site=site, with_links=links, with_images=images)
        print(json.dumps(result, indent=2))

    @jina.command()
    @click.argument("url")
    @click.option("--links/--no-links", default=False, help="Include links in result")
    @click.option("--images/--no-images", default=False, help="Include images in result")
    @click.option("--engine", help="Engine to retrieve/parse content ('readerlm-v2' or 'direct')")
    @click.option("--timeout", type=int, help="Maximum time in seconds to wait for webpage to load")
    @click.option("--target-selector", help="CSS selectors to focus on specific elements")
    @click.option("--wait-for-selector", help="CSS selectors to wait for before returning")
    @click.option("--remove-selector", help="CSS selectors to exclude from the response")
    @click.option("--with-generated-alt/--no-generated-alt", default=False, help="Add alt text to images lacking captions")
    @click.option("--no-cache/--use-cache", default=False, help="Bypass cache for fresh retrieval")
    @click.option("--with-iframe/--no-iframe", default=False, help="Include iframe content")
    @click.option("--format", "return_format", type=click.Choice(['markdown', 'html', 'text', 'screenshot', 'pageshot'], case_sensitive=False), 
                  help="Format of the response")
    @click.option("--token-budget", type=int, help="Maximum number of tokens to use for the request")
    @click.option("--retain-images", help="Use 'none' to remove all images from response")
    def read(url, links, images, engine, timeout, target_selector, wait_for_selector, 
             remove_selector, with_generated_alt, no_cache, with_iframe, return_format, 
             token_budget, retain_images):
        "Extract content from a URL using Jina AI Reader API"
        content = jina_read(
            url, with_links=links, with_images=images, engine=engine, timeout=timeout,
            target_selector=target_selector, wait_for_selector=wait_for_selector,
            remove_selector=remove_selector, with_generated_alt=with_generated_alt,
            no_cache=no_cache, with_iframe=with_iframe, return_format=return_format,
            token_budget=token_budget, retain_images=retain_images
        )
        print(content)

    @jina.command()
    @click.argument("content")
    @click.option("--tokenizer", default="cl100k_base", help="Tokenizer to use")
    @click.option("--return-tokens", is_flag=True, help="Return tokens in the response")
    @click.option("--return-chunks", is_flag=True, help="Return chunks in the response")
    @click.option("--max-chunk-length", type=int, default=1000, help="Maximum characters per chunk")
    def segment(content, tokenizer, return_tokens, return_chunks, max_chunk_length):
        try:
            result = jina_segment(content, tokenizer, return_tokens, return_chunks, max_chunk_length)
            click.echo(json.dumps(result, indent=2))
        except Exception as e:
            click.echo(f"Error: {str(e)}", err=True)

    @jina.command()
    @click.argument("statement", type=str)
    @click.option("--sites", help="Comma-separated list of URLs to use as grounding references")
    def ground(statement: str, sites: str):
        """Verify the factual accuracy of a statement using Jina AI Grounding API"""
        site_list = sites.split(",") if sites else None
        result = jina_ground(statement, site_list)
        click.echo(json.dumps(result, indent=2))

    @jina.command()
    @click.argument("query", type=str)
    @click.argument("documents", nargs=-1, required=True)
    @click.option("--model", default="jina-reranker-v2-base-multilingual", help="Reranking model to use")
    def rerank(query: str, documents: List[str], model: str):
        """Rerank a list of documents based on their relevance to a query"""
        try:
            result = rerank_documents(query, list(documents), model)
            click.echo(json.dumps(result, indent=2))
        except Exception as e:
            click.echo(f"An unexpected error occurred: {str(e)}", err=True)

    @jina.command()
    @click.argument("task")
    @click.option("-m", "--model", default="claude-3.5-sonnet", help="Model to use")
    @click.option("--max-retries", default=5, help="Max refinement retries")
    def generate_code(task: str, model: str, max_retries: int):
        try:
            # Fetch metaprompt content using the no-argument version
            # This fixes the parameter mismatch issue
            metaprompt_content = jina_metaprompt()
            
            # Load the prompt template
            prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "codegen_prompt.txt")
            if not os.path.exists(prompt_path):
                # Try alternative location
                prompt_path = os.path.join(os.path.dirname(__file__), "code_agent", "codegen_prompt.txt")
            
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()

            full_prompt = prompt_template.format(
                metaprompt=metaprompt_content,
                task=task
            )

            # Code generation workflow
            generator = CodeGenerator(task, model)
            initial_code = generator.generate_initial_code()
            validate_code_safety(initial_code)

            refiner = CodeRefiner(task, model, max_retries)
            result = refiner.refine_code(initial_code)

            # Validate result structure
            required_keys = ['success', 'final_code', 'iterations', 'coverage']
            missing_keys = [key for key in required_keys if key not in result]
            if missing_keys:
                raise APIError(f"Missing required keys in result: {', '.join(missing_keys)}")

            if result["success"]:
                click.secho(f"🎉 Code generated after {result['iterations']} iterations!", fg="green")
                click.echo(f"Test coverage: {result['coverage']}%")
                final_code_path = Path("final_code.py")
                final_code_path.write_text(result["final_code"], encoding="utf-8")
                click.echo(f"Code saved to: {final_code_path}")

                # Database logging
                db = sqlite_utils.Database(logs_db_path())
                response = llm.get_model(model).prompt(full_prompt)
                response.log_to_db(db)
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                click.secho(f"💔 Failed after {max_retries} tries", fg="red")
                click.echo(f"Error: {error_msg}")

        except (CodeValidationError, APIError) as e:
            click.secho(f"Validation error: {str(e)}", fg="red")
        except Exception as e:
            click.secho(f"Unexpected error: {str(e)}", fg="red")

    @jina.command()
    @click.argument("input_text", nargs=-1, required=True)
    @click.option("--labels", required=True, help="Comma-separated labels for classification")
    @click.option("--model", default="jina-embeddings-v3", help="Classification model")
    @click.option("--image", is_flag=True, help="Treat input as image file paths")
    def classify(input_text: List[str], labels: str, model: str, image: bool):
        """Classify text or images using Jina AI Classifier"""
        labels_list = [label.strip() for label in labels.split(",")]
        
        try:
            if image:
                # Handle image classification
                model = "jina-clip-v2"  # Force the CLIP model for images
                image_data = []
                
                for img_path in input_text:
                    try:
                        with open(img_path, "rb") as img_file:
                            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
                            image_data.append(img_base64)
                    except IOError as e:
                        click.echo(f"Error reading image {img_path}: {str(e)}", err=True)
                        return
                
                result = jina_classify_images(image_data, labels_list)
            else:
                # Handle text classification
                result = jina_classify_text(list(input_text), labels_list, model)
                
            click.echo(json.dumps(result, indent=2))
        except Exception as e:
            click.echo(f"Classification error: {str(e)}", err=True)

    @jina.command()
    def metaprompt():
        """Display the Jina metaprompt"""
        click.echo(jina_metaprompt())

    return jina
