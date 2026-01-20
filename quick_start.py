#!/usr/bin/env python3
"""
J.A.I Quick Start Script
Sets up test users and provides login credentials
"""

import os
import sys
import subprocess
import asyncio

def print_header():
    print("=" * 60)
    print("🚀 J.A.I Quick Start")
    print("   Setting up test users and login credentials")
    print("=" * 60)
    print()

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        result = subprocess.run(['mongod', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ MongoDB is available")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  MongoDB not detected or not running")
    print("   Please start MongoDB before continuing:")
    print("   - Windows: mongod")
    print("   - Linux/Mac: sudo systemctl start mongod")
    return False

async def setup_test_users():
    """Run the test user creation script"""
    print("🔧 Setting up test users...")
    
    # Change to backend directory
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory '{backend_dir}' not found")
        return False
    
    # Run the test user creation script
    try:
        result = subprocess.run([
            sys.executable, "create_test_users.py"
        ], cwd=backend_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Test users created successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Failed to create test users")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running test user script: {e}")
        return False

def print_quick_access():
    """Print quick access information"""
    print("\n" + "=" * 60)
    print("🎯 QUICK ACCESS")
    print("=" * 60)
    
    print("\n🔑 LOGIN CREDENTIALS:")
    print("-" * 30)
    print("CLIENT LOGIN:")
    print("  Email:    client@test.com")
    print("  Password: password123")
    print()
    print("LAWYER LOGIN:")
    print("  Email:    lawyer@test.com") 
    print("  Password: password123")
    
    print("\n🌐 ACCESS URLS:")
    print("-" * 30)
    print("Client Login:  pages/client-login.html")
    print("Lawyer Login:  pages/lawyer-login.html")
    print("Homepage:      pages/index.html")
    
    print("\n🚀 NEXT STEPS:")
    print("-" * 30)
    print("1. Start the backend server:")
    print("   cd backend")
    print("   python start_server.py")
    print()
    print("2. Open the login pages in your browser")
    print("3. Use the credentials above to login")
    print("4. Explore the dashboards!")
    
    print("\n📚 DOCUMENTATION:")
    print("-" * 30)
    print("Full credentials: TEST_CREDENTIALS.md")
    print("Backend docs:     backend/README.md")
    print("API docs:         http://localhost:8000/docs (when running)")

async def main():
    """Main function"""
    print_header()
    
    # Check MongoDB
    if not check_mongodb():
        print("\n❌ Please start MongoDB and try again.")
        return
    
    # Setup test users
    success = await setup_test_users()
    
    if success:
        print_quick_access()
        print("\n✅ Quick start setup complete!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())