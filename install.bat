@echo off
echo ========================================================
echo LLM Customer Service Agent - Installation Script
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.10 or higher and try again.
    echo.
    pause
    exit /b 1
)

:: Run the installation script
echo Running installation script...
echo.
python install_requirements.py

echo.
echo ========================================================
echo Installation process completed.
echo.
echo Next steps:
echo 1. Configure your API keys in the .env file
echo 2. Run the application with: uvicorn app.main:app --reload
echo 3. Explore the API at http://localhost:8000
echo ========================================================
echo.

:: Ask if user wants to test the installation
set /p test_install="Would you like to test the installation now? (y/n): "
if /i "%test_install%"=="y" (
    echo.
    echo Running installation test...
    echo.
    python test_installation.py
)

echo.
echo Press any key to exit...
pause >nul