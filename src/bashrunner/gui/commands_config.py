"""Commands configuration dialog."""

from typing import Optional

from loguru import logger
from PySide6.QtCore import Qt, Signal  # type: ignore
from PySide6.QtGui import QFont  # type: ignore
from PySide6.QtWidgets import (  # type: ignore
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from bashrunner.core.command_storage import Command
from bashrunner.core.storage_instance import command_storage


class CommandEditWidget(QWidget):
    """Widget for editing a single command."""

    def __init__(self, command: Optional[Command] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.command = command or Command("", "single", "", "")

        layout = QFormLayout(self)

        # Command name
        self.name_edit = QLineEdit(self.command.name)
        self.name_edit.setPlaceholderText("Command name (displayed on button)")
        layout.addRow("Name:", self.name_edit)

        # Command type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Single Command", "Multiple Commands", "Script File"])
        type_display = {
            "single": "Single Command",
            "multi": "Multiple Commands",
            "script": "Script File",
        }.get(self.command.command_type, "Single Command")
        self.type_combo.setCurrentText(type_display)
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        layout.addRow("Type:", self.type_combo)

        # Content area
        self.content_group = QGroupBox("Command Content")
        content_layout = QVBoxLayout(self.content_group)

        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(self.command.content)
        self.content_edit.setFont(QFont("Monospace", 10))
        content_layout.addWidget(self.content_edit)

        # File selection for scripts
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Script file path...")
        if self.command.command_type == "script":
            self.file_path_edit.setText(self.command.content)
        self.file_path_edit.setVisible(self.command.command_type == "script")

        self.file_button = QPushButton("Browse...")
        self.file_button.clicked.connect(self._browse_file)
        self.file_button.setVisible(self.command.command_type == "script")

        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.file_button)
        content_layout.addLayout(file_layout)

        layout.addRow(self.content_group)

        # Description
        self.description_edit = QLineEdit(self.command.description)
        self.description_edit.setPlaceholderText("Optional description")
        layout.addRow("Description:", self.description_edit)

        # Initialize visibility
        self._update_content_visibility()

    def _on_type_changed(self, text: str) -> None:
        """Handle command type change."""
        self._update_content_visibility()

        # Update placeholder text
        command_type = self._get_command_type()
        if command_type == "multi":
            self.content_edit.setPlaceholderText("Enter commands, one per line...")
        else:
            self.content_edit.setPlaceholderText("Enter command...")

    def _update_content_visibility(self) -> None:
        """Update visibility of content widgets based on command type."""
        command_type = self._get_command_type()
        is_script = command_type == "script"
        self.file_path_edit.setVisible(is_script)
        self.file_button.setVisible(is_script)
        self.content_edit.setVisible(not is_script)

    def _get_command_type(self) -> str:
        """Get the current command type."""
        type_map = {
            "Single Command": "single",
            "Multiple Commands": "multi",
            "Script File": "script",
        }
        return type_map.get(self.type_combo.currentText(), "single")

    def _browse_file(self) -> None:
        """Browse for script file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Script File", "", "All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)

    def get_command(self) -> Command:
        """Get the edited command."""
        command_type = self._get_command_type()

        if command_type == "script":
            content = self.file_path_edit.text()
        else:
            content = self.content_edit.toPlainText()

        return Command(
            name=self.name_edit.text().strip(),
            command_type=command_type,
            content=content,
            description=self.description_edit.text().strip(),
        )


class CommandsConfigDialog(QDialog):
    """Dialog for configuring commands."""

    commands_updated = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Commands Configuration")
        self.setMinimumSize(800, 600)
        self._is_new_command = False  # Track if current command is new

        layout = QVBoxLayout(self)

        # Splitter for list and editor
        self.splitter = QSplitter(Qt.Horizontal)

        # Commands list
        list_group = QGroupBox("Commands")
        list_layout = QVBoxLayout(list_group)

        self.commands_list = QListWidget()
        self.commands_list.currentRowChanged.connect(self._on_command_selected)
        list_layout.addWidget(self.commands_list)

        # List controls
        list_controls = QHBoxLayout()

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._add_command)
        list_controls.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_command)
        list_controls.addWidget(self.delete_button)

        self.move_up_button = QPushButton("Move Up")
        self.move_up_button.clicked.connect(self._move_command_up)
        list_controls.addWidget(self.move_up_button)

        self.move_down_button = QPushButton("Move Down")
        self.move_down_button.clicked.connect(self._move_command_down)
        list_controls.addWidget(self.move_down_button)

        list_controls.addStretch()
        list_layout.addLayout(list_controls)

        self.splitter.addWidget(list_group)

        # Command editor
        self.edit_widget = CommandEditWidget()
        self.splitter.addWidget(self.edit_widget)

        # Set splitter proportions
        self.splitter.setSizes([300, 500])

        layout.addWidget(self.splitter)

        # Dialog buttons
        buttons_layout = QHBoxLayout()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_command)
        buttons_layout.addWidget(self.save_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_button)

        layout.addLayout(buttons_layout)

        # Load commands
        self._load_commands()
        self._update_button_states()

        logger.info("Commands configuration dialog initialized")

    def _load_commands(self) -> None:
        """Load commands into the list."""
        self.commands_list.clear()
        commands = command_storage.get_commands()

        for i, command in enumerate(commands):
            item = QListWidgetItem(command.name)
            item.setData(Qt.UserRole, i)  # Store the index
            self.commands_list.addItem(item)

        if commands:
            self.commands_list.setCurrentRow(0)

    def _on_command_selected(self, row: int) -> None:
        """Handle command selection."""
        if row >= 0:
            commands = command_storage.get_commands()
            if row < len(commands):
                command = commands[row]
                self._is_new_command = False
                # Create new edit widget and replace the old one
                new_edit_widget = CommandEditWidget(command, self)
                old_widget = self.splitter.widget(1)
                self.splitter.replaceWidget(1, new_edit_widget)
                if old_widget:
                    old_widget.deleteLater()
                self.edit_widget = new_edit_widget

        self._update_button_states()

    def _update_button_states(self) -> None:
        """Update button enabled states."""
        current_row = self.commands_list.currentRow()
        has_selection = current_row >= 0
        command_count = self.commands_list.count()

        self.delete_button.setEnabled(has_selection and not self._is_new_command)
        self.move_up_button.setEnabled(
            has_selection and current_row > 0 and not self._is_new_command
        )
        self.move_down_button.setEnabled(
            has_selection and current_row < command_count - 1 and not self._is_new_command
        )
        self.save_button.setEnabled(has_selection or self._is_new_command)

    def _add_command(self) -> None:
        """Add a new command."""
        # Create a new empty command in the edit widget
        new_edit_widget = CommandEditWidget(Command("", "single", "", ""), self)
        old_widget = self.splitter.widget(1)
        self.splitter.replaceWidget(1, new_edit_widget)
        if old_widget:
            old_widget.deleteLater()
        self.edit_widget = new_edit_widget

        # Mark as new command
        self._is_new_command = True

        # Deselect any item in the list
        self.commands_list.setCurrentRow(-1)

        # Update button states
        self._update_button_states()

        logger.info("Adding new command")

    def _delete_command(self) -> None:
        """Delete the selected command."""
        current_row = self.commands_list.currentRow()
        if current_row >= 0 and not self._is_new_command:
            reply = QMessageBox.question(
                self,
                "Delete Command",
                "Are you sure you want to delete this command?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                if command_storage.delete_command(current_row):
                    self._load_commands()
                    self.commands_updated.emit()
                    logger.info("Deleted command")

    def _move_command_up(self) -> None:
        """Move the selected command up."""
        current_row = self.commands_list.currentRow()
        if current_row > 0 and not self._is_new_command:
            if command_storage.move_command(current_row, current_row - 1):
                self._load_commands()
                self.commands_list.setCurrentRow(current_row - 1)
                self.commands_updated.emit()

    def _move_command_down(self) -> None:
        """Move the selected command down."""
        current_row = self.commands_list.currentRow()
        if current_row < self.commands_list.count() - 1 and not self._is_new_command:
            if command_storage.move_command(current_row, current_row + 1):
                self._load_commands()
                self.commands_list.setCurrentRow(current_row + 1)
                self.commands_updated.emit()

    def _save_command(self) -> None:
        """Save the current command."""
        # Get the edited command
        edited_command = self.edit_widget.get_command()

        # Validate
        if not edited_command.name.strip():
            QMessageBox.warning(self, "Invalid Command", "Command name is required.")
            return

        if not edited_command.content.strip():
            QMessageBox.warning(self, "Invalid Command", "Command content is required.")
            return

        if self._is_new_command:
            # Add new command to storage
            command_storage.add_command(edited_command)
            self._is_new_command = False
            logger.info(f"Added new command: {edited_command.name}")
        else:
            # Update existing command
            current_row = self.commands_list.currentRow()
            if current_row >= 0:
                command_storage.update_command(current_row, edited_command)
                logger.info(f"Updated command: {edited_command.name}")

        # Reload the list and emit signal
        self._load_commands()
        self.commands_updated.emit()

        # Show success message
        QMessageBox.information(
            self, "Success", f"Command '{edited_command.name}' saved successfully."
        )
