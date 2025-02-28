__version__ = "0.1.0"

def register_commands(cli):
    from llm_jina.commands import register_jina_commands
    register_jina_commands(cli)
