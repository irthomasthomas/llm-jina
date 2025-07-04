"""
Command-line interface for llm-jina.
"""
import click
import json
from pathlib import Path
from . import reader, search, rerank, classifier, segmenter, deepsearch
from .metaprompt import jina_metaprompt
from .code_agent.generator import CodeGenerator
from .code_agent.refiner import CodeRefiner
from .code_agent.executor import TestExecutor, TestExecutionError
from .code_agent.validator import validate_code_safety, CodeValidationError
from .exceptions import APIError, CodeValidationError

@click.group()
def cli():
    """Jina AI API command-line interface."""
    pass

@cli.command()
@click.argument('url')
@click.option('--format', 'return_format', default='markdown', help='Return format (markdown, html, text)')
def read(url, return_format):
    """Read content from a URL."""
    result = reader.read(url=url, return_format=return_format)
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.argument('query')
@click.option('--site', help='Limit search to specific site')
@click.option('--num', 'num_results', type=int, help='Number of results')
def search_web(query, site, num_results):
    """Search the web."""
    result = search.search(query=query, site=site, num_results=num_results)
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.argument('query')
@click.argument('documents', nargs=-1, required=True)
@click.option('--model', default='jina-reranker-v2-base-multilingual', help='Reranker model')
@click.option('--top-n', type=int, help='Number of top results')
def rerank_docs(query, documents, model, top_n):
    """Rerank documents by relevance."""
    result = rerank.rerank(query=query, documents=list(documents), model=model, top_n=top_n)
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.argument('text')
@click.option('--return-chunks', is_flag=True, help='Return semantic chunks')
def segment(text, return_chunks):
    """Segment text into tokens or chunks."""
    result = segmenter.segment(content=text, return_chunks=return_chunks)
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.argument('query')
def deepsearch_query(query):
    """Perform comprehensive investigation."""
    result = deepsearch.deepsearch(query=query)
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.argument("task")
@click.option("-m", "--model", default="claude-3.5-sonnet", help="Model to use for code generation")
@click.option("--max-retries", default=3, help="Max refinement retries")
def generate_code(task: str, model: str, max_retries: int):
    """Generates and refines Python code based on a task description."""
    try:
        click.echo("🚀 Starting code generation workflow...")

        click.echo("📋 Loading metaprompt...")
        metaprompt_content = jina_metaprompt()
        prompt_path = Path(__file__).parent / "code_agent" / "codegen_prompt.txt"
        prompt_template = prompt_path.read_text()
        initial_prompt = prompt_template.format(metaprompt=metaprompt_content, task=task)

        click.echo(f"🔨 Generating initial code using {model}...")
        generator = CodeGenerator(prompt=initial_prompt, model_id=model)
        current_code = generator.generate()
        click.echo("🔒 Validating initial code for safety...")
        validate_code_safety(current_code)
        click.secho("✅ Initial code generated and validated.", fg="green")

        refiner = CodeRefiner(model_id=model, task=task)
        executor = TestExecutor()
        
        final_test_code = ""
        success = False

        for i in range(max_retries):
            iteration = i + 1
            click.echo(f"\n--- Iteration {iteration}/{max_retries} ---")

            click.echo("📝 Generating test cases...")
            current_test_code = refiner.generate_tests(current_code)

            click.echo("🧪 Running tests...")
            test_results = executor.run_tests(current_code, current_test_code)

            if test_results.get("passed"):
                passed_count = test_results.get("passed_tests", 0)
                total_count = test_results.get("total_tests", 0)
                click.secho(f"✅ All {total_count} tests passed!", fg="green")
                final_test_code = current_test_code
                success = True
                break

            passed_count = test_results.get("passed_tests", 0)
            total_count = test_results.get("total_tests", 0)
            click.secho(f"❌ {total_count - passed_count} of {total_count} tests failed.", fg="yellow")
            
            error_details = "\n".join([f["error"] for f in test_results.get("failures", [])])
            feedback_prompt = refiner.create_feedback_prompt(current_code, error_details)
            
            click.echo("🔧 Refining code based on test feedback...")
            refine_generator = CodeGenerator(prompt=feedback_prompt, model_id=model)
            current_code = refine_generator.generate()
            click.echo("🔒 Validating refined code...")
            validate_code_safety(current_code)
            click.secho("✅ Code refined and validated.", fg="green")

        if success:
            Path("final_code.py").write_text(current_code, encoding="utf-8")
            Path("test_final_code.py").write_text(final_test_code, encoding="utf-8")
            click.echo("\n🎉 Success!")
        else:
            click.secho(f"\n💔 Failed after {max_retries} iterations.", fg="red")

    except Exception as e:
        click.secho(f"❌ An unexpected error occurred: {e}", fg="red")

if __name__ == '__main__':
    cli()
