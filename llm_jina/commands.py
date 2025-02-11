import click
import json
import base64  # new import for image encoding
import os  # added for file handling
from typing import List
from .api import (
    jina_search,
    jina_read,
    jina_ground,
    jina_embed,
    rerank_documents,
    segment_text,
    jina_classify,
    jina_metaprompt
)
from .utils import logs_db_path
import sqlite_utils

def register_jina_commands(cli):
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
    @click.argument("task")
    @click.option("-m", "--model", default="claude-3.5-sonnet", help="Reranking model to use")
    def generate_code(task: str, model: str):
        """Generate Jina API code based on the given prompt"""
        try:
            # Read codegen prompt from file and substitute metaprompt
            metaprompt_content = jina_metaprompt()
            prompt_file = os.path.join(os.path.dirname(__file__), "codegen_prompt.txt")
            with open(prompt_file, 'r') as f:
                prompt_template = f.read()
            codegen_prompt = prompt_template.format(metaprompt=metaprompt_content, task=task)
            db = sqlite_utils.Database(logs_db_path())
            response = llm.get_model(model).prompt(codegen_prompt)
            response.log_to_db(db)
            result = response.text()
            click.echo("\n=== Generated Response ===")
            implementation_plan = ""
            if "<implementation_plan>" in result and "</implementation_plan>" in result:
                start = result.find("<implementation_plan>") + len("<implementation_plan>")
                end = result.find("</implementation_plan>")
                implementation_plan = result[start:end].strip()
                click.echo("\n=== Implementation Plan ===")
                click.echo(implementation_plan)

            # Parse Python code blocks and save to file
            python_code = ""
            filename = "jina_api_implementation.py"  # default filename
            if "<python_file" in result and "</python_file>" in result:
                start_tag = result.find("<python_file")
                end_tag = result.find("</python_file>") + len("</python_file>")
                python_block = result[start_tag:end_tag]
                
                # Extract filename
                filename_start = python_block.find('filename="') + len('filename="')
                filename_end = python_block.find('"', filename_start)
                filename = python_block[filename_start:filename_end]
                
                # Extract code
                code_start = python_block.find(">") + 1
                code_end = python_block.find("</python_file>")
                python_code = python_block[code_start:code_end].strip()
                
                # Handle markdown code blocks
                if "```python" in python_code:
                    code_start = python_code.find("```python") + len("```python")
                    code_end = python_code.rfind("```")
                    python_code = python_code[code_start:code_end].strip()
                
                # Save code to file
                try:
                    with open(filename, 'w') as f:
                        f.write(python_code)
                    click.echo(f"\nCode saved successfully to: {filename}")
                except IOError as e:
                    click.echo(f"\nError saving code to file: {str(e)}", err=True)
                
                click.echo("\n=== Generated Python Code ===")
                click.echo(f"Filename: {filename}")
                click.echo("\nCode:")
                click.echo(python_code)
            
            if not python_code:
                click.echo("\n=== Raw Generated Response ===")
                click.echo(result)
                
            click.echo("\nNote: Make sure to set your JINA_API_KEY environment variable before running the code.")
            click.echo("Get your Jina AI API key for free: https://jina.ai/?sui=apikey")
            
        except Exception as e:
            raise click.ClickException(f"Error generating code: {str(e)}")

    @jina.command()
    def metaprompt():
        """Display the Jina metaprompt"""
        click.echo(jina_metaprompt())

    @jina.command()
    @click.argument("input_text", nargs=-1, required=True)
    @click.option("--labels", required=True, help="Comma-separated list of labels for classification")
    @click.option("--model", default="jina-embeddings-v3", help="Model to use for classification (jina-embeddings-v3 for text, jina-clip-v2 for images)")
    @click.option("--image", is_flag=True, help="Treat input as image file paths")
    def classify(input_text: List[str], labels: str, model: str, image: bool) -> None:
        """Classify text or images using Jina AI Classifier API"""
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
