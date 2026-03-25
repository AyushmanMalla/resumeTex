@echo off
setlocal enabledelayedexpansion

echo Starting setup for Resume ATS Optimizer (Windows)...

:: 1. System Compatibility
call python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: python is not installed or not in PATH.
    exit /b 1
)

for /f "tokens=2" %%I in ('python -V 2^>^&1') do set PY_VERSION=%%I
echo Found Python %PY_VERSION%

python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"
if %errorlevel% neq 0 (
    echo Error: Python 3.9 or higher is required.
    exit /b 1
)
echo Python version is compatible (>= 3.9).

:: 2. Bootstrap uv for lightning fast installs
call uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Bootstrapping Astral 'uv'...
    python -m pip install uv
)

:: 3. Virtual Environment
if not exist ".venv\" (
    echo Creating virtual environment using uv...
    uv venv .venv
) else (
    echo Virtual environment .venv already exists.
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: 4. Install Dependencies
echo Installing dependencies blazingly fast with uv...
:: Optimization: use CPU-only PyTorch on Windows to save ~2.5GB of CUDA packages
uv pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

:: 5. Playwright Installation
echo Checking and installing Playwright browsers (chromium)...
playwright install chromium

echo Setup complete! Navigate to the directory and activate the environment using:
echo .venv\Scripts\activate
