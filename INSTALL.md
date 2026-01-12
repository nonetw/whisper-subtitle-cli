# Installation Guide

This guide will walk you through installing `whisper-subtitle-cli` step by step, even if you're new to Python or command-line tools.

## Prerequisites

You'll need to install three things before using this tool:
1. **Python** (version 3.11 or 3.12)
2. **Poetry** (Python package manager)
3. **ffmpeg** (audio/video processing tool)

---

## Step 1: Install Python

### Check if Python is already installed

Open your terminal (macOS/Linux) or Command Prompt (Windows) and run:

```bash
python3 --version
```

If you see `Python 3.11.x` or `Python 3.12.x`, you're good! Skip to Step 2.

### Install Python if needed

#### macOS

**Option A: Using Homebrew (recommended)**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.12
```

**Option B: Download from python.org**
1. Visit https://www.python.org/downloads/
2. Download Python 3.12 for macOS
3. Run the installer and follow the instructions

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

#### Linux (Fedora)

```bash
sudo dnf install python3.12
```

#### Windows

1. Visit https://www.python.org/downloads/
2. Download Python 3.12 for Windows
3. **Important**: During installation, check "Add Python to PATH"
4. Run the installer

---

## Step 2: Install Poetry

Poetry is a tool that manages Python dependencies. Think of it like a package manager for your Python projects.

### Install Poetry

#### macOS/Linux

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

After installation, you may need to add Poetry to your PATH. The installer will show you instructions like:

```bash
export PATH="/Users/yourusername/.local/bin:$PATH"
```

Add this line to your shell configuration file (`~/.zshrc` for macOS or `~/.bashrc` for Linux).

#### Windows (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### Verify Poetry installation

```bash
poetry --version
```

You should see something like `Poetry (version 1.7.0)`.

**Troubleshooting**: If `poetry` command is not found:
- Close and reopen your terminal
- Make sure you added Poetry to your PATH (see above)
- On Windows, you may need to restart your computer

---

## Step 3: Install ffmpeg

ffmpeg is a powerful tool for processing audio and video files.

### macOS

```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg
```

### Linux (Fedora)

```bash
sudo dnf install ffmpeg
```

### Windows

**Option A: Using Chocolatey (recommended)**
```bash
# Install Chocolatey first (if you don't have it)
# Visit https://chocolatey.org/install for instructions

# Then install ffmpeg
choco install ffmpeg
```

**Option B: Manual installation**
1. Visit https://ffmpeg.org/download.html
2. Download the Windows build
3. Extract to `C:\ffmpeg`
4. Add `C:\ffmpeg\bin` to your system PATH

### Verify ffmpeg installation

```bash
ffmpeg -version
```

You should see version information for ffmpeg.

---

## Step 4: Download the Project

### Option A: Using Git (if you have it)

```bash
# Clone the repository
git clone https://github.com/yourusername/whisper-subtitle-cli.git

# Navigate into the project directory
cd whisper-subtitle-cli
```

### Option B: Download ZIP

1. Go to the GitHub repository page
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file
5. Open terminal and navigate to the extracted folder:
   ```bash
   cd path/to/whisper-subtitle-cli
   ```

---

## Step 5: Install Project Dependencies

Now we'll use Poetry to install all the required Python packages.

### Install dependencies

From inside the project directory, run:

```bash
poetry install --no-root
```

This will:
- Create a virtual environment (isolated Python environment for this project)
- Download and install all required packages
- Take a few minutes, especially for the Whisper AI models

**Note**: The first time you run the actual tool, it will download the AI model (1.5GB for the default `medium` model), so expect a longer first run.

---

## Step 6: Verify Installation

Let's make sure everything works!

```bash
python main.py --help
```

You should see the help message with usage instructions. If you see this, congratulations! 🎉

---

## Quick Start

Now you're ready to use the tool!

### Test with a video file

```bash
python main.py your-video.mp4
```

### Test with a YouTube URL

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

---

## Common Issues

### "python: command not found"

Try using `python3` instead:
```bash
python3 main.py video.mp4
```

### "poetry: command not found"

Poetry is not in your PATH. See Step 2 for instructions on adding it.

### "ffmpeg: command not found"

ffmpeg is not installed or not in your PATH. See Step 3.

### "ModuleNotFoundError: No module named 'src'"

Make sure you're running the command from the project root directory (the folder containing `main.py`).

### Virtual environment issues

If you have issues with Poetry's virtual environment, you can create one manually:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies without Poetry
pip install faster-whisper ffmpeg-python click yt-dlp
```

### Slow download speeds

If Poetry is downloading packages very slowly, you can try using a mirror or check your internet connection.

---

## Updating the Project

If you want to update to the latest version:

```bash
# If using Git
git pull

# Reinstall dependencies
poetry install --no-root
```

---

## Getting Help

If you run into issues:

1. Check the [README.md](README.md) for usage examples
2. Check the [Troubleshooting section](#common-issues) above
3. Open an issue on GitHub with:
   - Your operating system
   - Python version (`python3 --version`)
   - Poetry version (`poetry --version`)
   - The full error message

---

## Next Steps

Once installed, check out the [README.md](README.md) for:
- Usage examples
- Advanced options
- Model selection guide
- Language codes
