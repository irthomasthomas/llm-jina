import llm
from llm.cli import logs_db_path
import sqlite_utils
import datetime
import uuid

def log_to_database(model, prompt, response):
    """
    Manually logs a prompt and response to the LLM database.
    """
    db = sqlite_utils.Database(logs_db_path())
    
    response_row = {
        "id": f"jina-{uuid.uuid4()}",
        "model": model.model_id,
        "prompt": prompt,
        "response": response.text(),
        "datetime_utc": datetime.datetime.utcnow().isoformat(),
        "duration_ms": 0, # Placeholder
    }
    
    responses_table = db.table("responses")
    responses_table.insert(response_row, pk="id", alter=True)


def log_code_generation_workflow(task, model, max_retries, final_code, final_test_code, success):
    """
    Logs the result of a code generation workflow to the database.
    """
    db = sqlite_utils.Database(logs_db_path())

    workflow_row = {
        "task": task,
        "model": model,
        "max_retries": max_retries,
        "final_code": final_code,
        "final_test_code": final_test_code,
        "success": success,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }

    workflows_table = db.table("code_generation_workflows")
    workflows_table.insert(workflow_row, pk="id", alter=True)
