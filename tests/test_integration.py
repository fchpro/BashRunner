"""Integration tests for user workflows."""

import tempfile
from pathlib import Path

import pytest
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtWidgets import QMessageBox  # type: ignore
from pytestqt.qtbot import QtBot  # type: ignore

from bashrunner.core.command_storage import Command, CommandStorage
from bashrunner.gui.commands_config import CommandsConfigDialog
from bashrunner.gui.main_window import MainWindow


@pytest.fixture
def temp_storage():
    """Create a temporary storage for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = CommandStorage(Path(tmpdir))
        yield storage


def test_add_and_save_new_command_workflow(qtbot: QtBot, temp_storage, monkeypatch):
    """Test the complete workflow of adding and saving a new command."""
    # Monkey patch the storage in the dialog module
    import bashrunner.gui.commands_config as config_module

    monkeypatch.setattr(config_module, "command_storage", temp_storage)

    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    # Initial state - no commands
    assert dialog.commands_list.count() == 0

    # Click Add button
    qtbot.mouseClick(dialog.add_button, Qt.LeftButton)

    # Should be in "new command" mode
    assert dialog._is_new_command is True

    # Fill in command details
    dialog.edit_widget.name_edit.setText("Test Command")
    dialog.edit_widget.content_edit.setPlainText("echo hello")
    dialog.edit_widget.description_edit.setText("A test command")

    # Mock the success message box
    monkeypatch.setattr(QMessageBox, "information", lambda *args: None)

    # Click Save button
    qtbot.mouseClick(dialog.save_button, Qt.LeftButton)

    # Command should be added to the list
    assert dialog.commands_list.count() == 1
    assert dialog.commands_list.item(0).text() == "Test Command"

    # Verify in storage
    commands = temp_storage.get_commands()
    assert len(commands) == 1
    assert commands[0].name == "Test Command"
    assert commands[0].content == "echo hello"


def test_edit_existing_command_workflow(qtbot: QtBot, temp_storage, monkeypatch):
    """Test the complete workflow of editing an existing command."""
    # Add a command to storage
    cmd = Command("Original", "single", "echo original", "")
    temp_storage.add_command(cmd)

    # Monkey patch the storage
    import bashrunner.gui.commands_config as config_module

    monkeypatch.setattr(config_module, "command_storage", temp_storage)

    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    # Should have one command
    assert dialog.commands_list.count() == 1

    # Select the command
    dialog.commands_list.setCurrentRow(0)

    # Edit the command
    dialog.edit_widget.name_edit.setText("Modified")
    dialog.edit_widget.content_edit.setPlainText("echo modified")

    # Mock the success message box
    monkeypatch.setattr(QMessageBox, "information", lambda *args: None)

    # Save
    qtbot.mouseClick(dialog.save_button, Qt.LeftButton)

    # Verify changes
    commands = temp_storage.get_commands()
    assert len(commands) == 1
    assert commands[0].name == "Modified"
    assert commands[0].content == "echo modified"


def test_delete_command_workflow(qtbot: QtBot, temp_storage, monkeypatch):
    """Test the complete workflow of deleting a command."""
    # Add commands to storage
    cmd1 = Command("Command1", "single", "echo 1", "")
    cmd2 = Command("Command2", "single", "echo 2", "")
    temp_storage.add_command(cmd1)
    temp_storage.add_command(cmd2)

    # Monkey patch the storage
    import bashrunner.gui.commands_config as config_module

    monkeypatch.setattr(config_module, "command_storage", temp_storage)

    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    # Should have two commands
    assert dialog.commands_list.count() == 2

    # Select first command
    dialog.commands_list.setCurrentRow(0)

    # Mock the confirmation dialog to return Yes
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)

    # Delete
    qtbot.mouseClick(dialog.delete_button, Qt.LeftButton)

    # Should have one command left
    assert dialog.commands_list.count() == 1
    assert dialog.commands_list.item(0).text() == "Command2"

    commands = temp_storage.get_commands()
    assert len(commands) == 1
    assert commands[0].name == "Command2"


def test_move_command_up_workflow(qtbot: QtBot, temp_storage, monkeypatch):
    """Test the complete workflow of moving a command up."""
    # Add commands to storage
    cmd1 = Command("First", "single", "echo 1", "")
    cmd2 = Command("Second", "single", "echo 2", "")
    temp_storage.add_command(cmd1)
    temp_storage.add_command(cmd2)

    # Monkey patch the storage
    import bashrunner.gui.commands_config as config_module

    monkeypatch.setattr(config_module, "command_storage", temp_storage)

    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    # Select second command
    dialog.commands_list.setCurrentRow(1)

    # Move up
    qtbot.mouseClick(dialog.move_up_button, Qt.LeftButton)

    # Order should be reversed
    assert dialog.commands_list.item(0).text() == "Second"
    assert dialog.commands_list.item(1).text() == "First"

    commands = temp_storage.get_commands()
    assert commands[0].name == "Second"
    assert commands[1].name == "First"


def test_move_command_down_workflow(qtbot: QtBot, temp_storage, monkeypatch):
    """Test the complete workflow of moving a command down."""
    # Add commands to storage
    cmd1 = Command("First", "single", "echo 1", "")
    cmd2 = Command("Second", "single", "echo 2", "")
    temp_storage.add_command(cmd1)
    temp_storage.add_command(cmd2)

    # Monkey patch the storage
    import bashrunner.gui.commands_config as config_module

    monkeypatch.setattr(config_module, "command_storage", temp_storage)

    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    # Select first command
    dialog.commands_list.setCurrentRow(0)

    # Move down
    qtbot.mouseClick(dialog.move_down_button, Qt.LeftButton)

    # Order should be reversed
    assert dialog.commands_list.item(0).text() == "Second"
    assert dialog.commands_list.item(1).text() == "First"


def test_main_window_refresh_after_command_update(qtbot: QtBot, temp_storage, monkeypatch):
    """Test that main window refreshes after commands are updated."""
    # Monkey patch the storage
    import bashrunner.gui.main_window as main_module

    monkeypatch.setattr(main_module, "command_storage", temp_storage)

    window = MainWindow()
    qtbot.addWidget(window)

    # Initially no commands
    # (the window loads with empty label initially)

    # Add a command to storage
    cmd = Command("NewCmd", "single", "echo new", "")
    temp_storage.add_command(cmd)

    # Refresh buttons
    window._refresh_buttons()

    # Should have one button now
    assert window.buttons_layout.count() == 1


def test_validation_empty_name(qtbot: QtBot, temp_storage, monkeypatch):
    """Test validation when saving a command with empty name."""
    # Monkey patch the storage
    import bashrunner.gui.commands_config as config_module

    monkeypatch.setattr(config_module, "command_storage", temp_storage)

    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    # Click Add
    qtbot.mouseClick(dialog.add_button, Qt.LeftButton)

    # Leave name empty, but fill content
    dialog.edit_widget.content_edit.setPlainText("echo test")

    # Mock warning dialog
    warning_called = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warning_called.append(True))

    # Try to save
    qtbot.mouseClick(dialog.save_button, Qt.LeftButton)

    # Should show warning
    assert len(warning_called) > 0

    # Should not be added to storage
    assert len(temp_storage.get_commands()) == 0


def test_validation_empty_content(qtbot: QtBot, temp_storage, monkeypatch):
    """Test validation when saving a command with empty content."""
    # Monkey patch the storage
    import bashrunner.gui.commands_config as config_module

    monkeypatch.setattr(config_module, "command_storage", temp_storage)

    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    # Click Add
    qtbot.mouseClick(dialog.add_button, Qt.LeftButton)

    # Fill name but leave content empty
    dialog.edit_widget.name_edit.setText("Test")

    # Mock warning dialog
    warning_called = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warning_called.append(True))

    # Try to save
    qtbot.mouseClick(dialog.save_button, Qt.LeftButton)

    # Should show warning
    assert len(warning_called) > 0

    # Should not be added to storage
    assert len(temp_storage.get_commands()) == 0


def test_multi_command_type_workflow(qtbot: QtBot, temp_storage, monkeypatch):
    """Test creating a multi-command type."""
    # Monkey patch the storage
    import bashrunner.gui.commands_config as config_module

    monkeypatch.setattr(config_module, "command_storage", temp_storage)

    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    # Add new command
    qtbot.mouseClick(dialog.add_button, Qt.LeftButton)

    # Set to multi command type
    dialog.edit_widget.type_combo.setCurrentText("Multiple Commands")
    dialog.edit_widget.name_edit.setText("Multi")
    dialog.edit_widget.content_edit.setPlainText("echo line1\necho line2\necho line3")

    # Mock success dialog
    monkeypatch.setattr(QMessageBox, "information", lambda *args: None)

    # Save
    qtbot.mouseClick(dialog.save_button, Qt.LeftButton)

    # Verify
    commands = temp_storage.get_commands()
    assert len(commands) == 1
    assert commands[0].command_type == "multi"
    assert "echo line1" in commands[0].content
    assert "echo line2" in commands[0].content
