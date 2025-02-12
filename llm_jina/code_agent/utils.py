from pathlib import Path
import click

def read_prompt_template(prompt_file: Path) -> str:
    try:
        with prompt_file.open("r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise click.ClickException(f"Prompt template not found: {prompt_file}")
    except Exception as e:
        raise click.ClickException(f"Error reading prompt template: {e}")

def format_error(reason: str, exception: Exception) -> str:
    return f"{reason}: {str(exception)}"

def aggregate_failures(failures: list[dict]) -> str:
    return "\n".join([f"Test {f.get('test', 'unknown')}: {f.get('message', 'No message')}" for f in failures])
