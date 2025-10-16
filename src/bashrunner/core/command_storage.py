"""Command storage and management system."""

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


@dataclass
class Command:
    """Represents a single command or script."""

    name: str
    command_type: str  # 'single', 'multi', or 'script'
    content: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Command":
        """Create from dictionary."""
        return cls(**data)


class CommandStorage:
    """Manages command storage and persistence."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize command storage.

        Args:
            storage_path: Path to store commands. Defaults to app data directory.
        """
        if storage_path is None:
            storage_path = self._get_default_storage_path()

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.commands_file = self.storage_path / "commands.json"
        self._commands: List[Command] = []
        self._load_commands()

    def _get_default_storage_path(self) -> Path:
        """Get the default storage path based on platform."""
        if sys.platform == "win32":
            return Path.home() / "AppData" / "Roaming" / "BashRunner"
        elif sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "BashRunner"
        else:
            return Path.home() / ".config" / "bashrunner"

    def _load_commands(self) -> None:
        """Load commands from storage file."""
        if self.commands_file.exists():
            try:
                with open(self.commands_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self._commands = [Command.from_dict(cmd) for cmd in data.get("commands", [])]
                logger.info(f"Loaded {len(self._commands)} commands from storage")
            except Exception as e:
                logger.error(f"Failed to load commands: {e}")
                self._commands = []
        else:
            logger.info("No existing commands file found, starting fresh")
            self._commands = []

    def _save_commands(self) -> None:
        """Save commands to storage file."""
        try:
            data = {"commands": [cmd.to_dict() for cmd in self._commands]}
            with open(self.commands_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self._commands)} commands to storage")
        except Exception as e:
            logger.error(f"Failed to save commands: {e}")

    def get_commands(self) -> List[Command]:
        """Get all commands."""
        return self._commands.copy()

    def add_command(self, command: Command) -> None:
        """Add a new command."""
        self._commands.append(command)
        self._save_commands()
        logger.info(f"Added command: {command.name}")

    def update_command(self, index: int, command: Command) -> bool:
        """Update a command at the given index.

        Returns:
            True if update was successful, False otherwise.
        """
        if 0 <= index < len(self._commands):
            self._commands[index] = command
            self._save_commands()
            logger.info(f"Updated command at index {index}: {command.name}")
            return True
        else:
            logger.error(f"Invalid command index: {index}")
            return False

    def delete_command(self, index: int) -> bool:
        """Delete a command at the given index.

        Returns:
            True if deletion was successful, False otherwise.
        """
        if 0 <= index < len(self._commands):
            deleted = self._commands.pop(index)
            self._save_commands()
            logger.info(f"Deleted command: {deleted.name}")
            return True
        else:
            logger.error(f"Invalid command index: {index}")
            return False

    def move_command(self, from_index: int, to_index: int) -> bool:
        """Move a command from one index to another.

        Returns:
            True if move was successful, False otherwise.
        """
        if 0 <= from_index < len(self._commands) and 0 <= to_index < len(self._commands):
            command = self._commands.pop(from_index)
            self._commands.insert(to_index, command)
            self._save_commands()
            logger.info(f"Moved command from index {from_index} to {to_index}")
            return True
        else:
            logger.error(f"Invalid move indices: {from_index} -> {to_index}")
            return False

    def execute_command(self, index: int) -> bool:
        """Execute a command at the given index.

        Returns:
            True if execution was successful, False otherwise.
        """
        if not (0 <= index < len(self._commands)):
            logger.error(f"Invalid command index: {index}")
            return False

        command = self._commands[index]
        try:
            if command.command_type == "single":
                return self._execute_single_command(command.content, command.name)
            elif command.command_type == "multi":
                return self._execute_multi_commands(command.content, command.name)
            elif command.command_type == "script":
                return self._execute_script(command.content, command.name)
            else:
                logger.error(f"Unknown command type: {command.command_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to execute command '{command.name}': {e}")
            return False

    def _execute_single_command(self, command: str, name: str) -> bool:
        """Execute a single shell command."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                logger.info(f"Command '{name}' executed successfully")
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"Command '{name}' failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"Error: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Exception executing command '{name}': {e}")
            return False

    def _execute_multi_commands(self, commands_text: str, name: str) -> bool:
        """Execute multiple shell commands separated by newlines."""
        try:
            commands = [cmd.strip() for cmd in commands_text.split("\n") if cmd.strip()]
            for command in commands:
                logger.info(f"Executing: {command}")
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True, check=False
                )
                if result.returncode != 0:
                    logger.error(f"Command failed: {command}")
                    if result.stderr:
                        logger.error(f"Error: {result.stderr}")
                    return False
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
            logger.info(f"All commands in '{name}' executed successfully")
            return True
        except Exception as e:
            logger.error(f"Exception executing multi commands '{name}': {e}")
            return False

    def _execute_script(self, script_path: str, name: str) -> bool:
        """Execute a script file."""
        try:
            script_file = Path(script_path)
            if not script_file.exists():
                logger.error(f"Script file does not exist: {script_path}")
                return False

            result = subprocess.run(
                [str(script_file)], shell=True, capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                logger.info(f"Script '{name}' executed successfully")
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"Script '{name}' failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"Error: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Exception executing script '{name}': {e}")
            return False


def create_command_storage(storage_path: Optional[Path] = None) -> CommandStorage:
    """Factory function to create a CommandStorage instance."""
    return CommandStorage(storage_path)
