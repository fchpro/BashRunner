"""Unit tests for command storage module."""

import tempfile
from pathlib import Path

import pytest

from bashrunner.core.command_storage import Command, CommandStorage


@pytest.fixture
def temp_storage_path():
    """Create a temporary storage path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage(temp_storage_path):
    """Create a CommandStorage instance with temporary path."""
    return CommandStorage(temp_storage_path)


def test_command_creation():
    """Test creating a Command instance."""
    cmd = Command("Test", "single", "echo hello", "Test description")
    assert cmd.name == "Test"
    assert cmd.command_type == "single"
    assert cmd.content == "echo hello"
    assert cmd.description == "Test description"


def test_command_to_dict():
    """Test converting Command to dictionary."""
    cmd = Command("Test", "single", "echo hello", "Test description")
    cmd_dict = cmd.to_dict()
    assert cmd_dict == {
        "name": "Test",
        "command_type": "single",
        "content": "echo hello",
        "description": "Test description",
    }


def test_command_from_dict():
    """Test creating Command from dictionary."""
    data = {
        "name": "Test",
        "command_type": "single",
        "content": "echo hello",
        "description": "Test description",
    }
    cmd = Command.from_dict(data)
    assert cmd.name == "Test"
    assert cmd.command_type == "single"
    assert cmd.content == "echo hello"
    assert cmd.description == "Test description"


def test_storage_initialization(temp_storage_path):
    """Test CommandStorage initialization."""
    storage = CommandStorage(temp_storage_path)
    assert storage.storage_path == temp_storage_path
    assert storage.commands_file == temp_storage_path / "commands.json"
    assert storage.get_commands() == []


def test_add_command(storage):
    """Test adding a command."""
    cmd = Command("Test", "single", "echo hello", "")
    storage.add_command(cmd)
    commands = storage.get_commands()
    assert len(commands) == 1
    assert commands[0].name == "Test"


def test_get_commands_returns_copy(storage):
    """Test that get_commands returns a copy, not the original list."""
    cmd = Command("Test", "single", "echo hello", "")
    storage.add_command(cmd)

    commands1 = storage.get_commands()
    commands2 = storage.get_commands()

    assert commands1 is not commands2
    assert commands1 == commands2


def test_update_command(storage):
    """Test updating a command."""
    cmd = Command("Test", "single", "echo hello", "")
    storage.add_command(cmd)

    updated_cmd = Command("Updated", "multi", "echo world\nls", "New description")
    result = storage.update_command(0, updated_cmd)

    assert result is True
    commands = storage.get_commands()
    assert commands[0].name == "Updated"
    assert commands[0].command_type == "multi"
    assert commands[0].content == "echo world\nls"


def test_update_command_invalid_index(storage):
    """Test updating with invalid index."""
    cmd = Command("Test", "single", "echo hello", "")
    storage.add_command(cmd)

    updated_cmd = Command("Updated", "single", "echo world", "")
    result = storage.update_command(5, updated_cmd)

    assert result is False
    commands = storage.get_commands()
    assert len(commands) == 1
    assert commands[0].name == "Test"


def test_delete_command(storage):
    """Test deleting a command."""
    cmd1 = Command("Test1", "single", "echo hello", "")
    cmd2 = Command("Test2", "single", "echo world", "")
    storage.add_command(cmd1)
    storage.add_command(cmd2)

    result = storage.delete_command(0)

    assert result is True
    commands = storage.get_commands()
    assert len(commands) == 1
    assert commands[0].name == "Test2"


def test_delete_command_invalid_index(storage):
    """Test deleting with invalid index."""
    cmd = Command("Test", "single", "echo hello", "")
    storage.add_command(cmd)

    result = storage.delete_command(5)

    assert result is False
    commands = storage.get_commands()
    assert len(commands) == 1


def test_move_command(storage):
    """Test moving a command."""
    cmd1 = Command("Test1", "single", "echo 1", "")
    cmd2 = Command("Test2", "single", "echo 2", "")
    cmd3 = Command("Test3", "single", "echo 3", "")
    storage.add_command(cmd1)
    storage.add_command(cmd2)
    storage.add_command(cmd3)

    result = storage.move_command(0, 2)

    assert result is True
    commands = storage.get_commands()
    assert commands[0].name == "Test2"
    assert commands[1].name == "Test3"
    assert commands[2].name == "Test1"


def test_move_command_invalid_indices(storage):
    """Test moving with invalid indices."""
    cmd = Command("Test", "single", "echo hello", "")
    storage.add_command(cmd)

    result = storage.move_command(0, 5)

    assert result is False


def test_persistence(temp_storage_path):
    """Test that commands are persisted to disk."""
    storage1 = CommandStorage(temp_storage_path)
    cmd = Command("Test", "single", "echo hello", "")
    storage1.add_command(cmd)

    # Create new storage instance with same path
    storage2 = CommandStorage(temp_storage_path)
    commands = storage2.get_commands()

    assert len(commands) == 1
    assert commands[0].name == "Test"
    assert commands[0].content == "echo hello"


def test_load_corrupted_file(temp_storage_path):
    """Test loading from a corrupted JSON file."""
    commands_file = temp_storage_path / "commands.json"
    commands_file.write_text("invalid json{")

    storage = CommandStorage(temp_storage_path)
    assert storage.get_commands() == []


def test_execute_single_command(storage):
    """Test executing a single command."""
    cmd = Command("Echo", "single", "echo test", "")
    storage.add_command(cmd)

    result = storage.execute_command(0)
    assert result is True


def test_execute_multi_commands(storage):
    """Test executing multiple commands."""
    cmd = Command("Multi", "multi", "echo line1\necho line2", "")
    storage.add_command(cmd)

    result = storage.execute_command(0)
    assert result is True


def test_execute_failing_command(storage):
    """Test that commands launch successfully even if they eventually fail.
    
    With non-blocking execution, we can't immediately detect if a command fails.
    The return value indicates whether the process launched, not whether it succeeded.
    """
    cmd = Command("Fail", "single", "false", "")  # false command always fails
    storage.add_command(cmd)

    result = storage.execute_command(0)
    # With non-blocking execution, this returns True if the process launched
    assert result is True


def test_execute_nonexistent_script(storage):
    """Test executing a nonexistent script."""
    cmd = Command("Script", "script", "/nonexistent/script.sh", "")
    storage.add_command(cmd)

    result = storage.execute_command(0)
    assert result is False


def test_execute_invalid_index(storage):
    """Test executing with invalid index."""
    result = storage.execute_command(5)
    assert result is False


def test_empty_storage_get_commands(storage):
    """Test getting commands from empty storage."""
    commands = storage.get_commands()
    assert commands == []
    assert isinstance(commands, list)


def test_multiple_add_operations(storage):
    """Test adding multiple commands in sequence."""
    for i in range(5):
        cmd = Command(f"Test{i}", "single", f"echo {i}", "")
        storage.add_command(cmd)

    commands = storage.get_commands()
    assert len(commands) == 5
    assert all(cmd.name == f"Test{i}" for i, cmd in enumerate(commands))
