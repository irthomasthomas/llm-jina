"""
Custom exceptions for the llm-jina library.
"""

class JinaAPIError(Exception):
    """Custom exception for Jina AI API errors."""
    pass

class APIError(Exception):
    """Generic API Error for compatibility."""
    pass

class CodeValidationError(Exception):
    """Custom exception for code validation errors."""
    pass

class TestExecutionError(Exception):
    """Custom exception for errors during test execution."""
    pass
