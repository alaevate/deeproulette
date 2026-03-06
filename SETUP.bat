@echo off
color 0A
cls
echo.
echo  =====================================================
echo    DeepRoulette  --  First Time Setup
echo  =====================================================
echo.
echo  This will install all required Python packages.
echo  This only needs to be done ONCE.
echo.
echo  Press any key to continue, or close this window to cancel.
pause > nul

echo.
echo  [Step 1/4] Checking Python installation...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Python was not found on your computer!
    echo.
    echo  Please download and install Python from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During install, check the box that says:
    echo  "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
python --version
echo  Python found!

echo.
echo  [Step 2/4] Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Package installation failed.
    echo  Please make sure you have an internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo  [Step 3/4] Creating required folders...
if not exist "saved_models" mkdir saved_models
if not exist "logs"         mkdir logs
if not exist "data_store"   mkdir data_store

echo.
echo  [Step 4/4] Verifying installation...
python -c "import tensorflow, websockets, numpy, rich; print('  All packages verified!')"
if %errorlevel% neq 0 (
    echo.
    echo  [WARNING] Some packages could not be verified.
    echo  Try running SETUP.bat again.
    echo.
    pause
    exit /b 1
)

echo.
echo  =====================================================
echo    Setup Complete!
echo.
echo    To start the program, double-click START.bat
echo  =====================================================
echo.
pause
