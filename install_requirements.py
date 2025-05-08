import subprocess
import sys
import os
import site
from pathlib import Path

def install_requirements():
    """Install packages from requirements.txt"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def add_to_path():
    """Add the project directory to Python path"""
    print("Adding project directory to Python path...")
    try:
        # Get the current directory (project root)
        project_dir = os.path.abspath(os.path.dirname(__file__))
        
        # Create or append to .pth file in site-packages
        site_packages_dir = site.getsitepackages()[0]
        pth_file = os.path.join(site_packages_dir, "llm_customer_service.pth")
        
        with open(pth_file, "w") as f:
            f.write(project_dir)
        
        print(f"✅ Added project directory to Python path: {project_dir}")
        print(f"✅ Created .pth file at: {pth_file}")
    except Exception as e:
        print(f"❌ Error adding to path: {e}")
        return False
    return True

def verify_installation():
    """Verify that key packages can be imported"""
    print("Verifying installation...")
    packages_to_check = [
        "fastapi", "uvicorn", "pydantic", "langchain", "openai", 
        "chromadb", "aiohttp", "asyncio", "pytest", "loguru"
    ]
    
    all_successful = True
    for package in packages_to_check:
        try:
            __import__(package)
            print(f"✅ Successfully imported {package}")
        except ImportError as e:
            print(f"❌ Failed to import {package}: {e}")
            all_successful = False
    
    return all_successful

def main():
    """Main function to run the installation process"""
    print("=" * 60)
    print("LLM Customer Service Agent - Package Installation")
    print("=" * 60)
    
    # Step 1: Install requirements
    if not install_requirements():
        print("Installation failed at package installation step.")
        return
    
    print("\n")
    
    # Step 2: Add to path
    if not add_to_path():
        print("Installation failed at adding to path step.")
        return
    
    print("\n")
    
    # Step 3: Verify installation
    if not verify_installation():
        print("Some packages could not be imported. Please check the errors above.")
    else:
        print("\n" + "=" * 60)
        print("✅ Installation completed successfully!")
        print("=" * 60)
        print("\nYou can now import modules from the LLM Customer Service Agent project.")
        print("Example usage:")
        print("  from app.agent import CustomerServiceAgent")
        print("  from app.tools.summarizer import EmailSummarizer")

if __name__ == "__main__":
    main()