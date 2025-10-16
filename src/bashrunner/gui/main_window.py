"""Main application window."""

from typing import Optional

from loguru import logger
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtWidgets import (  # type: ignore
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from bashrunner.core.command_storage import Command
from bashrunner.core.storage_instance import command_storage


class CommandButton(QPushButton):
    """Button that executes a command when clicked."""

    def __init__(self, command: Command, index: int, parent: Optional[QWidget] = None):
        super().__init__(command.name, parent)
        self.command = command
        self.index = index
        self.clicked.connect(self._execute_command)
        self.setToolTip(command.description or f"Execute: {command.content[:100]}...")
        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _execute_command(self) -> None:
        """Execute the associated command."""
        logger.info(f"Executing command: {self.command.name}")
        success = command_storage.execute_command(self.index)
        if success:
            logger.info(f"Command executed successfully: {self.command.name}")
        else:
            logger.error(f"Command execution failed: {self.command.name}")


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BashRunner")
        self.setMinimumSize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Scroll area for buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container for button grid
        self.buttons_container = QWidget()
        self.buttons_layout = QGridLayout(self.buttons_container)
        self.buttons_layout.setSpacing(10)

        scroll_area.setWidget(self.buttons_container)
        layout.addWidget(scroll_area)

        # Bottom toolbar
        bottom_layout = QHBoxLayout()

        # Commands configuration button
        self.commands_button = QPushButton("Commands")
        self.commands_button.clicked.connect(self._show_commands_config)
        bottom_layout.addWidget(self.commands_button)

        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self._show_settings)
        bottom_layout.addWidget(self.settings_button)

        # Stretch to push buttons to the left
        bottom_layout.addStretch()

        layout.addLayout(bottom_layout)

        # Load initial commands
        self._refresh_buttons()

        logger.info("Main window initialized")

    def _refresh_buttons(self) -> None:
        """Refresh the button grid based on current commands."""
        # Clear existing buttons
        while self.buttons_layout.count():
            child = self.buttons_layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

        commands = command_storage.get_commands()

        if not commands:
            # Show empty state
            empty_label = QLabel("No commands configured.\nClick 'Commands' to add some.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 16px; color: #666; padding: 40px;")
            self.buttons_layout.addWidget(empty_label, 0, 0)
        else:
            # Create buttons in a grid layout
            columns = min(4, len(commands))  # Max 4 columns
            if columns == 0:
                columns = 1

            for i, command in enumerate(commands):
                row = i // columns
                col = i % columns

                button = CommandButton(command, i, self.buttons_container)
                self.buttons_layout.addWidget(button, row, col)

        # Update container size
        self.buttons_container.adjustSize()

        logger.info(f"Refreshed buttons: {len(commands)} commands displayed")

    def _show_commands_config(self) -> None:
        """Show the commands configuration dialog."""
        from bashrunner.gui.commands_config import CommandsConfigDialog

        dialog = CommandsConfigDialog(self)
        dialog.commands_updated.connect(self._refresh_buttons)
        dialog.exec()

    def _show_settings(self) -> None:
        """Show the settings dialog."""
        from bashrunner.gui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(self)
        if dialog.exec():
            settings = dialog.get_settings()
            logger.info(f"Settings updated: {settings}")
            self._refresh_buttons()
