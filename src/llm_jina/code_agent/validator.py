import logging
import re
from ..exceptions import CodeValidationError

logger = logging.getLogger(__name__)

SAFETY_PATTERNS = [
    r"subprocess\.",
    r"os\.system",
    r"shutil\.rmtree",
    r"tempfile\.",
    r"\beval\s*\(",   # eval with optional whitespace
    r"\bexec\s*\(",   # exec with optional whitespace
    r"open\s*\(",     # open
    r"sys\.exit",
    r"pickle\.",
    r"marshal\.",
    r"__import__"
]

def validate_code_safety(code: str) -> None:
    """
    Performs regex-based safety checks on the code.
    """
    for pattern in SAFETY_PATTERNS:
        if re.search(pattern, code):
            logger.error(f"Code validation failed: potentially dangerous pattern '{pattern}' found.")
            raise CodeValidationError(f"Potentially dangerous pattern '{pattern}' found in code.")

    if not re.search(r'os\.(environ\.get|getenv)\(["\']JINA_API_KEY["\']\)', code):
        logger.warning("API key handling not detected.")

    logger.debug("Code safety validation passed.")
