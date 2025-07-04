"""
Utility for loading the Jina metaprompt.
"""
from pathlib import Path
import os

def jina_metaprompt() -> str:
    """
    Loads the Jina metaprompt content from the jina-metaprompt.md file.
    It assumes the file is in the project root.
    """
    # This path is fragile, but a simple solution for now.
    # It assumes the script is run from the project root or a similar depth.
    metaprompt_path = Path("jina-metaprompt.md")
    if not metaprompt_path.is_file():
        # Fallback for different execution contexts
        # Note: This is still not perfectly robust.
        # A better solution might involve package data.
        alt_path = Path(__file__).parent.parent.parent / "jina-metaprompt.md"
        if alt_path.is_file():
            metaprompt_path = alt_path
        else:
            raise FileNotFoundError(
                "jina-metaprompt.md not found. Ensure it is in the project root."
            )
    return metaprompt_path.read_text(encoding="utf-8")
