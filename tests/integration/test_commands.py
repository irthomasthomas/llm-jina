import pytest
from unittest.mock import patch, MagicMock
import click
from click.testing import CliRunner
from llm_jina.commands import register_jina_commands
import json


@pytest.fixture
def cli():
    """Create a Click CLI with the jina commands registered"""
    @click.group()
    def root_cli():
        pass
    
    jina_cli = register_jina_commands(root_cli)
    return root_cli


@pytest.fixture
def runner():
    """Create a Click test runner"""
    return CliRunner()


def test_embed_command(cli, runner):
    """Test the 'embed' command"""
    with patch('llm_jina.commands.jina_embed') as mock_embed:
        mock_embed.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] + [0.0] * 90 + [0.6, 0.7, 0.8, 0.9, 1.0]
        
        result = runner.invoke(cli, ['jina', 'embed', 'test text'])
        
        assert result.exit_code == 0
        assert f"Generated embedding with {len(mock_embed.return_value)} dimensions" in result.output
        assert "[0.1, 0.2, 0.3, 0.4, 0.5]" in result.output
        assert "[0.6, 0.7, 0.8, 0.9, 1.0]" in result.output
        mock_embed.assert_called_once_with('test text', model='jina-embeddings-v3', normalized=True)


def test_search_command(cli, runner):
    """Test the 'search' command"""
    mock_results = {"results": [{"title": "Test Result"}]}
    
    with patch('llm_jina.commands.jina_search') as mock_search:
        mock_search.return_value = mock_results
        
        result = runner.invoke(cli, ['jina', 'search', 'test query'])
        
        assert result.exit_code == 0
        assert json.dumps(mock_results, indent=2) in result.output
        mock_search.assert_called_once_with('test query', site=None, with_links=False, with_images=False)


def test_generate_code_command_parameter_issue(cli, runner):
    """Test the 'generate-code' command with metaprompt parameter issue fix"""
    # Mock the response from jina_metaprompt with no parameters
    metaprompt_content = "# Test Metaprompt"
    test_code = "def test(): return True"
    
    with patch('llm_jina.commands.jina_metaprompt', return_value=metaprompt_content) as mock_metaprompt, \
         patch('llm_jina.commands.CodeGenerator') as mock_generator, \
         patch('llm_jina.commands.validate_code_safety') as mock_validate, \
         patch('llm_jina.commands.CodeRefiner') as mock_refiner, \
         patch('llm_jina.commands.Path.write_text'):
        
        # Setup the mock returned values
        generator_instance = MagicMock()
        generator_instance.generate_initial_code.return_value = test_code
        mock_generator.return_value = generator_instance
        
        refiner_instance = MagicMock()
        refiner_instance.refine_code.return_value = {
            "success": True,
            "final_code": "def test(): return True  # Final",
            "iterations": 1,
            "coverage": 90.0
        }
        mock_refiner.return_value = refiner_instance
        
        # Run the command
        result = runner.invoke(cli, ['jina', 'generate-code', 'Create a calculator'])
        
        # Verify the command worked without error
        assert result.exit_code == 0
        assert "Code generated after 1 iterations!" in result.output
        assert "Test coverage: 90.0%" in result.output
        
        # Most importantly, verify jina_metaprompt was called with no arguments
        mock_metaprompt.assert_called_once_with()
