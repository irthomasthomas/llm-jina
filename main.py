import sys
import logging
import traceback
# ...existing code (import ast removed)...

# Configure logger for main operations.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def generate_code(model, request, max_retries=2):
    # ... existing code for interacting with the model ...
    if request == "example request":
        return "def faulty_function():\n    return None"
    else:
        return "def add(a, b):\n    return a + b"

def process_request(model, request, max_retries=2):
    code = generate_code(model, request, max_retries)
    code = str(code)  # Force code to be a string
    if not isinstance(code, str):
        logger.error("Generated code must be a string, got %s", type(code))
        sys.exit(1)

    logger.info("Generated code:\n%s", code)
    return code

def main():
    model = "gemini-2"
    request = "example request"
    max_retries = 2
    process_request(model, request, max_retries)

if __name__ == "__main__":
    main()
