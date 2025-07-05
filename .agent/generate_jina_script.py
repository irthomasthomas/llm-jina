#!/usr/bin/env python3
import os
import llm
import re

def extract_python_files(text: str) -> dict:
    """
    Extract Python files from a response containing <python_file> tags.
    Returns a dictionary mapping filenames to their content.
    """
    files = {}
    # Pattern to match <python_file filename="...">...</python_file>
    pattern = r'<python_file\s+filename=["\']([^"\']+)["\']>(.*?)</python_file>'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        for filename, content in matches:
            files[filename] = content.strip()
        return files
        
    # Also check for files indicated by markdown code blocks with filename comments
    pattern = r'```python\s*#\s*(\S+\.py)\s*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        for filename, content in matches:
            files[filename] = content.strip()
        return files

    # If still no files found, look for a single code block and save as a generic file
    if "```python" in text and "```" in text:
        start = text.index("```python") + len("```python")
        end = text.index("```", start)
        code = text[start:end].strip()
        files["jina_reader_script.py"] = code
        
    return files

def main():
    # Load the metaprompt
    try:
        with open("jina-metaprompt.md", "r", encoding="utf-8") as f:
            metaprompt = f.read()
    except:
        print("Warning: Could not read metaprompt file. Using a placeholder.")
        metaprompt = "You are an AI assistant that helps users with Jina AI APIs."
    
    # Create the prompt
    task = "Create a simple script that uses Jina Reader API to extract content from a URL and save it to a file."
    
    prompt = f"""
You are tasked with creating a Python script that uses the Jina Reader API to extract content from a URL and save that content to a file.

The script should:
1. Take a URL as an input parameter
2. Take an output filename as an input parameter (with a default value)
3. Use the Jina Reader API to extract content from the URL
4. Save the extracted content to the specified file
5. Include proper error handling and user feedback

Here are the details of the Jina Reader API:
- Endpoint: https://r.jina.ai/
- HTTP Method: POST
- Authentication: Bearer token from JINA_API_KEY environment variable
- Required Headers:
  - Authorization: Bearer $JINA_API_KEY
  - Content-Type: application/json
  - Accept: application/json
- Request Body: JSON with "url" field

The response format will be a JSON with the extracted content in the response["data"]["content"] field.

Please provide a complete, well-commented, and production-ready Python script that handles all the above requirements.

Your code should be presented in this format:
<python_file filename="jina_reader_script.py">
# Code goes here
</python_file>
"""
    
    # Call the model
    model = "claude-3.5-haiku"  # Adjust as needed
    response = llm.get_model(model).prompt(prompt)
    
    print(f"Generated response using {model}")
    
    # Extract code
    files = extract_python_files(str(response))
    
    if files:
        print(f"Found {len(files)} file(s) in the response")
        for filename, content in files.items():
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved {filename}")
    else:
        print("No code files found in the response")
        fallback_file = "full_response.txt"
        with open(fallback_file, "w", encoding="utf-8") as f:
            f.write(str(response))
        print(f"Saved full response to {fallback_file}")

if __name__ == "__main__":
    main()
