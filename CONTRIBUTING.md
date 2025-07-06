# Contributing to Stockholm Traffic MCP Server

We welcome contributions to the Stockholm Traffic MCP Server! This guide will help you get started with contributing to the project.

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/stockholm-traffic-mcp.git
   cd stockholm-traffic-mcp
   ```

3. **Set up the development environment:**
   ```bash
   # Using uv (recommended)
   uv sync --dev
   
   # Or using pip
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

4. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Tests

We use pytest for testing. Run the full test suite with:

```bash
uv run pytest
```

For verbose output:
```bash
uv run pytest -v
```

### Code Quality

We use ruff for linting and formatting. Before submitting your changes:

```bash
# Check for linting issues
uv run ruff check

# Fix auto-fixable issues
uv run ruff check --fix

# Format code
uv run ruff format
```

### Testing Your Changes

1. **Run the server locally:**
   ```bash
   uv run mcp dev server.py
   ```

2. **Test with MCP inspector** to verify your changes work correctly

3. **Add tests** for any new functionality you implement

## Contribution Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all functions and classes
- Keep functions focused and single-purpose
- Use descriptive variable and function names

### Commit Messages

Write clear, concise commit messages:

```
feat: add support for real-time delays in journey planning

- Enhanced journey planning to include real-time delay information
- Updated response format to include delay indicators
- Added tests for delay handling scenarios
```

Use conventional commit prefixes:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for adding or modifying tests
- `refactor:` for code refactoring
- `style:` for formatting changes
- `chore:` for maintenance tasks

### Pull Request Process

1. **Ensure your branch is up to date** with the main branch:
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature-name
   git rebase main
   ```

2. **Run all tests and linting** to ensure everything passes:
   ```bash
   uv run pytest
   uv run ruff check
   uv run ruff format
   ```

3. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a pull request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Link to any relevant issues
   - Screenshots or examples if applicable

### Testing Requirements

- All new features must include tests
- Bug fixes should include regression tests
- Aim for high test coverage (>90%)
- Tests should be fast and reliable
- Mock external API calls in tests

## Types of Contributions

### Bug Reports

When reporting bugs, please include:
- Clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Relevant logs or error messages

### Feature Requests

For new features:
- Describe the use case and why it would be valuable
- Provide examples of how it would be used
- Consider backwards compatibility
- Discuss implementation approach if you have ideas

### Code Contributions

We welcome:
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements
- Code refactoring

## API Integration Guidelines

### Stockholm Public Transport API

- Always handle API rate limits gracefully
- Include proper error handling for API failures
- Use appropriate timeouts for requests
- Follow the API terms of service
- Consider caching strategies for frequently requested data

### Adding New Features

When adding new features:
1. Check if the SL API supports the functionality
2. Design the MCP tool interface thoughtfully
3. Add comprehensive error handling
4. Include proper documentation
5. Add thorough tests

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all new functions
- Include examples in docstrings
- Update API documentation as needed
- Add inline comments for complex logic

## Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Ask questions when you're unsure
- Share knowledge and best practices

## Getting Help

If you need help with your contribution:
- Check existing issues and discussions
- Create a new issue for questions
- Join the project discussions
- Tag maintainers if you need guidance

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- GitHub contributors list
- Special mentions for outstanding contributions

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## Contact

- **Issues**: [GitHub Issues](https://github.com/argia-andreas/stockholm-traffic-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/argia-andreas/stockholm-traffic-mcp/discussions)

Thank you for contributing to the Stockholm Traffic MCP Server! 🚇🚌🚊