"""Unit tests for GUI widgets."""

from pytestqt.qtbot import QtBot  # type: ignore

from bashrunner.core.command_storage import Command
from bashrunner.gui.commands_config import (
    AddEditCommandDialog,
    CommandEditWidget,
    CommandsConfigDialog,
)
from bashrunner.gui.console_view import ConsoleView
from bashrunner.gui.main_window import CommandButton, MainWindow
from bashrunner.gui.settings_dialog import SettingsDialog


def test_command_edit_widget_initialization(qtbot: QtBot):
    """Test CommandEditWidget initialization."""
    cmd = Command("Test", "single", "echo hello", "Description")
    widget = CommandEditWidget(cmd)
    qtbot.addWidget(widget)

    assert widget.name_edit.text() == "Test"
    assert widget.description_edit.text() == "Description"
    assert widget.content_edit.toPlainText() == "echo hello"
    assert widget.type_combo.currentText() == "Single Command"


def test_command_edit_widget_empty_initialization(qtbot: QtBot):
    """Test CommandEditWidget with no command."""
    widget = CommandEditWidget()
    qtbot.addWidget(widget)

    assert widget.name_edit.text() == ""
    assert widget.description_edit.text() == ""
    assert widget.content_edit.toPlainText() == ""


def test_command_edit_widget_get_command(qtbot: QtBot):
    """Test getting command from CommandEditWidget."""
    widget = CommandEditWidget()
    qtbot.addWidget(widget)

    widget.name_edit.setText("TestCmd")
    widget.content_edit.setPlainText("echo test")
    widget.description_edit.setText("Test description")

    cmd = widget.get_command()
    assert cmd.name == "TestCmd"
    assert cmd.content == "echo test"
    assert cmd.description == "Test description"
    assert cmd.command_type == "single"


def test_command_edit_widget_type_change(qtbot: QtBot):
    """Test changing command type in CommandEditWidget."""
    widget = CommandEditWidget()
    qtbot.addWidget(widget)
    widget.show()

    # Initially single command - check internal state, not visual state
    assert widget._get_command_type() == "single"

    # Change to script
    widget.type_combo.setCurrentText("Script File")
    assert widget._get_command_type() == "script"

    # Change to multi
    widget.type_combo.setCurrentText("Multiple Commands")
    assert widget._get_command_type() == "multi"


def test_command_edit_widget_script_type(qtbot: QtBot):
    """Test CommandEditWidget with script type."""
    cmd = Command("Script", "script", "/path/to/script.sh", "")
    widget = CommandEditWidget(cmd)
    qtbot.addWidget(widget)

    assert widget.type_combo.currentText() == "Script File"
    assert widget.file_path_edit.text() == "/path/to/script.sh"
    assert widget._get_command_type() == "script"


def test_command_button_initialization(qtbot: QtBot):
    """Test CommandButton initialization."""
    cmd = Command("Test", "single", "echo hello", "Test tooltip")
    button = CommandButton(cmd, 0)
    qtbot.addWidget(button)

    assert button.text() == "Test"
    assert "Test tooltip" in button.toolTip()
    assert button.index == 0


def test_main_window_initialization(qtbot: QtBot):
    """Test MainWindow initialization."""
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.windowTitle() == "BashRunner"
    assert window.commands_button is not None
    assert window.settings_button is not None
    assert window.buttons_layout is not None


def test_commands_config_dialog_initialization(qtbot: QtBot):
    """Test CommandsConfigDialog initialization."""
    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Commands Configuration"
    assert dialog.commands_list is not None
    assert dialog.add_button is not None
    assert dialog.edit_button is not None
    assert dialog.delete_button is not None
    assert dialog.move_up_button is not None
    assert dialog.move_down_button is not None
    assert dialog.close_button is not None


def test_commands_config_dialog_button_states(qtbot: QtBot):
    """Test button states in CommandsConfigDialog."""
    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    # With no selection, buttons should be disabled
    dialog.commands_list.setCurrentRow(-1)
    dialog._update_button_states()

    assert not dialog.edit_button.isEnabled()
    assert not dialog.delete_button.isEnabled()
    assert not dialog.move_up_button.isEnabled()
    assert not dialog.move_down_button.isEnabled()


