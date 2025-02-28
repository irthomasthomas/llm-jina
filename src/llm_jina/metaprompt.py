import httpx
import click
import os
import time

def fetch_metaprompt() -> str:
    """
    Fetches the metaprompt content from a remote URL.

    Returns:
        str: The metaprompt content, or None if the fetch fails.
    """
    url = "https://docs.jina.ai"
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text
    except (httpx.RequestError, httpx.TimeoutException) as e:
        click.echo(f"Error fetching metaprompt: {str(e)}")
        return None

def jina_metaprompt() -> str:
    """
    Retrieves the Jina metaprompt, either from a local cache or by fetching it remotely.

    Returns:
        str: The Jina metaprompt content.

    Raises:
        click.ClickException: If the metaprompt cannot be retrieved.
    """
    cache_file = "jina-metaprompt.md"
    one_day = 86400  # seconds in a day
    need_fetch = True
    if os.path.exists(cache_file):
        last_mod = os.path.getmtime(cache_file)
        if time.time() - last_mod < one_day:
            need_fetch = False
    if need_fetch:
        metaprompt_content = fetch_metaprompt()
        if metaprompt_content is not None:
            try:
                with open(cache_file, "w") as file:
                    file.write(metaprompt_content)
            except IOError as e:
                click.echo(f"Warning: Failed to update {cache_file}: {str(e)}")
            return metaprompt_content
        else:
            raise click.ClickException("Failed to fetch metaprompt from remote URL.")
    try:
        with open(cache_file, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise click.ClickException(f"{cache_file} not found")