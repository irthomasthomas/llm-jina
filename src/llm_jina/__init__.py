"""
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
