# llm-jina Plugin

LLM Plugin for Jina AI: Powerful AI-powered interactions across multiple domains.

## Overview
The `llm-jina` plugin integrates Jina AI services with Simon Willison's llm CLI tool, providing a comprehensive set of AI-powered capabilities directly accessible from the command line.

## Features

- **Web Search** - Search the web with options for domain filtering
- **URL Content Reading** - Extract and process content from URLs
- **Fact Checking** - Verify the factual accuracy of statements
- **Text Embeddings** - Generate vector embeddings for text analysis
- **Document Reranking** - Reorder documents based on relevance to a query
- **Text Segmentation** - Split text into manageable chunks
- **Classification** - Categorize text or images into specified labels
- **Metaprompt Access** - Access Jina's metaprompt system

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

### Search
```bash
llm jina search "AI technology trends"
llm jina search "machine learning papers" --site arxiv.org
llm jina search "news today" --links --images
```

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
llm jina ground "The Earth orbits the Sun" --sites nasa.gov,space.com
```

### Metaprompt
```bash
llm jina metaprompt
```

## Contributing

Contributions welcome! Please read the contributing guidelines.

## Testing

Run the test suite:

```bash
pip install -e ".[dev]"
pytest
```

## License

Apache 2.0
