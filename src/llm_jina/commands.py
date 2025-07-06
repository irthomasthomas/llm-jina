"""
Command-line interface for llm-jina.
"""
import click
import json
from pathlib import Path
from . import reader, search, classifier, segmenter, deepsearch as ds
from . import rerank as rerank_module
from .metaprompt import jina_metaprompt
from .exceptions import APIError, CodeValidationError

@click.group()
def cli():
    """Jina AI API command-line interface."""
    pass

@cli.command()
@click.argument('url')
@click.option('--format', 'return_format', default='markdown', help='Return format (markdown, html, text)')
def read(url, return_format):
    """Read content from a URL."""
    result = reader.read(url=url, return_format=return_format)
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.argument('query')
@click.option('--site', help='Limit search to specific site')
@click.option('--num', 'num_results', type=int, help='Number of results')
def websearch(query, site, num_results):
    """Search the web."""
    result = search.search(query=query, site=site, num_results=num_results)
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.argument('query')
@click.argument('documents', nargs=-1, required=True)
@click.option('--model', default='jina-reranker-v2-base-multilingual', help='Reranker model')
@click.option('--top-n', type=int, help='Number of top results')
def rerank(query, documents, model, top_n):
    """Rerank documents by relevance."""
    result = rerank_module.rerank(query=query, documents=list(documents), model=model, top_n=top_n)
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.argument('text')
@click.option('--return-chunks', is_flag=True, help='Return semantic chunks')
def segment(text, return_chunks):
    """Segment text into tokens or chunks."""
    result = segmenter.segment(content=text, return_chunks=return_chunks)
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.argument('query')
def deepsearch(query):
    """Perform comprehensive investigation."""
    result = ds.deepsearch(query=query)
    click.echo(json.dumps(result, indent=2))



@cli.command()
def metaprompt():
    """Get the Jina AI metaprompt."""
    try:
        result = jina_metaprompt()
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.ClickException(f"Failed to get metaprompt: {str(e)}")
if __name__ == '__main__':
    cli()

@cli.command()
@click.argument('input_text', nargs=-1, required=True)
@click.option('--labels', required=True, help='Comma-separated list of labels for classification')
@click.option('--model', help='Model to use for classification (auto-detected if not specified)')
@click.option('--image', is_flag=True, help='Treat input as image file paths')
def classify(input_text, labels, model, image):
    """Classify text or images using Jina AI Classifier API."""
    labels_list = [label.strip() for label in labels.split(',')]
    
    if image:
        import base64
        input_data = []
        for img_path in input_text:
            try:
                with open(img_path, 'rb') as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                    input_data.append({'image': img_base64})
            except IOError as e:
                click.echo(f'Error reading image file {img_path}: {str(e)}', err=True)
                return
    else:
        input_data = list(input_text)
    
    result = classifier.classify(inputs=input_data, labels=labels_list, model=model)
    click.echo(json.dumps(result, indent=2))
