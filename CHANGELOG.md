# Changelog

## [0.3.0] - 2023-07-25

### Added
- Comprehensive test suite for all API functions
- Added proper error handling for API failures
- Added support for the latest Jina model names
- Added dependency on requests for better API compatibility

### Fixed
- Fixed issue with generate-code command where metaprompt function was called incorrectly
- Resolved conflict between different implementations of jina_metaprompt
- Stopped debug messages from being printed to stdout

### Changed
- Updated documentation with latest API usage examples
- Improved error messages with more context
- Refactored API code for better maintainability

## [0.2.0] - 2023-06-15

### Added
- Code generation capabilities with validation and refinement
- Support for image classification using CLIP model

### Changed
- Updated embeddings API to use v3 model
- Improved error handling in API code

## [0.1.2] - 2023-05-20

### Fixed
- URL parsing in reader API

## [0.1.1] - 2023-05-10

### Added
- Initial integration with Jina AI services
- Basic command line interface
