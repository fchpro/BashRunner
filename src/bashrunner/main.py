#!/usr/bin/env python3
"""Main entry point for BashRunner application."""

import sys

from loguru import logger
from PySide6.QtWidgets import QApplication

from bashrunner.gui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Configure logger
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("BashRunner")
    app.setApplicationVersion("0.1.0")

    # Create and show main window
    window = MainWindow()
    window.show()

    logger.info("BashRunner application started")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
