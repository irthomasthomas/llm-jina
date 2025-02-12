import ast
import logging
from ..exceptions import CodeValidationError

logger = logging.getLogger(__name__)

SAFETY_BLACKLIST = [
    "subprocess", "os.system", "shutil", "rmtree",
    "tempfile", "eval", "exec", "open", "sys.exit",
    "pickle", "marshal", "__import__"
]

def validate_code_safety(code: str) -> None:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise CodeValidationError(f"AST parsing failed: {e}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            else:
                continue
            if func_name in SAFETY_BLACKLIST:
                raise CodeValidationError(f"Security risk: {func_name}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in SAFETY_BLACKLIST:
                    logger.warning(f"Potentially risky module import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module in SAFETY_BLACKLIST:
                logger.warning(f"Potentially risky module import: {node.module}")

    if not any(key in code for key in ['os.environ.get("JINA_API_KEY")', 'os.getenv("JINA_API_KEY")']):
        logger.warning("API key handling not detected.")
