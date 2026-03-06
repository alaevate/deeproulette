@echo off
color 0A
cls
python main.py
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] The program encountered an error.
    echo.
    echo  If this is your first time running the program,
    echo  please run SETUP.bat first to install dependencies.
    echo.
)
pause
