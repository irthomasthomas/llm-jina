import os
import requests

def extract_web_content(url):
    """
    Extract content from a webpage using Jina Reader API
    
    Args:
        url (str): The webpage URL to extract content from
    
    Returns:
        str: Extracted webpage content
    """
    try:
        # Get API key from environment variable
        api_key = os.environ.get('JINA_API_KEY')
        if not api_key:
            raise ValueError("JINA_API_KEY environment variable not set")

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-No-Cache': 'true'
        }

        response = requests.post('https://r.jina.ai/', 
                                 json={'url': url}, 
                                 headers=headers)
        
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Extract content from the response
        content = response.json().get('data', {}).get('content', '')
        return content

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None
    except ValueError as e:
        print(f"Configuration error: {e}")
        return None