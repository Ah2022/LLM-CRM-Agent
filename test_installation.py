"""
Test script to verify that the LLM Customer Service Agent installation is working correctly.
This script attempts to import and initialize key components of the system.
"""

import os
import sys

def test_imports():
    """Test importing key modules from the project"""
    print("Testing imports...")
    
    # List of modules to test
    modules_to_test = [
        "app.agent",
        "app.config",
        "app.tools.summarizer",
        "app.tools.crm_entry",
        "app.tools.ticket_router",
        "app.services.email",
        "app.services.crm",
        "app.services.tickets"
    ]
    
    # Try importing each module
    success_count = 0
    for module_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=["*"])
            print(f"✅ Successfully imported {module_name}")
            success_count += 1
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {e}")
    
    # Print summary
    print(f"\nSuccessfully imported {success_count} out of {len(modules_to_test)} modules.")
    return success_count == len(modules_to_test)

def test_initialization():
    """Test initializing key components"""
    print("\nTesting component initialization...")
    
    try:
        # Only attempt this if imports succeeded
        from app.config import settings
        print(f"✅ Loaded configuration settings")
        
        # Test initializing the email summarizer
        from app.tools.summarizer import EmailSummarizer
        # Use a mock LLM to avoid API calls
        summarizer = EmailSummarizer(None)
        print(f"✅ Initialized EmailSummarizer")
        
        # Test initializing the ticket router
        from app.tools.ticket_router import TicketRouter
        router = TicketRouter(None)
        print(f"✅ Initialized TicketRouter")
        
        return True
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return False

def check_path():
    """Check if the project directory is in the Python path"""
    print("\nChecking Python path...")
    
    # Get the absolute path of the project directory
    project_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Check if it's in sys.path
    if project_dir in sys.path:
        print(f"✅ Project directory is in Python path: {project_dir}")
        return True
    else:
        print(f"❌ Project directory is NOT in Python path")
        print(f"Current path includes:")
        for path in sys.path:
            print(f"  - {path}")
        return False

def main():
    """Main function to run the tests"""
    print("=" * 60)
    print("LLM Customer Service Agent - Installation Test")
    print("=" * 60)
    
    # Add the current directory to the path for testing
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Run tests
    path_ok = check_path()
    imports_ok = test_imports()
    init_ok = test_initialization() if imports_ok else False
    
    # Print summary
    print("\n" + "=" * 60)
    if path_ok and imports_ok and init_ok:
        print("✅ All tests passed! The installation is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
        if not path_ok:
            print("\nSuggestion: Run the install_requirements.py script to add the project to your Python path.")
        
        if not imports_ok:
            print("\nSuggestion: Make sure all required packages are installed:")
            print("  python -m pip install -r requirements.txt")
    
    print("=" * 60)

if __name__ == "__main__":
    main()