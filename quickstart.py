#!/usr/bin/env python3
"""Quick start script for Salesforce Identity Validator"""
import os
import sys
import subprocess
from pathlib import Path


def main():
    """Quick start"""
    print("""
╔════════════════════════════════════════════════════════╗
║   Salesforce Identity Validator - Quick Start         ║
╚════════════════════════════════════════════════════════╝
""")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("✗ Python 3.11+ required")
        return 1
    
    print(f"✓ Python {sys.version}")
    
    # Create .env from template
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("\nCreating .env file...")
        with open(env_example) as f_in:
            with open(env_file, "w") as f_out:
                f_out.write(f_in.read())
        print("✓ .env file created")
        print("⚠ Please edit .env and add your Azure credentials")
    
    # Install dependencies
    print("\nInstalling dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return 1
    
    # Run tests
    print("\nRunning tests...")
    try:
        subprocess.run(["pytest", "tests/", "-v"], check=False)
        print("✓ Tests completed")
    except FileNotFoundError:
        print("⚠ pytest not found, skipping tests")
    
    print("""
✓ Setup completed successfully!

Next steps:

1. Edit .env with your Azure credentials
2. Start the server:
   python main.py

3. Visit the API documentation:
   http://localhost:8000/docs

4. Test the API:
   python test_api.py
""")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
