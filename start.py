#!/usr/bin/env python3
"""
ResultHub Startup Script
Starts both frontend and backend servers
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

def run_backend():
    """Start the Flask backend server"""
    print("🚀 Starting ResultHub Backend...")
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    try:
        # Install backend dependencies if needed
        print("📦 Installing backend dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # Start Flask server
        print("🌐 Starting Flask API server on http://localhost:5000")
        subprocess.run([sys.executable, "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")

def run_frontend():
    """Start the React frontend server"""
    print("🎨 Starting ResultHub Frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    try:
        # Install frontend dependencies if needed
        print("📦 Installing frontend dependencies...")
        subprocess.run(["npm", "install"], check=True)
        
        # Start Vite dev server
        print("🌐 Starting React dev server on http://localhost:3000")
        subprocess.run(["npm", "run", "dev"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")

def main():
    """Main startup function"""
    print("🎓 ResultHub Smart Result Management System")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Make sure you have both 'backend' and 'frontend' folders")
        sys.exit(1)
    
    print("🔧 Starting both servers...")
    print("   Backend:  http://localhost:5000")
    print("   Frontend: http://localhost:3000")
    print("   Press Ctrl+C to stop both servers")
    print("=" * 50)
    
    try:
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start frontend in the main thread
        run_frontend()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down ResultHub...")
        print("✅ Goodbye!")

if __name__ == "__main__":
    main()


