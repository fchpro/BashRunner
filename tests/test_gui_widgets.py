"""Unit tests for GUI widgets."""

from pytestqt.qtbot import QtBot  # type: ignore

from bashrunner.core.command_storage import Command
from bashrunner.gui.commands_config import CommandEditWidget, CommandsConfigDialog
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
    assert dialog.edit_widget is not None
    assert dialog.add_button is not None
    assert dialog.delete_button is not None
    assert dialog.move_up_button is not None
    assert dialog.move_down_button is not None
    assert dialog.save_button is not None


def test_commands_config_dialog_button_states(qtbot: QtBot):
    """Test button states in CommandsConfigDialog."""
    dialog = CommandsConfigDialog()
    qtbot.addWidget(dialog)

    # With no selection, buttons should be disabled
    dialog.commands_list.setCurrentRow(-1)
    dialog._update_button_states()

    assert not dialog.delete_button.isEnabled()
    assert not dialog.move_up_button.isEnabled()
    assert not dialog.move_down_button.isEnabled()


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

