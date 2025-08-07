#!/usr/bin/env python3
"""
Development setup script for the AI-Driven Reverse Job Search Engine.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Set up the development environment."""
    print("🚀 Setting up AI-Driven Reverse Job Search Engine development environment...")
    
    # Check if Python 3.9+ is available
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Create virtual environment
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        sys.exit(1)
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Create necessary directories
    directories = [
        "logs",
        "data/raw/resumes",
        "data/processed",
        "data/models",
        "notebooks"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Copy environment file
    if not Path(".env").exists():
        if Path("env.example").exists():
            import shutil
            shutil.copy("env.example", ".env")
            print("✅ Created .env file from env.example")
            print("⚠️  Please edit .env file with your configuration")
        else:
            print("⚠️  No env.example file found. Please create .env file manually")
    
    # Initialize database
    if not run_command(f"{python_cmd} scripts/setup_database.py", "Initializing database"):
        print("⚠️  Database initialization failed. You can run it manually later")
    
    # Run basic tests
    if not run_command(f"{python_cmd} -m pytest tests/test_basic.py -v", "Running basic tests"):
        print("⚠️  Some tests failed. Check the output above")
    
    print("\n🎉 Development environment setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run the application: python run.py")
    print("3. Access the API documentation: http://localhost:8000/docs")
    print("4. Start developing in the notebooks/ directory")

if __name__ == "__main__":
    main()
