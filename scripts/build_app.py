#!/usr/bin/env python3
"""Build script for packaging BashRunner with PyInstaller."""

import shutil
import subprocess
import sys
from pathlib import Path

from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "BashRunner.spec"

# App metadata
APP_NAME = "BashRunner"
APP_VERSION = "0.1.0"
ENTRY_POINT = SRC_DIR / "bashrunner" / "main.py"


def clean_build_artifacts():
    """Remove previous build artifacts."""
    logger.info("Cleaning previous build artifacts...")
    for directory in [DIST_DIR, BUILD_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            logger.info(f"Removed {directory}")
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        logger.info(f"Removed {SPEC_FILE}")


def build_app():
    """Build the application using PyInstaller."""
    logger.info(f"Building {APP_NAME} v{APP_VERSION}...")

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # No console window (GUI app)
        "--onedir",  # Create a folder with all dependencies
        "--clean",  # Clean cache before building
        # macOS specific options
        "--osx-bundle-identifier", "com.bashrunner.app",
        # Add src to Python path
        f"--paths={SRC_DIR}",
        # Hidden imports for PySide6
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "PySide6.QtWidgets",
        # Hidden imports for loguru
        "--hidden-import", "loguru",
        # Entry point
        str(ENTRY_POINT),
    ]

    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        logger.error("Build failed!")
        sys.exit(1)

    logger.success(f"Build completed successfully!")
    logger.info(f"Application bundle: {DIST_DIR / APP_NAME}")


def main():
    """Main build process."""
    logger.info(f"Starting build process for {APP_NAME}...")

    # Check if PyInstaller is installed
    try:
        subprocess.run(["pyinstaller", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("PyInstaller is not installed!")
        logger.info("Install it with: pip install pyinstaller")
        sys.exit(1)

    # Clean previous builds
    clean_build_artifacts()

    # Build the app
    build_app()

    # Display final info
    logger.info("\n" + "=" * 60)
    logger.info(f"Build complete! Your app is ready:")
    logger.info(f"  Location: {DIST_DIR / APP_NAME}")
    if sys.platform == "darwin":
        logger.info(f"  macOS App: {DIST_DIR / f'{APP_NAME}.app'}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

