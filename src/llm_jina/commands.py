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
    segment_text,
    jina_classify,
    jina_metaprompt,
)
from .utils import logs_db_path
from .code_agent.generator import CodeGenerator
from .code_agent.refiner import CodeRefiner
from .code_agent.validator import validate_code_safety, CodeValidationError
from .exceptions import APIError
import sqlite_utils
import llm  # Added for logging functionality

def register_jina_commands(cli):
    @cli.group()
    def jina():
        """Commands for interacting with Jina AI."""
        pass

    # Combined search command from both implementations
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
        try:
            result = segment_text(content, tokenizer, return_tokens, return_chunks, max_chunk_length)
            click.echo(json.dumps(result, indent=2))
        except Exception as e:
            click.echo(f"Error: {str(e)}", err=True)

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
        site_list = sites.split(",") if sites else None
        result = jina_ground(statement, site_list)
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
        except Exception as e:
            click.echo(f"An unexpected error occurred: {str(e)}", err=True)

    @jina.command()
    @click.argument("task")
    @click.option("-m", "--model", default="claude-3.5-sonnet", help="Model to use")
    @click.option("--max-retries", default=5, help="Max refinement retries")
    def generate_code(task: str, model: str, max_retries: int):
        try:
            # Prompt template handling
            metaprompt_content = jina_metaprompt()
            prompt_path = os.path.join("prompts", "codegen_prompt.txt")
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

            # Detailed output and logging
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
                click.secho(f"💔 Failed after {max_retries} tries", fg="red")
                click.echo(f"Error: {result['error']}")

        except (CodeValidationError, APIError) as e:
            click.secho(f"Validation error: {str(e)}", fg="red")
        except Exception as e:
            click.secho(f"Unexpected error: {str(e)}", fg="red")

    @jina.command()
    def metaprompt():
        """Display the Jina metaprompt"""
        click.echo(jina_metaprompt())

    @jina.command()
    @click.argument("input_text", nargs=-1, required=True)
    @click.option("--labels", required=True, help="Comma-separated labels for classification")
    @click.option("--model", default="jina-embeddings-v3", help="Classification model")
    @click.option("--image", is_flag=True, help="Treat input as image file paths")
    def classify(input_text: List[str], labels: str, model: str, image: bool):
        """Classify text or images using Jina AI Classifier"""
        labels_list = [label.strip() for label in labels.split(",")]
        input_data = []

        if image:
            model = "jina-clip-v2"
            for img_path in input_text:
                try:
                    with open(img_path, "rb") as img_file:
                        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
                        input_data.append({"image": img_base64})
                except IOError as e:
                    click.echo(f"Error reading image {img_path}: {str(e)}", err=True)
                    return
        else:
            input_data = list(input_text)

        try:
            result = jina_classify(input_data, labels_list, model)
            click.echo(json.dumps(result, indent=2))
        except Exception as e:
            click.echo(f"Classification error: {str(e)}", err=True)

    return jina
