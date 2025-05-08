#!/bin/bash

echo "========================================================"
echo "LLM Customer Service Agent - Installation Script"
echo "========================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.10 or higher and try again."
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the installation script
echo "Running installation script..."
echo
python3 install_requirements.py

echo
echo "========================================================"
echo "Installation process completed."
echo
echo "Next steps:"
echo "1. Configure your API keys in the .env file"
echo "2. Run the application with: uvicorn app.main:app --reload"
echo "3. Explore the API at http://localhost:8000"
echo "========================================================"
echo

# Ask if user wants to test the installation
read -p "Would you like to test the installation now? (y/n): " test_install
if [[ $test_install == "y" || $test_install == "Y" ]]; then
    echo
    echo "Running installation test..."
    echo
    python3 test_installation.py
fi

echo
echo "Press Enter to exit..."
read