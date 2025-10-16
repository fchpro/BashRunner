# BashRunner Development Guide

## Project Structure

```
bashrunner/
├── src/bashrunner/
│   ├── main.py                 # Application entry point
│   ├── core/                   # Core business logic
│   │   ├── command_storage.py  # Command storage and execution
│   │   └── storage_instance.py # Global storage singleton
│   └── gui/                    # GUI components
│       ├── main_window.py      # Main application window
│       ├── commands_config.py  # Commands configuration dialog
│       └── settings_dialog.py  # Settings dialog
├── tests/                      # Test suite
│   ├── test_command_storage.py # Unit tests for core
│   ├── test_gui_widgets.py     # Unit tests for GUI
│   └── test_integration.py     # Integration tests
└── docs/                       # Documentation
```

## Development Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run the application**:
   ```bash
   uv run python src/bashrunner/main.py
   ```

## Code Quality

### Linting

We use **ruff** for linting and code quality checks:

```bash
# Check for linting errors
uv run ruff check src/ tests/

# Auto-fix linting errors
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/
```

### Type Checking

We use **mypy** for static type checking:

```bash
uv run mypy src/
```

Note: PySide6 has dynamic attributes that mypy cannot verify, so some false positives are expected and can be ignored with `# type: ignore` comments.

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_command_storage.py

# Run specific test function
uv run pytest tests/test_command_storage.py::test_add_command
```

### Test Coverage

```bash
# Run tests with coverage report
uv run pytest tests/ --cov=src/bashrunner --cov-report=term-missing

# Generate HTML coverage report
uv run pytest tests/ --cov=src/bashrunner --cov-report=html
# Open htmlcov/index.html in browser
```

**Current Coverage**: 86% (exceeds 80% requirement)

### Test Structure

- **Unit Tests** (`test_command_storage.py`, `test_gui_widgets.py`): Test individual components in isolation
- **Integration Tests** (`test_integration.py`): Test complete user workflows and component interactions

### Testing Philosophy

Following the project's rapid development philosophy:

✅ **DO**:
- Test user-visible behavior
- Test critical paths and data integrity
- Test plugin contracts (not implementations)
- Use real objects when practical
- Write tests that survive refactoring
- Focus on integration over unit tests

❌ **DON'T**:
- Test getters/setters
- Mock everything
- Test implementation details
- Aim for 100% coverage
- Test private methods
- Write brittle UI tests

## Code Style

### General Principles

- **Keep it simple**: Avoid verbose complex code
- **Separation of concerns**: Each function does one thing, each file covers a single concern
- **No print statements**: Use loguru logger instead
- **Type hints**: Use type hints for function parameters and return types
- **Function-based tests**: Each test is a separate function (no classes)

### Import Order

1. Standard library imports
2. Third-party imports
3. Local application imports

Ruff automatically sorts imports.

## Architecture

### Command Storage

The `CommandStorage` class manages:
- Loading/saving commands from/to JSON
- CRUD operations for commands
- Command execution (single, multi, script)

### GUI Components

- **MainWindow**: Main application with button grid
- **CommandsConfigDialog**: Configure, add, edit, delete, reorder commands
- **CommandEditWidget**: Form for editing command details
- **SettingsDialog**: Application settings

### Data Flow

1. User clicks button in MainWindow
2. Button executes command via `command_storage.execute_command(index)`
3. CommandStorage executes the command and logs output
4. Results are logged via loguru

### Hot Reload

When commands are modified in CommandsConfigDialog:
1. Dialog emits `commands_updated` signal
2. MainWindow receives signal and calls `_refresh_buttons()`
3. Button grid is rebuilt with updated commands

## Building and Packaging

The project uses `hatchling` as the build backend:

```bash
uv build
```

## Troubleshooting

### Tests Failing

- Ensure you're using the correct Python version (3.11+)
- Make sure all dependencies are installed: `uv sync`
- Check that Qt is properly initialized (especially for GUI tests)

### Linting Errors

- Run `uv run ruff check --fix` to auto-fix most issues
- Check the ruff configuration in `pyproject.toml`

### Type Checking Errors

- PySide6 dynamic attributes cause false positives in mypy
- Use `# type: ignore` comments on PySide6 imports if needed
- Focus on fixing actual type errors in business logic

## Contributing

1. Create a feature branch
2. Write code following the style guide
3. Add tests for new functionality
4. Ensure all tests pass: `uv run pytest tests/`
5. Check linting: `uv run ruff check src/ tests/`
6. Verify coverage: `uv run pytest --cov=src/bashrunner`
7. Submit a pull request

## Resources

- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [pytest Documentation](https://docs.pytest.org/)
- [ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)

