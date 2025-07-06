"""
Command-line interface for llm-jina.
"""
import click
import json
from pathlib import Path
from . import reader, search, rerank, classifier, segmenter, deepsearch
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
def rerank_docs(query, documents, model, top_n):
    """Rerank documents by relevance."""
    result = rerank.rerank(query=query, documents=list(documents), model=model, top_n=top_n)
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
    result = deepsearch.deepsearch(query=query)
    click.echo(json.dumps(result, indent=2))


if __name__ == '__main__':
    cli()
