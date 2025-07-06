import pytest
from click.testing import CliRunner
from unittest.mock import patch
from llm_jina.commands import cli

@pytest.fixture
def runner():
    return CliRunner()

@patch('llm_jina.reader.read')
def test_cli_read_command(mock_read, runner):
    """Test the 'read' CLI command."""
    mock_read.return_value = {"content": "mocked content"}
    result = runner.invoke(cli, ['read', 'https://example.com'])
    
    assert result.exit_code == 0
    assert 'mocked content' in result.output
    mock_read.assert_called_once_with(url='https://example.com')
