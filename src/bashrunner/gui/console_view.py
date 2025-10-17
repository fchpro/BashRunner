"""Console view for displaying command output."""

import re

from PySide6.QtCore import Slot  # type: ignore
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor  # type: ignore
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget  # type: ignore


class ConsoleView(QWidget):
    """Widget for displaying console output from command execution."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Console text display
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setFont(QFont("Monospace", 10))
        self.console_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.console_text.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #ffffff;
                border: none;
            }
        """)

        # Set default text color to white
        cursor = self.console_text.textCursor()
        format = cursor.charFormat()
        format.setForeground(QColor("#ffffff"))
        self.console_text.setCurrentCharFormat(format)

        layout.addWidget(self.console_text)

    def _strip_ansi_codes(self, text: str) -> str:
        """Strip ANSI color/formatting codes from text."""
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", text)

    @Slot(str)
    def append_output(self, text: str) -> None:
        """Append text to the console output."""
        # Strip ANSI codes
        clean_text = self._strip_ansi_codes(text)

        # Move cursor to end
        cursor = self.console_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Create text format with white color
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#ffffff"))

        # Insert text with white color
        cursor.insertText(clean_text, fmt)
        self.console_text.setTextCursor(cursor)
        self.console_text.ensureCursorVisible()

    @Slot(str)
    def append_error(self, text: str) -> None:
        """Append error text to the console output with red color."""
        # Strip ANSI codes
        clean_text = self._strip_ansi_codes(text)

        # Move cursor to end
        cursor = self.console_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Use white color for error text as well
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#ffffff"))

        # Insert text with red color
        cursor.insertText(clean_text, fmt)
        self.console_text.setTextCursor(cursor)
        self.console_text.ensureCursorVisible()

    def clear(self) -> None:
        """Clear the console output."""
        self.console_text.clear()
