# BashRunner

A simple PySide6 application for running saved terminal commands and scripts with buttons.

## Features

- **Command Buttons**: Save frequently used terminal commands and run them with a single button click
- **Script Support**: Execute bash scripts or other executable files
- **Multi-Command Support**: Chain multiple commands together to run sequentially
- **Simple UI**: Clean, grid-based interface with command configuration dialog
- **Persistent Storage**: Commands are saved to disk and persist between sessions

## Installation

1. **Using uv (recommended)**:
   ```bash
   uv sync
   ```

2. **Using pip**:
   ```bash
   pip install -e .
   ```

## Usage

Run the application:
```bash
uv run python src/bashrunner/main.py
```

### Main Interface

The main window displays a grid of command buttons. Click any button to execute its associated command.

### Adding Commands

1. Click the **"Commands"** button in the bottom toolbar
2. In the configuration dialog:
   - Click **"Add"** to create a new command
   - Enter a name for the command (displayed on the button)
   - Choose the command type:
     - **Single Command**: Execute one terminal command
     - **Multiple Commands**: Execute multiple commands sequentially (one per line)
     - **Script File**: Execute a script file
   - Enter the command content or select a script file
   - Optionally add a description
   - Click **"Save"** to save the command

### Managing Commands

- **Delete**: Select a command and click **"Delete"**
- **Rearrange**: Use **"Move Up"** and **"Move Down"** buttons
- **Edit**: Select a command to edit its properties

### Settings

Click the **"Settings"** button to configure application preferences (currently includes button grid columns).

## Command Types

### Single Command
Execute a single terminal command:
```bash
ls -la
git status
python script.py
```

### Multiple Commands
Execute multiple commands in sequence:
```bash
cd /path/to/project
git pull
npm install
npm run build
```

### Script File
Execute any executable script file (bash, python, etc.):
- `/path/to/script.sh`
- `./build.py`
- `C:\path\to\script.bat`

## Development

This project uses:
- **PySide6** for the GUI
- **uv** for package management
- **loguru** for logging
- **pytest** and **pytest-qt** for testing

## Project Structure

```
src/bashrunner/
├── main.py                 # Application entry point
├── gui/
│   ├── main_window.py      # Main application window
│   ├── commands_config.py  # Command configuration dialog
│   └── settings_dialog.py  # Settings dialog
└── core/
    └── command_storage.py  # Command storage and execution
```

## License

MIT License
