#!/usr/bin/env python3
"""
Installation script for the Mental Health Chatbot
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version {sys.version.split()[0]} is compatible.")
    return True

def install_requirements():
    """Install required packages."""
    try:
        print("📦 Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = ".env"
    if os.path.exists(env_file):
        print("✅ .env file already exists.")
        return True
    
    print("🔧 Creating .env file...")
    try:
        with open(env_file, "w") as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("✅ .env file created successfully!")
        print("⚠️  Please edit .env file and add your OpenAI API key.")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported."""
    required_modules = [
        "openai",
        "chromadb",
        "dotenv",
        "langchain",
        "colorama"
    ]
    
    print("🧪 Testing imports...")
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All imports successful!")
    return True

def create_directories():
    """Create necessary directories."""
    directories = ["chroma_db", "documents"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory already exists: {directory}")

def main():
    """Main installation function."""
    print("🤖 Mental Health Chatbot Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Installation failed. Please check the error messages above.")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 50)
    print("🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file and add your OpenAI API key")
    print("2. Run the chatbot: python chatbot.py")
    print("3. Add your mental health documents to the 'documents' folder")
    print("\n📚 For more information, see README.md")
    print("=" * 50)

if __name__ == "__main__":
    main() 