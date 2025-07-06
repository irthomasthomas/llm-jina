"""
Jina AI Classifier API implementation.
"""
from typing import Dict, Any, List, Union, Optional
from .client import JinaClient

def classify(
    inputs: List[Union[str, Dict[str, str]]],
    labels: List[str],
    model: Optional[str] = None
) -> Dict[str, Any]:
    """Classify text or images using Jina AI Classifier API."""
    client = JinaClient()
    
    if not model:
        if isinstance(inputs[0], str):
            model = "jina-embeddings-v3"
        elif isinstance(inputs[0], dict) and "image" in inputs[0]:
            model = "jina-clip-v2"
        else:
            raise ValueError("Invalid input type. Must be list of strings or image dicts.")

    api_inputs = inputs
    if model == "jina-clip-v2":
        # Ensure all items are in the correct format for image classification
        formatted_inputs = []
        for item in inputs:
            if isinstance(item, str):
                formatted_inputs.append({"image": item}) 
            else:
                formatted_inputs.append(item)
        api_inputs = formatted_inputs

    data = {"model": model, "input": api_inputs, "labels": labels}
    
    response = client.post("https://api.jina.ai/v1/classify", data=data)
    return response

