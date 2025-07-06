import logging
from pathlib import Path
from llm import get_model
from llm_jina.metaprompt import jina_metaprompt
from .utils import read_prompt_template

logger = logging.getLogger(__name__)

TEST_PREAMBLE = """# Auto-generated test suite for {filename}
import pytest
import os
assert "JINA_API_KEY" in os.environ, "JINA_API_KEY must be set."
from {module} import *
# Test cases:
"""

class CodeGenerator:
    def __init__(self, task: str, model: str):
        self.task = task
        self.model = model
        self.codegen_prompt = read_prompt_template(Path(__file__).parent / "codegen_prompt.txt")
        self.testgen_prompt = read_prompt_template(Path(__file__).parent / "testgen_prompt.txt")
        self.feedback_prompt = read_prompt_template(Path(__file__).parent / "feedback_prompt.txt")

    def call_model(self, prompt_text: str) -> str:
        try:
            response = get_model(self.model).prompt(prompt_text)
            return self.extract_code(response.text())
        except Exception as e:
            logger.error(f"Error calling model: {e}")
            raise

    def extract_code(self, text: str) -> str:
        if "```python" in text and "```" in text:
            start = text.index("```python") + len("```python")
            end = text.index("```", start)
            return text[start:end].strip()
        return ""

    def generate_initial_code(self) -> str:
        metaprompt_content = jina_metaprompt()
        prompt = self.codegen_prompt.format(metaprompt=metaprompt_content, task=self.task)
        logger.debug(f"Generating initial code with prompt:\n{prompt}")
        try:
            code = get_model(self.model).prompt(prompt)
            logger.debug(f"Generated initial code:\n{code}")
            return code
        except Exception as e:
            logger.error(f"Error generating initial code: {e}")
            raise

    def generate_tests(self, code: str, module_name: str = "generated") -> str:
        prompt = self.testgen_prompt.format(task=self.task, code=code)
        test_code = self.call_model(prompt)
        return TEST_PREAMBLE.format(filename=f"test_{module_name}.py", module=module_name) + test_code

    def generate_new_version(self, code: str, error_feedback: list[str]) -> str:
        prompt = self.feedback_prompt.format(
            task=self.task, error_feedback="\n".join(error_feedback), code=code
        )
        return self.call_model(prompt)
