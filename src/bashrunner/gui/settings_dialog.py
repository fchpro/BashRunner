"""Settings dialog."""

from typing import Any, Dict, Optional

from loguru import logger
from PySide6.QtWidgets import (  # type: ignore
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        # General settings group
        general_group = QGroupBox("General")
        general_layout = QVBoxLayout(general_group)

        # Auto-refresh buttons after command execution
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh buttons after command execution")
        self.auto_refresh_checkbox.setChecked(True)
        general_layout.addWidget(self.auto_refresh_checkbox)

        # Button grid columns
        columns_layout = QHBoxLayout()
        columns_layout.addWidget(QLabel("Button grid columns:"))
        self.columns_spinbox = QSpinBox()
        self.columns_spinbox.setRange(1, 8)
        self.columns_spinbox.setValue(4)
        columns_layout.addWidget(self.columns_spinbox)
        columns_layout.addStretch()
        general_layout.addLayout(columns_layout)

        layout.addWidget(general_group)

        # Dialog buttons
        buttons_layout = QHBoxLayout()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)

        logger.info("Settings dialog initialized")

    def get_settings(self) -> Dict[str, Any]:
        """Get current settings as a dictionary."""
        return {
            "auto_refresh": self.auto_refresh_checkbox.isChecked(),
            "grid_columns": self.columns_spinbox.value(),
        }
