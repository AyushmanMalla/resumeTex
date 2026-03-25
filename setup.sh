#!/usr/bin/env bash
set -e

echo "Starting setup for Resume ATS Optimizer (macOS/Linux)..."

# 1. System Compatibility
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Found Python $PY_VER"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "Python version is compatible (>= 3.9)."
else
    echo "Error: Python 3.9 or higher is required."
    exit 1
fi

# 2. Network Check
echo "Checking network connectivity..."
if ping -c 1 github.com &> /dev/null; then
    echo "Network check passed."
else
    echo "Error: Cannot reach github.com. Check your internet connection."
    exit 1
fi

# 3. Virtual Environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv..."
    python3 -m venv .venv
else
    echo "Virtual environment .venv already exists."
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# 4. Install Dependencies
echo "Installing dependencies from requirements.txt..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Playwright Installation
echo "Checking and installing Playwright browsers (chromium)..."
# playwright install is safe to run multiple times, it skips if already installed
playwright install chromium

echo "Setup complete! Navigate to the directory and activate the environment using:"
echo "source .venv/bin/activate"
