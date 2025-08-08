#!/usr/bin/env python3
"""
Quick start script for the Mental Health Chatbot
"""

import os
import sys
import subprocess

def check_env_file():
    """Check if .env file exists and has API key."""
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("Please run: python install.py")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
        if "your_openai_api_key_here" in content:
            print("❌ Please add your OpenAI API key to the .env file!")
            print("Edit .env file and replace 'your_openai_api_key_here' with your actual API key.")
            return False
    
    return True

def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = [
        ("openai", "openai"),
        ("chromadb", "chromadb"),
        ("python-dotenv", "dotenv"),
        ("langchain", "langchain"),
        ("colorama", "colorama")
    ]
    
    missing_packages = []
    for package, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main function to run the chatbot."""
    print("🤖 Mental Health Chatbot - Quick Start")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    print("✅ All checks passed!")
    print("🚀 Starting chatbot...")
    print("=" * 50)
    
    try:
        # Import and run the chatbot
        from chatbot import main as run_chatbot
        run_chatbot()
    except ImportError as e:
        print(f"❌ Error importing chatbot: {e}")
        print("Please make sure all files are in the correct location.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 