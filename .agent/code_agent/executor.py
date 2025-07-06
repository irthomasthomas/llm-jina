"""
Handles the execution of generated tests against generated code.
"""
import subprocess
import json
from pathlib import Path
import tempfile
from typing import Dict
import logging
from llm_jina.exceptions import TestExecutionError

logger = logging.getLogger(__name__)

class TestExecutor:
    """
    Executes pytest tests in an isolated temporary directory.
    """
    def __init__(self, timeout: int = 60):
        self.timeout = timeout

    def run_tests(self, implementation_code: str, test_code: str) -> Dict:
        """
        Runs tests against the generated code in a temporary environment.
        """
        result = {"passed": False, "passed_tests": 0, "total_tests": 0, "failures": [], "output": ""}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            code_file = temp_path / "generated_code.py"
            test_file = temp_path / "test_generated_code.py"
            report_file = temp_path / "report.json"

            try:
                code_file.write_text(implementation_code, encoding="utf-8")
                test_file.write_text(test_code, encoding="utf-8")

                cmd = ["pytest", str(test_file), "-v", f"--json-report-file={report_file}"]
                
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=temp_dir,
                )
                
                result["output"] = process.stdout + "\n" + process.stderr

                if not report_file.exists():
                    raise TestExecutionError(f"pytest failed to generate a report file. Stderr: {process.stderr}")

                report = json.loads(report_file.read_text())
                summary = report.get("summary", {})
                
                result["total_tests"] = summary.get("total", 0)
                result["passed_tests"] = summary.get("passed", 0)
                result["passed"] = result["total_tests"] > 0 and result["passed_tests"] == result["total_tests"]

                if report.get("tests"):
                    for test in report["tests"]:
                        if test.get("outcome") == "failed":
                            result["failures"].append({
                                "test": test.get("nodeid", "Unknown test"),
                                "error": test.get("longrepr", "No error message"),
                            })

            except subprocess.TimeoutExpired:
                msg = f"Test execution timed out after {self.timeout} seconds."
                result["failures"].append({"error": msg})
                result["output"] += f"\n{msg}"
            except Exception as e:
                msg = f"An unexpected error occurred during test execution: {e}"
                result["failures"].append({"error": msg})
                result["output"] += f"\n{msg}"
                
        return result
