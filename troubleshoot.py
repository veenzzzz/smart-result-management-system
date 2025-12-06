#!/usr/bin/env python3
"""
ResultHub Troubleshooting Script
Diagnoses and fixes common issues
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python():
    """Check Python installation"""
    print("🐍 Checking Python...")
    try:
        version = sys.version_info
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("   ⚠️  Python 3.8+ recommended")
        return True
    except Exception as e:
        print(f"   ❌ Python error: {e}")
        return False

def check_node():
    """Check Node.js installation"""
    print("📦 Checking Node.js...")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Node.js {result.stdout.strip()}")
            return True
        else:
            print("   ❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("   ❌ Node.js not installed")
        print("   💡 Download from: https://nodejs.org/")
        return False

def check_directories():
    """Check project structure"""
    print("📁 Checking project structure...")
    required_dirs = ["backend", "frontend", "database", "modules", "utils"]
    missing = []
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ missing")
            missing.append(dir_name)
    
    return len(missing) == 0

def check_backend_deps():
    """Check backend dependencies"""
    print("🔧 Checking backend dependencies...")
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("   ❌ Backend directory not found")
        return False
    
    try:
        # Check if requirements.txt exists
        req_file = backend_dir / "requirements.txt"
        if not req_file.exists():
            print("   ❌ requirements.txt not found")
            return False
        
        print("   ✅ requirements.txt found")
        
        # Try to import Flask
        try:
            import flask
            print("   ✅ Flask installed")
        except ImportError:
            print("   ❌ Flask not installed")
            print("   💡 Run: cd backend && pip install -r requirements.txt")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_frontend_deps():
    """Check frontend dependencies"""
    print("🎨 Checking frontend dependencies...")
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("   ❌ Frontend directory not found")
        return False
    
    try:
        # Check if package.json exists
        pkg_file = frontend_dir / "package.json"
        if not pkg_file.exists():
            print("   ❌ package.json not found")
            return False
        
        print("   ✅ package.json found")
        
        # Check if node_modules exists
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            print("   ❌ node_modules not found")
            print("   💡 Run: cd frontend && npm install")
            return False
        
        print("   ✅ node_modules found")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_ports():
    """Check if ports are available"""
    print("🌐 Checking ports...")
    import socket
    
    ports = [3000, 5000]
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"   ⚠️  Port {port} is in use")
        else:
            print(f"   ✅ Port {port} is available")

def fix_issues():
    """Attempt to fix common issues"""
    print("\n🔧 Attempting to fix issues...")
    
    # Install backend dependencies
    print("📦 Installing backend dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], 
                      check=True, capture_output=True)
        print("   ✅ Backend dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install backend dependencies: {e}")
    
    # Install frontend dependencies
    print("📦 Installing frontend dependencies...")
    try:
        subprocess.run(["npm", "install"], cwd="frontend", check=True, capture_output=True)
        print("   ✅ Frontend dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install frontend dependencies: {e}")
    
    # Install root dependencies
    print("📦 Installing root dependencies...")
    try:
        subprocess.run(["npm", "install"], check=True, capture_output=True)
        print("   ✅ Root dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install root dependencies: {e}")

def main():
    """Main troubleshooting function"""
    print("🔍 ResultHub Troubleshooting")
    print("=" * 40)
    
    issues = []
    
    # Run all checks
    if not check_python():
        issues.append("Python installation")
    
    if not check_node():
        issues.append("Node.js installation")
    
    if not check_directories():
        issues.append("Project structure")
    
    if not check_backend_deps():
        issues.append("Backend dependencies")
    
    if not check_frontend_deps():
        issues.append("Frontend dependencies")
    
    check_ports()
    
    # Summary
    print("\n📋 Summary:")
    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   • {issue}")
        
        print("\n🔧 Attempting to fix issues...")
        fix_issues()
        
        print("\n💡 Manual fixes:")
        print("   1. Install Python: https://python.org/")
        print("   2. Install Node.js: https://nodejs.org/")
        print("   3. Run: npm run install-all")
        print("   4. Run: npm run dev")
    else:
        print("✅ All checks passed!")
        print("🚀 Ready to start: npm run dev")

if __name__ == "__main__":
    main()


