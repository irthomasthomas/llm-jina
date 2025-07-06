"""
llm-jina: A Python library and LLM plugin for the Jina AI API.
"""
import llm
from .embeddings import register_embedding_models
from .commands import cli as jina_cli

@llm.hookimpl
def register_commands(cli):
    """Register the 'jina' subcommand."""
    cli.add_command(jina_cli, name="jina")

@llm.hookimpl
def register_embedding_models_hook(register):
    """Register the Jina embedding models."""
    register_embedding_models(register)
