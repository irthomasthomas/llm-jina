import subprocess
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class TestExecutionError(Exception):
    pass

class TestExecutor:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def run_tests(self, test_file: str) -> Dict:
        result = {"passed": False, "output": "", "failures": [], "coverage": 0}
        report_path = Path(".report.json")
        try:
            cmd = [
                "pytest",
                test_file,
                "-v",
                "--tb=line",
                "--cov", test_file.replace("test_", "").replace(".py", ""),
                "--cov-report", "term-missing",
                "--json-report=.report.json",
            ]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout, check=False)
            result["output"] = process.stdout + "\n" + process.stderr

            if report_path.exists():
                try:
                    with report_path.open("r", encoding="utf-8") as f:
                        report = json.load(f)
                        summary = report.get("summary", {})
                        result["passed"] = summary.get("passed", 0) == summary.get("total", 0)
                        result["coverage"] = summary.get("coverage", 0)
                        failures = []
                        for test in report.get("tests", []):
                            if test.get("outcome") == "failed":
                                failures.append({
                                    "test": test.get("nodeid", "Unknown"),
                                    "message": test.get("call", {}).get("longrepr", "No message")
                                })
                        result["failures"] = failures
                except json.JSONDecodeError as e:
                    result["output"] += f"\nJSON report parse error: {e}"
                    logger.error(f"JSON report parse error: {e}")
        except subprocess.TimeoutExpired:
            result["output"] = "Test execution timed out!"
            logger.error("Test execution timed out")
            raise TestExecutionError("Test execution timed out")
        except FileNotFoundError:
            result["output"] = "pytest not found. Ensure it is installed."
            logger.error("pytest not found")
            raise TestExecutionError("pytest not found")
        except Exception as e:
            result["output"] = f"Unexpected error: {e}"
            logger.exception(f"Unexpected error during test execution: {e}")
            raise TestExecutionError(f"Unexpected error: {e}")
        finally:
            if report_path.exists():
                report_path.unlink()
        return result

    def run_tests_in_memory(self, test_code: str) -> Dict:
        with NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as temp:
            temp.write(test_code)
            temp_name = temp.name
        try:
            return self.run_tests(temp_name)
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)
