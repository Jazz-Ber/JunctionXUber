#!/usr/bin/env python3
"""
Dependency Installation Script for JunctionX-Uber Project

This script automatically installs all required Python packages for the project.
Run this script to ensure all dependencies are properly installed.

Usage:
    python install_dependencies.py
"""

import subprocess
import sys
import os
from pathlib import Path

def check_pip_available():
    """Check if pip is available and working."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def install_requirements():
    """Install packages from requirements.txt file."""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("Error: requirements.txt file not found!")
        print("Make sure you're running this script from the project root directory.")
        return False
    
    print("Installing required packages from requirements.txt...")
    print("=" * 50)
    
    try:
        # Upgrade pip first to ensure we have the latest version
        print("Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        
        # Install requirements
        print("Installing project dependencies...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              check=True, capture_output=True, text=True)
        
        print("All dependencies installed successfully!")
        print("\nInstalled packages:")
        print("- tkintermapview (for map functionality)")
        print("- pillow (for image processing)")
        print("- requests (for HTTP requests)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("Error installing dependencies!")
        print(f"Error details: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    """Main function to handle the installation process."""
    print("Dependency Installer")
    print("=" * 50)
    
    # Check if pip is available
    if not check_pip_available():
        print("Error: pip is not available!")
        print("Please ensure Python and pip are properly installed.")
        print("You can install pip by running: python -m ensurepip --upgrade")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("Error: requirements.txt not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Install dependencies
    if install_requirements():
        print("\nSetup complete! You can now run the main application.")
        print("To start the application, run: python main.py")
    else:
        print("\nSetup failed! Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
