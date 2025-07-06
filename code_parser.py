import ast
import logging
import traceback
import sys
from typing import Union

# Configure a logger for detailed error messages.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def parse_code(code: Union[str, bytes, ast.AST]) -> ast.AST:
    """
    Parse code into an AST object.
    
    Args:
        code: Input code as string, bytes, or AST object
        
    Returns:
        ast.AST: The parsed abstract syntax tree
        
    Raises:
        TypeError: If code is not string, bytes, or AST
        SyntaxError: If code has invalid syntax
    """
    if isinstance(code, ast.AST):
        return code
    if isinstance(code, bytes):
        code = code.decode('utf-8')
    # Instead of raising an error for non-string types, convert to string.
    if not isinstance(code, str):
        code = str(code)  # Coerce code to string
    
    try:
        tree = ast.parse(code)
        return tree
    except SyntaxError as e:
        logger.error("AST parsing failed: %s", e)
        logger.debug("Code that failed to parse:\n%s", code)
        logger.debug("Traceback:\n%s", traceback.format_exc())
        raise
    except Exception as ex:
        logger.error("Unexpected error during AST parsing: %s", ex)
        logger.debug("Code being parsed:\n%s", code)
        logger.debug("Traceback:\n%s", traceback.format_exc())
        raise

def main():
    correct_code = "def add(a, b):\n    return a + b"
    error_code = "def faulty_function(\n    return None"
    
    logger.info("Parsing correct code...")
    try:
        tree = parse_code(correct_code)
        logger.info("Correct code parsed successfully.")
    except SyntaxError:
        logger.error("Unexpected SyntaxError in correct code.")
    
    logger.info("Parsing error code...")
    try:
        tree = parse_code(error_code)
    except SyntaxError:
        logger.error("SyntaxError encountered as expected with error code.")

if __name__ == "__main__":
    main()
