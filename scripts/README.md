# Build Scripts

This directory contains scripts for packaging the BashRunner application.

## Prerequisites

Install PyInstaller:
```bash
pip install pyinstaller
# or with uv:
uv pip install pyinstaller
```

## Building the Application

### Option 1: Using the Python script (recommended)
```bash
python3 scripts/build_app.py
```

### Option 2: Using the bash wrapper
```bash
./scripts/build.sh
```

## Output

The built application will be in the `dist/` directory:
- **macOS**: `dist/BashRunner.app` - Double-click to run
- **Linux**: `dist/BashRunner/` - Run the `BashRunner` executable
- **Windows**: `dist/BashRunner/` - Run `BashRunner.exe`

## Build Options

The build script uses the following PyInstaller options:
- `--windowed`: No console window (GUI mode)
- `--onedir`: Creates a directory with all dependencies
- `--clean`: Cleans cache before building for a fresh build

## Customization

To customize the build, edit `scripts/build_app.py`:
- Change app metadata (name, version, bundle ID)
- Add additional hidden imports
- Include data files or resources
- Modify PyInstaller options

## Troubleshooting

**Build fails with missing modules:**
- Add them to the `--hidden-import` list in `build_app.py`

**App won't run:**
- Check the console output for errors
- Try running with `--debug all` flag in PyInstaller command
- Make sure all dependencies are installed

**App is too large:**
- Consider using `--onefile` instead of `--onedir` (single executable)
- Exclude unnecessary packages with `--exclude-module`

