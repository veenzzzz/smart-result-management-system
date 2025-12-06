#!/usr/bin/env python3
"""
Windows-compatible launcher for the Result Management System
This script handles Unicode encoding issues on Windows
"""

import sys
import os
import codecs

# Set console encoding to UTF-8 for Windows
if sys.platform == "win32":
    # Enable UTF-8 mode for Windows console
    os.system("chcp 65001 > nul")
    
    # Set stdout and stderr to UTF-8
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
try:
    from main import main
    main()
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to exit...")


