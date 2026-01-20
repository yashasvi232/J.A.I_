#!/usr/bin/env python3
"""
J.A.I Project Setup Script
Helps set up the complete J.A.I legal platform
"""

import os
import subprocess
import sys
import platform

def print_header():
    print("=" * 60)
    print("🏛️  J.A.I (Jurist Artificial Intelligence) Setup")
    print("   AI-Powered Legal Platform")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_mongodb():
    """Check if MongoDB is available"""
    try:
        result = subprocess.run(['mongod', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ MongoDB is installed")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  MongoDB not detected")
    print("   Please install MongoDB:")
    if platform.system() == "Windows":
        print("   - Download from: https://www.mongodb.com/try/download/community")
    elif platform.system() == "Darwin":  # macOS
        print("   - brew install mongodb-community")
    else:  # Linux
        print("   - sudo apt-get install mongodb (Ubuntu/Debian)")
        print("   - sudo yum install mongodb (CentOS/RHEL)")
    
    return False

def setup_backend():
    """Set up the backend environment"""
    print("\n🔧 Setting up Backend...")
    
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory '{backend_dir}' not found")
        return False
    
    os.chdir(backend_dir)
    
    # Create virtual environment
    print("   Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("   ✅ Virtual environment created")
    except subprocess.CalledProcessError:
        print("   ❌ Failed to create virtual environment")
        return False
    
    # Determine activation script
    if platform.system() == "Windows":
        activate_script = os.path.join("venv", "Scripts", "activate")
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:
        activate_script = os.path.join("venv", "bin", "activate")
        pip_path = os.path.join("venv", "bin", "pip")
    
    # Install requirements
    print("   Installing Python packages...")
    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("   ✅ Backend dependencies installed")
    except subprocess.CalledProcessError:
        print("   ❌ Failed to install dependencies")
        return False
    
    # Set up environment file
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("   ✅ Environment file created from template")
        else:
            # Create basic .env file
            with open(".env", "w") as f:
                f.write("""# Database Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=jai_database

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
""")
            print("   ✅ Basic environment file created")
    else:
        print("   ✅ Environment file already exists")
    
    os.chdir("..")
    return True

def setup_frontend():
    """Set up the frontend"""
    print("\n🎨 Setting up Frontend...")
    
    pages_dir = "pages"
    if not os.path.exists(pages_dir):
        print(f"❌ Frontend directory '{pages_dir}' not found")
        return False
    
    print("   ✅ Frontend files detected")
    print("   ✅ No additional setup required for frontend")
    return True

def print_instructions():
    """Print final setup instructions"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    
    print("\n📋 Next Steps:")
    print("\n1. Start MongoDB:")
    if platform.system() == "Windows":
        print("   mongod")
    else:
        print("   sudo systemctl start mongod  # Linux")
        print("   brew services start mongodb-community  # macOS")
    
    print("\n2. Start the Backend API:")
    print("   cd backend")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("   python start_server.py")
    print("   # Or: uvicorn main:app --reload")
    
    print("\n3. Open Frontend:")
    print("   Open pages/index.html in your browser")
    print("   Or use a local server:")
    print("   python -m http.server 5500")
    
    print("\n🌐 URLs:")
    print("   Frontend: http://localhost:5500")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    print("\n👥 Test Accounts:")
    print("   Create accounts through the registration forms")
    print("   - Client: Use client-login.html")
    print("   - Lawyer: Use lawyer-login.html")
    
    print("\n📚 Documentation:")
    print("   - Backend: backend/README.md")
    print("   - API Docs: http://localhost:8000/docs (when running)")

def main():
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    mongodb_available = check_mongodb()
    
    # Setup components
    backend_success = setup_backend()
    frontend_success = setup_frontend()
    
    if backend_success and frontend_success:
        print_instructions()
        
        if not mongodb_available:
            print("\n⚠️  Warning: MongoDB not detected.")
            print("   Please install and start MongoDB before running the backend.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()