#!/usr/bin/env python3
"""
BeatBridge Backend Initialization Script

This script initializes the backend directory structure and creates placeholder files.
"""

import os
import sys
import shutil
from pathlib import Path

# Define directory structure
DIRECTORIES = [
    "models",
    "services",
    "utils",
    "logs",
    "keys"
]

# Define placeholder files for each directory
PLACEHOLDER_FILES = {
    "keys": [".gitkeep"],
    "logs": [".gitkeep"]
}

def create_directory_structure():
    """Create the directory structure for the backend."""
    print("Creating directory structure...")
    
    # Get the current directory
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Create directories
    for directory in DIRECTORIES:
        dir_path = current_dir / directory
        if not dir_path.exists():
            print(f"Creating directory: {directory}")
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py in Python module directories
        if directory in ["models", "services", "utils"]:
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                print(f"Creating: {directory}/__init__.py")
                with open(init_file, "w") as f:
                    f.write(f'"""\nBeatBridge {directory.capitalize()} Package\n"""\n')
        
        # Create placeholder files
        if directory in PLACEHOLDER_FILES:
            for filename in PLACEHOLDER_FILES[directory]:
                file_path = dir_path / filename
                if not file_path.exists():
                    print(f"Creating: {directory}/{filename}")
                    with open(file_path, "w") as f:
                        f.write("")

def check_requirements():
    """Check if the required files and directories exist."""
    print("Checking requirements...")
    
    missing_files = []
    
    # Check for key files
    required_files = [
        "service.py",
        "config.py",
        "requirements.txt",
        "models/track.py",
        "models/playlist.py",
        "services/spotify.py",
        "services/apple_music.py",
        "services/youtube_music.py",
        "utils/auth.py",
        "utils/matching.py",
        "utils/logging.py"
    ]
    
    for file_path in required_files:
        full_path = Path(os.path.dirname(os.path.abspath(__file__))) / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("\nWarning: The following required files are missing:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\nPlease make sure these files are created before running the service.")
    else:
        print("All required files are present.")

def create_gitignore():
    """Create a .gitignore file for the backend directory."""
    print("Creating .gitignore file...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# Logs
logs/*
!logs/.gitkeep

# Keys
keys/*
!keys/.gitkeep

# Environment variables
.env
.env.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# Redis
dump.rdb
"""
    
    gitignore_path = Path(os.path.dirname(os.path.abspath(__file__))) / ".gitignore"
    if not gitignore_path.exists():
        print("Creating: .gitignore")
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content)

def main():
    """Main function."""
    print("Initializing BeatBridge Backend...")
    
    create_directory_structure()
    create_gitignore()
    check_requirements()
    
    print("\nInitialization complete!")
    print("Remember to set up your environment variables and API keys.")

if __name__ == "__main__":
    main()