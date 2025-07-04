"""
Handles the generation of Python code using an LLM.
"""
import logging
import llm
import re
from . import utils

logger = logging.getLogger(__name__)

class CodeGenerator:
    """
    Generates Python code from a given prompt using a specified model.
    """
    def __init__(self, prompt: str, model_id: str):
        self.prompt = prompt
        self.model = llm.get_model(model_id)

    def extract_code(self, response_text: str) -> str:
        """
        Extracts the first Python code block from the LLM's response.
        """
        match = re.search(r"```python\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        logger.warning("No python code block found in response. Returning full text.")
        return response_text.strip()

    def generate(self) -> str:
        """
        Generates and returns the initial Python code.
        """
        try:
            logger.debug(f"Generating code with prompt starting with: {self.prompt[:200]}...")
            response = self.model.prompt(self.prompt)
            utils.log_to_database(self.model, self.prompt, response)
            code = self.extract_code(response.text())
            if not code:
                raise ValueError("LLM returned an empty response.")
            return code
        except Exception as e:
            logger.error(f"Error during code generation: {e}")
            raise
