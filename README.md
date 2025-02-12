# llm-jina

LLM Plugin for Jina AI: Powerful AI-powered interactions across multiple domains.

## Features

- Web Search
- URL Content Reading
- Fact Checking
- Text Embeddings
- Document Reranking
- Text Segmentation
- Classification
- Code Generation

## Installation

```bash
llm install llm-jina
```

## Configuration

Set your Jina AI API key:

```bash
export JINA_API_KEY=your_api_key_here
```

## Usage Examples

### Search
```bash
llm jina search "AI technology trends"
```

### Read URL
```bash
llm jina read https://example.com/article
```

### Embed Text
```bash
llm jina embed "Your text here"
```

### Rerank Documents
```bash
llm jina rerank "machine learning" "Document 1" "Document 2" "Document 3"
```

### Classify
```bash
llm jina classify "Sample text" --labels positive,negative,neutral
```

## Contributing

Contributions welcome! Please read the contributing guidelines.

## License

Apache 2.0
