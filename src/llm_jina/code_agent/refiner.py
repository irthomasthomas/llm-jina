"""
Handles the refinement of generated code by generating tests and processing feedback.
"""
import logging
import llm
import re
from . import utils
from pathlib import Path

logger = logging.getLogger(__name__)

TEST_PREAMBLE = """
import pytest
import os
from unittest.mock import MagicMock, patch

if "JINA_API_KEY" not in os.environ:
    os.environ["JINA_API_KEY"] = "mock_api_key_for_testing"

from generated_code import *
"""

class CodeRefiner:
    """
    Generates tests and constructs feedback prompts for code refinement.
    """
    def __init__(self, model_id: str, task: str):
        self.model = llm.get_model(model_id)
        self.task = task
        self.testgen_prompt_template = self.read_prompt("testgen_prompt.txt")
        self.feedback_prompt_template = self.read_prompt("feedback_prompt.txt")

    def read_prompt(self, filename: str) -> str:
        """Reads a prompt template file from the same directory."""
        try:
            return (Path(__file__).parent / filename).read_text(encoding="utf-8")
        except FileNotFoundError:
            # Basic fallback if template files are missing
            if "testgen" in filename:
                return "Generate pytest tests for this code that validates the following task: {task}\n\nCode:\n{code}"
            else:
                return "The code failed tests. Please fix it.\nTask: {task}\nError: {error_feedback}\nCode:\n{code}"

    def generate_tests(self, code_to_test: str) -> str:
        """
        Generates pytest tests for a given block of code.
        """
        prompt = self.testgen_prompt_template.format(task=self.task, code=code_to_test)
        logger.debug("Generating tests...")
        response = self.model.prompt(prompt)
        utils.log_to_database(self.model, prompt, response)
        
        match = re.search(r"```python\n(.*?)\n```", response.text(), re.DOTALL)
        test_code = match.group(1).strip() if match else response.text().strip()
            
        return TEST_PREAMBLE + test_code

    def create_feedback_prompt(self, code: str, error_feedback: str) -> str:
        """
        Creates a new prompt to refine code based on test failures.
        """
        prompt = self.feedback_prompt_template.format(
            task=self.task,
            error_feedback=error_feedback,
            code=code
        )
        return prompt
