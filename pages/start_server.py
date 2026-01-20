#!/usr/bin/env python3
"""
Simple script to start the J.A.I backend server
"""

import subprocess
import sys
import os

def check_requirements():
    """Check if required packages are installed"""
    required_imports = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('motor', 'motor'),
        ('pymongo', 'pymongo'),
        ('python-dotenv', 'dotenv'),
        ('passlib', 'passlib'),
        ('python-jose', 'jose'),
        ('bcrypt', 'bcrypt')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_imports:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def start_server():
    """Start the FastAPI server"""
    if not check_requirements():
        sys.exit(1)
    
    print("Starting J.A.I Backend Server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    start_server()