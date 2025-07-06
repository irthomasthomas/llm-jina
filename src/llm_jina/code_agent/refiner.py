from .generator import CodeGenerator
from .executor import TestExecutor
from .validator import validate_code_safety, CodeValidationError
from .utils import format_error, aggregate_failures
from typing import Dict
import logging
import llm

logger = logging.getLogger(__name__)

class CodeRefiner:
    def __init__(self, task: str, model: str, max_retries: int = 5):
        self.generator = CodeGenerator(task, model)
        self.executor = TestExecutor()
        self.max_retries = max_retries
        self.refinement_prompt = "Refine the following code based on task: {task}\nCurrent Code:\n{code}\n"

    def refine_code(self, initial_code: str) -> Dict:
        """
        Refines the generated code.
        
        Args:
            initial_code (str): The initial code to refine
            
        Returns:
            dict: A dictionary containing:
                - success (bool): Whether refinement was successful
                - final_code (str): The refined code
                - iterations (int): Number of refinement iterations
                - coverage (float): Test coverage percentage
                - error (str, optional): Error message if failed
        """
        version_history = []
        current_code = initial_code
        for iteration in range(1, self.max_retries + 1):
            prompt = self.refinement_prompt.format(task=self.generator.task, code=current_code)
            logger.debug(f"Iteration {iteration}: Refining code with prompt:\n{prompt}")
            try:
                refined_code = llm.get_model(self.generator.model).prompt(prompt)
                validate_code_safety(refined_code)
                test_results = self.executor.run_tests_in_memory(refined_code)
                version_history.append({
                    "iteration": iteration,
                    "passed": test_results["passed"],
                    "failures": test_results["failures"],
                    "coverage": test_results["coverage"],
                    "test_output": test_results["output"],
                })
                if test_results["passed"]:
                    return {
                        "success": True,
                        "final_code": refined_code,
                        "iterations": iteration,
                        "coverage": test_results["coverage"],
                        "versions": version_history,
                    }
                error_msg = aggregate_failures(test_results["failures"])
                new_code = self.generator.generate_new_version(current_code, [error_msg])
                if new_code.strip() == current_code.strip():
                    return {
                        "success": False,
                        "error": f"No changes in iteration {iteration}. Stopping.\nDetails:\n{error_msg}",
                        "versions": version_history,
                    }
                current_code = new_code
            except CodeValidationError as e:
                logger.error(f"Iteration {iteration}: Code safety error: {e}")
                return {
                    "success": False,
                    "error": format_error("Code safety error", e),
                    "versions": version_history,
                }
            except Exception as e:
                logger.error(f"Iteration {iteration}: Refinement error: {e}")
                if iteration == self.max_retries:
                    return {"success": False, "error": str(e), "iterations": iteration}
        return {
            "success": False,
            "error": f"Failed after {self.max_retries} iterations.",
            "versions": version_history,
        }
