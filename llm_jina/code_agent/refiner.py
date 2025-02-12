from .generator import CodeGenerator
from .executor import TestExecutor
from .validator import validate_code_safety, CodeValidationError
from .utils import format_error, aggregate_failures
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class CodeRefiner:
    def __init__(self, task: str, model: str, max_retries: int = 5):
        self.generator = CodeGenerator(task, model)
        self.executor = TestExecutor()
        self.max_retries = max_retries

    def refine_code(self, initial_code: str) -> Dict:
        version_history = []
        current_code = initial_code
        for iteration in range(1, self.max_retries + 1):
            test_code = self.generator.generate_tests(current_code)
            try:
                validate_code_safety(test_code)
            except CodeValidationError as e:
                return {
                    "success": False,
                    "error": format_error("Code safety error", e),
                    "versions": version_history,
                }
            test_results = self.executor.run_tests_in_memory(test_code)
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
                    "final_code": current_code,
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
        return {
            "success": False,
            "error": f"Failed after {self.max_retries} iterations.",
            "versions": version_history,
        }
