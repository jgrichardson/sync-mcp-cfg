# Contributing to Sync MCP Config

Thank you for your interest in contributing to Sync MCP Config! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/jgrichardson/sync-mcp-cfg.git
   cd sync-mcp-cfg
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Verify the setup**:
   ```bash
   sync-mcp-cfg --help
   pytest
   ```

## 🛠️ Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write your code following the project's coding standards
- Add tests for new functionality
- Update documentation as needed

### 3. Run Quality Checks

```bash
# Format code
black src/ tests/

# Lint code  
ruff src/ tests/

# Type checking
mypy src/

# Run tests
pytest

# Run all pre-commit hooks
pre-commit run --all-files
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add support for new MCP client"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## 📝 Coding Standards

### Code Style

- **Formatting**: We use [Black](https://black.readthedocs.io/) with default settings
- **Linting**: We use [Ruff](https://docs.astral.sh/ruff/) for fast linting
- **Type Hints**: All new code should include type hints
- **Line Length**: 88 characters (Black default)

### Code Organization

- **Imports**: Use absolute imports, group by standard/third-party/local
- **Functions**: Keep functions focused and well-documented
- **Classes**: Use dataclasses or Pydantic models for data structures
- **Error Handling**: Use custom exceptions from `core.exceptions`

### Documentation

- **Docstrings**: Use Google-style docstrings for all public functions/classes
- **Comments**: Explain complex logic, not obvious code
- **Type Hints**: Document complex types and return values

Example:
```python
def add_server(self, server: MCPServer) -> None:
    """Add a server to the client configuration.
    
    Args:
        server: The MCP server configuration to add.
        
    Raises:
        ClientHandlerError: If the server cannot be added.
    """
```

## 🧪 Testing

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test CLI commands and client interactions  
- **Mock Tests**: Mock external dependencies (file system, etc.)

### Writing Tests

```python
import pytest
from sync_mcp_cfg.core.models import MCPServer, MCPServerType

def test_mcp_server_creation():
    """Test MCP server model creation."""
    server = MCPServer(
        name="test-server",
        command="echo",
        args=["hello"],
        server_type=MCPServerType.STDIO
    )
    assert server.name == "test-server"
    assert server.enabled is True
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/sync_mcp_cfg

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

## 🏗️ Architecture Guidelines

### Adding New MCP Clients

To add support for a new MCP client:

1. **Create a new client handler**:
   ```python
   # src/sync_mcp_cfg/clients/new_client.py
   from .base import BaseClientHandler
   
   class NewClientHandler(BaseClientHandler):
       def load_servers(self) -> List[MCPServer]:
           # Implementation
           pass
   ```

2. **Add client type**:
   ```python
   # src/sync_mcp_cfg/core/models.py
   class ClientType(str, Enum):
       NEW_CLIENT = "new-client"
   ```

3. **Register the handler**:
   ```python
   # src/sync_mcp_cfg/clients/__init__.py
   CLIENT_HANDLERS[ClientType.NEW_CLIENT] = NewClientHandler
   ```

4. **Add discovery logic**:
   ```python
   # src/sync_mcp_cfg/core/registry.py
   def _discover_new_client(self) -> Optional[ClientConfig]:
       # Implementation
       pass
   ```

### Core Principles

- **Single Responsibility**: Each class/function should have one clear purpose
- **Dependency Injection**: Pass dependencies rather than creating them
- **Error Handling**: Always handle errors gracefully with user-friendly messages
- **Extensibility**: Design for easy addition of new clients and features

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] Tests are added for new functionality
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Pre-commit hooks pass
- [ ] Commit messages follow the conventional commit format

### PR Description Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(clients): add support for new MCP client
fix(cli): handle missing config files gracefully
docs(readme): update installation instructions
```

## 🐛 Bug Reports

### Before Reporting

1. Check if the issue already exists
2. Try to reproduce with minimal example
3. Check if it's fixed in the latest version

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. macOS 12.0]
- Python version: [e.g. 3.9.7]
- Tool version: [e.g. 0.1.0]
- MCP clients: [e.g. Claude Code, Cursor]

**Additional context**
Any other context about the problem.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots about the feature request.
```

## 📞 Getting Help

- 🐛 [GitHub Issues](https://github.com/jgrichardson/sync-mcp-cfg/issues)
- 💬 [GitHub Discussions](https://github.com/jgrichardson/sync-mcp-cfg/discussions)
- 📖 [Documentation](https://github.com/jgrichardson/sync-mcp-cfg/wiki)

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Please be respectful and inclusive in all interactions.

## 🙏 Recognition

Contributors will be recognized in:
- The project's README
- Release notes
- GitHub contributor statistics

Thank you for contributing to Sync MCP Config! 🎉