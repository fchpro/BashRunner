"""Main application window."""

from typing import Optional

from loguru import logger
from PySide6.QtCore import Qt, Signal, Slot  # type: ignore
from PySide6.QtWidgets import (  # type: ignore
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from bashrunner.core.command_storage import Command
from bashrunner.core.storage_instance import command_storage
from bashrunner.gui.console_view import ConsoleView


class CommandButton(QPushButton):
    """Button that executes a command when clicked."""

    def __init__(self, command: Command, index: int, parent: Optional[QWidget] = None):
        super().__init__(command.name, parent)
        self.command = command
        self.index = index
        self.clicked.connect(self._execute_command)
        self.setToolTip(command.description or f"Execute: {command.content[:100]}...")
        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

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

    output_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BashRunner")
        self.setMinimumSize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Tab buttons at the top
        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(0)
        tab_layout.setContentsMargins(0, 0, 0, 10)

        self.main_tab_button = QPushButton("Commands")
        self.main_tab_button.setCheckable(True)
        self.main_tab_button.setChecked(True)
        self.main_tab_button.clicked.connect(lambda: self._switch_view(0))
        self.main_tab_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border: 1px solid #ccc;
                border-bottom: none;
                background-color: #f0f0f0;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: white;
            }
        """)
        tab_layout.addWidget(self.main_tab_button)

        self.console_tab_button = QPushButton("Console")
        self.console_tab_button.setCheckable(True)
        self.console_tab_button.clicked.connect(lambda: self._switch_view(1))
        self.console_tab_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border: 1px solid #ccc;
                border-bottom: none;
                background-color: #f0f0f0;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: white;
            }
        """)
        tab_layout.addWidget(self.console_tab_button)

        tab_layout.addStretch()
        layout.addLayout(tab_layout)

        # Stacked widget for views
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Main view with scroll area for buttons
        main_view = QWidget()
        main_view_layout = QVBoxLayout(main_view)
        main_view_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Container for button grid
        self.buttons_container = QWidget()
        self.buttons_layout = QGridLayout(self.buttons_container)
        self.buttons_layout.setSpacing(10)

        scroll_area.setWidget(self.buttons_container)
        main_view_layout.addWidget(scroll_area)

        self.stacked_widget.addWidget(main_view)

        # Console view
        self.console_view = ConsoleView()
        self.stacked_widget.addWidget(self.console_view)

        # Connect signals with QueuedConnection for thread safety
        self.output_signal.connect(
            self.console_view.append_output, Qt.ConnectionType.QueuedConnection
        )
        self.error_signal.connect(
            self.console_view.append_error, Qt.ConnectionType.QueuedConnection
        )

        # Set up command storage callbacks
        command_storage.set_output_callback(self._on_command_output)
        command_storage.set_error_callback(self._on_command_error)

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

    def _switch_view(self, index: int) -> None:
        """Switch between main view and console view."""
        self.stacked_widget.setCurrentIndex(index)
        self.main_tab_button.setChecked(index == 0)
        self.console_tab_button.setChecked(index == 1)

    @Slot(str)
    def _on_command_output(self, text: str) -> None:
        """Handle command output."""
        self.output_signal.emit(text)

    @Slot(str)
    def _on_command_error(self, text: str) -> None:
        """Handle command error output."""
        self.error_signal.emit(text)

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
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