def test_add_edit_command_dialog_initialization_add(qtbot: QtBot):
    """Test AddEditCommandDialog initialization for adding."""
    dialog = AddEditCommandDialog()
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Add Command"
    assert dialog.edit_widget is not None
    assert dialog.save_button is not None
    assert dialog.cancel_button is not None


def test_add_edit_command_dialog_initialization_edit(qtbot: QtBot):
    """Test AddEditCommandDialog initialization for editing."""
    cmd = Command("Test", "single", "echo hello", "Description")
    dialog = AddEditCommandDialog(cmd)
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Edit Command"
    assert dialog.edit_widget is not None
    assert dialog.edit_widget.name_edit.text() == "Test"


def test_add_edit_command_dialog_get_command(qtbot: QtBot):
    """Test getting command from AddEditCommandDialog."""
    dialog = AddEditCommandDialog()
    qtbot.addWidget(dialog)

    dialog.edit_widget.name_edit.setText("TestCmd")
    dialog.edit_widget.content_edit.setPlainText("echo test")
    dialog.edit_widget.description_edit.setText("Test description")

    cmd = dialog.get_command()
    assert cmd.name == "TestCmd"
    assert cmd.content == "echo test"
    assert cmd.description == "Test description"


def test_settings_dialog_initialization(qtbot: QtBot):
    """Test SettingsDialog initialization."""
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Settings"
    assert dialog.auto_refresh_checkbox is not None
    assert dialog.columns_spinbox is not None


def test_settings_dialog_get_settings(qtbot: QtBot):
    """Test getting settings from SettingsDialog."""
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    dialog.auto_refresh_checkbox.setChecked(False)
    dialog.columns_spinbox.setValue(3)

    settings = dialog.get_settings()
    assert settings["auto_refresh"] is False
    assert settings["grid_columns"] == 3


def test_settings_dialog_default_values(qtbot: QtBot):
    """Test default values in SettingsDialog."""
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    settings = dialog.get_settings()
    assert settings["auto_refresh"] is True
    assert settings["grid_columns"] == 4


def test_console_view_initialization(qtbot: QtBot):
    """Test ConsoleView initialization."""
    console = ConsoleView()
    qtbot.addWidget(console)

    assert console.console_text is not None
    assert console.console_text.isReadOnly()
    assert console.console_text.toPlainText() == ""


def test_console_view_append_output(qtbot: QtBot):
    """Test appending output to ConsoleView."""
    console = ConsoleView()
    qtbot.addWidget(console)

    console.append_output("Test output\n")
    console.append_output("More output\n")

    text = console.console_text.toPlainText()
    assert "Test output" in text
    assert "More output" in text


def test_console_view_append_error(qtbot: QtBot):
    """Test appending error to ConsoleView."""
    console = ConsoleView()
    qtbot.addWidget(console)

    console.append_error("Error message\n")

    # Check that text was added (HTML parsing makes exact match difficult)
    assert len(console.console_text.toPlainText()) > 0


def test_console_view_clear(qtbot: QtBot):
    """Test clearing ConsoleView."""
    console = ConsoleView()
    qtbot.addWidget(console)

    console.append_output("Test output\n")
    assert len(console.console_text.toPlainText()) > 0

    console.clear()
    assert console.console_text.toPlainText() == ""


def test_main_window_has_console_view(qtbot: QtBot):
    """Test that MainWindow has console view."""
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.console_view is not None
    assert window.stacked_widget is not None
    assert window.main_tab_button is not None
    assert window.console_tab_button is not None


def test_main_window_switch_view(qtbot: QtBot):
    """Test switching views in MainWindow."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Initially on main view
    assert window.stacked_widget.currentIndex() == 0
    assert window.main_tab_button.isChecked()
    assert not window.console_tab_button.isChecked()

    # Switch to console view
    window._switch_view(1)
    assert window.stacked_widget.currentIndex() == 1
    assert not window.main_tab_button.isChecked()
    assert window.console_tab_button.isChecked()

    # Switch back to main view
    window._switch_view(0)
    assert window.stacked_widget.currentIndex() == 0
    assert window.main_tab_button.isChecked()
    assert not window.console_tab_button.isChecked()
