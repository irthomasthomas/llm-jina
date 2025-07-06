"""
<<<<<<< HEAD
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
=======
llm-jina: LLM plugin for Jina AI
"""

__version__ = "0.3.0"

import click
import llm
from .commands import register_jina_commands
from .api import (
    jina_embed, 
    jina_search, 
    jina_read,
    jina_rerank,
    jina_classify_text,
    jina_classify_images,
    jina_segment,
    jina_ground,
    jina_metaprompt,
    APIError
)

__all__ = [
    'register_jina_commands',
    'jina_embed',
    'jina_search',
    'jina_read',
    'jina_rerank',
    'jina_classify_text',
    'jina_classify_images',
    'jina_segment',
    'jina_ground',
    'jina_metaprompt',
    'APIError'
]

@llm.hookimpl
def register_commands(cli):
    register_jina_commands(cli)
>>>>>>> origin/main
