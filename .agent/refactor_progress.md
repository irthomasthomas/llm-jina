# Jina Embedding Refactor Plan

This document tracks the progress of refactoring the llm-jina plugin to use the standard llm embedding API.

## 1. Research & Planning (In Progress)

- [ ] Download Jina AI metaprompt documentation.
- [ ] Study the Jina embedding API section.
- [ ] Research `llm` CLI documentation for custom embedding models.
- [ ] Analyze the current codebase to locate existing embedding logic.
- [ ] Finalize the refactoring plan.

## 2. Implementation

- [ ] Create a new file for the `llm.EmbeddingModel` implementation.
- [ ] Implement the new embedding model class.
- [ ] Register the model via `pyproject.toml`.
- [ ] Update CLI commands to use the new API.

## 3. Testing & Verification

- [ ] Write unit tests for the new embedding model.
- [ ] Write integration tests for the CLI command.
- [ ] Manually verify the embedding functionality.

## 4. Documentation & Cleanup

- [ ] Update README.md with new usage instructions.
- [ ] Remove old, redundant code.
- [ ] Final code review.
