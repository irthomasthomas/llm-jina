"""
Validates the safety of the generated Python code.
"""
import logging
import re
from llm_jina.exceptions import CodeValidationError

logger = logging.getLogger(__name__)

DANGEROUS_PATTERNS = {
    "os.system": r"os\.system\s*\(",
    "subprocess": r"subprocess\.(run|call|check_call|check_output|Popen)",
    "eval": r"\beval\s*\(",
    "exec": r"\bexec\s*\(",
    "shutil.rmtree": r"shutil\.rmtree\s*\(",
    "pickle": r"pickle\.(load|loads)",
}

def validate_code_safety(code: str) -> None:
    """
    Performs security checks on the generated code.
    """
    for name, pattern in DANGEROUS_PATTERNS.items():
        if re.search(pattern, code):
            logger.error(f"Code validation failed: dangerous pattern '{name}' found.")
            raise CodeValidationError(
                f"Generated code contains a potentially dangerous pattern: {name}."
            )
    logger.debug("Code safety validation passed.")
