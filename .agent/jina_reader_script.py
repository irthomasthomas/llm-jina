#!/usr/bin/env python3
"""
Jina Reader Content Extraction Script

This script uses the Jina Reader API to extract content from a given URL
and save it to a specified output file.

Dependencies:
- requests
- python-dotenv (optional, for environment variable management)
"""

import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_content_from_url(url, api_key=None):
    """
    Extract content from a given URL using Jina Reader API.

    Args:
        url (str): The URL to extract content from
        api_key (str, optional): Jina API Key. Defaults to environment variable.

    Returns:
        str: Extracted content from the URL

    Raises:
        ValueError: If no API key is provided
        requests.RequestException: For network or API-related errors
    """
    # Validate API key
    if not api_key:
        api_key = os.getenv('JINA_API_KEY')
    
    if not api_key:
        raise ValueError("No Jina API Key found. Please set JINA_API_KEY environment variable.")

    # API endpoint and headers
    endpoint = "https://r.jina.ai/"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Request payload
    payload = {"url": url}

    try:
        # Send POST request to Jina Reader API
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        
        # Raise an exception for bad HTTP responses
        response.raise_for_status()

        # Parse JSON response
        result = response.json()

        # Extract and return content
        return result.get('data', {}).get('content', '')

    except requests.RequestException as e:
        print(f"Error extracting content: {e}")
        sys.exit(1)

def save_content_to_file(content, output_file):
    """
    Save extracted content to a file.

    Args:
        content (str): Content to be saved
        output_file (str): Path to output file

    Raises:
        IOError: For file writing errors
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Content successfully saved to {output_file}")
    except IOError as e:
        print(f"Error writing to file {output_file}: {e}")
        sys.exit(1)

def main():
    """
    Main function to parse arguments and orchestrate content extraction and saving.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Extract content from a URL using Jina Reader API")
    parser.add_argument("url", help="URL to extract content from")
    parser.add_argument("-o", "--output", 
                        default="extracted_content.txt", 
                        help="Output filename (default: extracted_content.txt)")
    
    # Parse arguments
    args = parser.parse_args()

    try:
        # Extract content
        content = extract_content_from_url(args.url)

        # Save content to file
        save_content_to_file(content, args.output)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()