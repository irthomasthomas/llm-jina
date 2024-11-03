# llm-jina

[![PyPI](https://img.shields.io/pypi/v/llm-jina.svg)](https://pypi.org/project/llm-jina/)
[![Changelog](https://img.shields.io/github/v/release/yourusername/llm-jina?include_prereleases&label=changelog)](https://github.com/yourusername/llm-jina/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/yourusername/llm-jina/blob/main/LICENSE)

LLM plugin for interacting with Jina AI APIs

## Table of Contents
- [llm-jina](#llm-jina)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage)
    - [Embedding](#embedding)
    - [Reranking](#reranking)
    - [URL Reading](#url-reading)
    - [Web Search](#web-search)
    - [Fact Checking](#fact-checking)
    - [Text Segmentation](#text-segmentation)
    - [Classification](#classification)
    - [Code Generation](#code-generation)
    - [Metaprompt](#metaprompt)
  - [Development](#development)
  - [Contributing](#contributing)

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).

```bash
llm install llm-jina
```

## Configuration

You need to set the `JINA_API_KEY` environment variable with your Jina AI API key. You can get a free API key from [https://jina.ai/?sui=apikey](https://jina.ai/?sui=apikey).

```bash
export JINA_API_KEY=your_api_key_here
```

## Usage

This plugin adds several commands to interact with Jina AI APIs:

### Embedding

Generate embeddings for given texts:

```bash
llm jina embed "The quick brown fox jumps over the lazy dog."
```

You can specify a different model using the `--model` option:

```bash
llm jina embed "To be, or not to be, that is the question." --model jina-embeddings-v2-base-en
```

### Reranking

Rerank documents based on a query:

```bash
llm jina rerank "Best sci-fi movies" "Star Wars: A New Hope" "The Matrix" "Blade Runner" "Interstellar" "2001: A Space Odyssey"
```

You can specify a different model using the `--model` option:

```bash
llm jina rerank "Healthy eating tips" "Eat more fruits and vegetables" "Limit processed foods" "Stay hydrated" --model jina-reranker-v2-base-en 
```

### URL Reading

Read and parse content from a URL:

```bash
llm jina read https://en.wikipedia.org/wiki/Artificial_intelligence
```

You can include link and image summaries:

```bash
llm jina read https://www.nasa.gov/topics/moon-to-mars --with-links --with-images
```

### Web Search

Search the web for information:

```bash
llm jina search "History of the internet"
```

You can limit the search to a specific domain:

```bash
llm jina search "Python programming tutorials" --site docs.python.org 
```

Example with multiple options:

```bash
llm jina search "Climate change impacts" --site nasa.gov --with-links --with-images
```

### Fact Checking

Verify the factual accuracy of a statement:

```bash
llm jina ground "The Mona Lisa was painted by Leonardo da Vinci."
```

You can provide specific sites for grounding:

```bash
llm jina ground "Jina AI offers state-of-the-art AI models." --sites https://jina.ai,https://docs.jina.ai
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

### Code Generation

Generate Jina API code based on a prompt:

```bash
llm jina generate-code "Create a function that searches Wikipedia for information about famous scientists and reranks the results based on relevance to the query."
```

```bash
llm jina generate-code "Create a function that searches for information about AI and reranks the results based on relevance"
```

### Metaprompt

Display the Jina metaprompt used for generating code:

```bash
llm jina metaprompt
```

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

```bash 
cd llm-jina
python3 -m venv venv
source venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
pytest
```

## Contributing

Contributions to this plugin are welcome! Please refer to the [LLM plugin development documentation](https://llm.datasette.io/en/stable/plugins/index.html) for more information on how to get started.