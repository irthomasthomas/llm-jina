"""
Unit tests for the full code agent workflow in commands.py.
"""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from llm_jina.commands import cli

@pytest.fixture
def mock_llm_calls():
    """Mocks the llm.get_model().prompt() calls."""
    with patch("llm.get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_get_model.return_value = mock_model
        
        mock_model.prompt.side_effect = [
            MagicMock(text=lambda: "```python\ndef my_func():\n    return 1\n```"),
            MagicMock(text=lambda: "```python\nimport pytest\ndef test_my_func_fail():\n    assert my_func() == 2\n```"),
            MagicMock(text=lambda: "```python\ndef my_func():\n    return 2\n```"),
            MagicMock(text=lambda: "```python\nimport pytest\ndef test_my_func_pass():\n    assert my_func() == 2\n```"),
        ]
        yield mock_model

@pytest.fixture
def mock_executor():
    """Mocks the TestExecutor."""
    with patch("llm_jina.commands.TestExecutor") as mock_executor_class:
        executor_instance = mock_executor_class.return_value
        executor_instance.run_tests.side_effect = [
            {"passed": False, "passed_tests": 0, "total_tests": 1, "failures": [{"error": "AssertionError: assert 1 == 2"}]},
            {"passed": True, "passed_tests": 1, "total_tests": 1, "failures": []},
        ]
        yield executor_instance

@pytest.fixture
def runner():
    return CliRunner()

def test_generate_code_full_success_loop(runner, mock_llm_calls, mock_executor):
    """
    Tests the entire `generate_code` workflow, simulating one failed
    refinement loop followed by a successful one.
    """
    with patch("pathlib.Path.read_text", return_value="Task: {task}\nTemplate: {metaprompt}"):
        result = runner.invoke(
            cli,
            ["generate-code", "Create a function that returns 2", "--max-retries", "2"],
            catch_exceptions=False
        )

    assert result.exit_code == 0
    assert "✅ All 1 tests passed!" in result.output
    assert "🎉 Success!" in result.output
    
    assert mock_llm_calls.prompt.call_count == 4
    assert mock_executor.run_tests.call_count == 2
    
    final_code_call = mock_executor.run_tests.call_args_list[1]
    assert "return 2" in final_code_call.kwargs['implementation_code']
