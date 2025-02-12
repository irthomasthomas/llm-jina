import click
import llm
from .commands import register_jina_commands

@llm.hookimpl
def register_commands(cli):
    register_jina_commands(cli)
