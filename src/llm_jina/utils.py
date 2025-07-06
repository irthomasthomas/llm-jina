
import click
import os
import pathlib

def user_dir():
    """
    Returns the user's application directory for storing data.

    Returns:
        pathlib.Path: The path to the user's application directory.
    """
    llm_user_path = os.environ.get("LLM_USER_PATH")
    if llm_user_path:
        path = pathlib.Path(llm_user_path)
    else:
        path = pathlib.Path(click.get_app_dir("io.datasette.llm"))
    path.mkdir(exist_ok=True, parents=True)
    return path

def logs_db_path():
    """
    Returns the path to the logs database.

    Returns:
        pathlib.Path: The path to the logs database.
    """
    return user_dir() / "logs.db"