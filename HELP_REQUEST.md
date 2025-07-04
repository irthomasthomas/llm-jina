# HELP: `ModuleNotFoundError` in Poetry Project with `src` Layout

## Problem

I am unable to run `pytest` successfully in this project. Every attempt fails with a `ModuleNotFoundError`, indicating that the tests in the `tests/` directory cannot find the `llm_jina` package located in the `src/` directory.

## Project Structure

- `pyproject.toml`: Defines the project and dependencies.
- `src/llm_jina/`: Contains the main library code.
- `tests/unit/`: Contains the unit tests.

## What I've Tried

I have attempted the following solutions, all of which resulted in the same `ModuleNotFoundError`:

1.  **Reinstalling Dependencies:** Running `poetry install` multiple times.
2.  **`pytest.ini` Configuration:** Creating a `pytest.ini` file with the following content:
    ```ini
    [pytest]
    pythonpath = src
    ```
3.  **`src/__init__.py`:** Adding an empty `__init__.py` file to the `src` directory.
4.  **Direct `pytest` call:** This failed because `pytest` is not in the global path, confirming the need for `poetry run`.

## My `pyproject.toml`

The `packages` configuration seems correct for a `src` layout:

```toml
[tool.poetry]
name = "llm-jina"
# ...
packages = [{include = "llm_jina", from = "src"}]
```

## Request

What is the correct and idiomatic way to configure a Poetry project with a `src` layout so that `pytest` can discover and import the modules from the `tests` directory? I am clearly missing a key piece of configuration or a fundamental concept.

Please provide the specific configuration or command needed to resolve this `ModuleNotFoundError`.
