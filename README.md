# llm-jina Plugin

LLM Plugin for Jina AI: Powerful AI-powered interactions across multiple domains.

## Overview
The `llm-jina` plugin integrates Jina AI services with Simon Willison's llm CLI tool, providing a comprehensive set of AI-powered capabilities directly accessible from the command line.

<<<<<<< HEAD
## Table of Contents
- [llm-jina Plugin](#llm-jina-plugin)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage Examples](#usage-examples)
    - [Read URL](#read-url)
    - [Embed Text](#embed-text)
    - [Rerank Documents](#rerank-documents)
    - [Segment Text](#segment-text)
    - [Classify](#classify)
    - [Ground (Fact Checking)](#ground-fact-checking)
    - [Text Segmentation](#text-segmentation)
    - [Classification](#classification)
    - [Metaprompt](#metaprompt)
  - [Development](#development)
  - [Testing](#testing)
  - [License](#license)
## Features

- **Web Search** - Search the web with options for domain filtering
- **URL Content Reading** - Extract and process content from URLs
- **Fact Checking** - Verify the factual accuracy of statements
- **Text Embeddings** - Generate vector embeddings for text analysis
- **Document Reranking** - Reorder documents based on relevance to a query
- **Text Segmentation** - Split text into manageable chunks
- **Classification** - Categorize text or images into specified labels
- **Metaprompt Access** - Access Jina's metaprompt system
>>>>>>> origin/main

## Installation

```bash
pip install llm-jina
# or
llm install llm-jina
```

## Configuration

Set your Jina AI API key:

```bash
export JINA_API_KEY=your_api_key_here
```

You can get a Jina AI API key from [jina.ai](https://jina.ai/?sui=apikey).

## Usage Examples

### Read URL
```bash
llm jina read https://example.com/article
llm jina read https://blog.jina.ai --links
llm jina read https://docs.python.org/3/ --format markdown
```

### Embed Text
```bash
llm jina embed "Your text here"
llm jina embed "Compare similarity using embeddings" --model jina-embeddings-v3
```

### Rerank Documents
```bash
llm jina rerank "machine learning" "Document about NLP" "Paper on computer vision" "Article about ML"
```

### Segment Text
```bash
llm jina segment "Long text to be split into chunks" --return-chunks
```

### Classify
```bash
llm jina classify "I love this product!" --labels positive,negative,neutral
llm jina classify --image cat.jpg dog.jpg --labels cat,dog
```

### Ground (Fact Checking)
```bash
llm jina websearch "History of the internet"
```

You can limit the search to a specific domain:

```bash
llm jina websearch "Python programming tutorials" --site docs.python.org
```

Example with multiple options:

```bash
llm jina websearch "Climate change impacts" --site nasa.gov --with-links --with-images
```

### Text Segmentation 

Segment text into tokens or chunks:

```bash
llm jina segment --content "Space: the final frontier. These are the voyages of the starship Enterprise. Its five-year mission: to explore strange new worlds. To seek out new life and new civilizations. To boldly go where no man has gone before
In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep." --tokenizer cl100k_base --return-chunks
```

Example response:
```json
{
  "chunks": [
    "Space: the final frontier. These are the voyages of the starship Enterprise. Its five-year mission: to explore strange new worlds. To seek out new life and new civilizations. To boldly go where no man has gone before\n",
    "In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep."
  ]
}
```

### Classification

Classify inputs into given labels:

```bash
llm jina classify "The movie was amazing! I loved every minute of it." "The acting was terrible and the plot made no sense." --labels positive negative neutral 
```

For image classification:

```bash
llm jina classify path/to/cat.jpg path/to/dog.jpg path/to/bird.jpg --labels feline canine avian --image
```

### Metaprompt
```bash
llm jina metaprompt
```

Use the metaprompt to generate code for a specific task:

```bash
llm jina metaprompt | llm "Write a script to use jina_ai to classify images of cats and dogs."
```

## Development

Contributions welcome! Please read the contributing guidelines.

## Testing

Run the test suite:

```bash
pip install -e ".[dev]"
pytest
```

## License

Apache 2.0
