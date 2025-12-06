# 🔧 Fix Terminal Issues - ResultHub

## 🚨 Common Issues & Solutions

### Issue 1: PowerShell Execution Policy Error
**Error**: `npm : File C:\Program Files\nodejs\npm.ps1 cannot be loaded because running scripts is disabled`

**Solution**:
```powershell
# Run this command in PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Node.js/npm Not Found
**Error**: `'npm' is not recognized as the name of a cmdlet, function, script file`

**Solution**:
1. Download and install Node.js from https://nodejs.org/
2. Restart your terminal/PowerShell
3. Verify installation: `node --version` and `npm --version`

### Issue 3: Python Not Found
**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Download and install Python from https://python.org/
2. Make sure to check "Add Python to PATH" during installation
3. Restart your terminal/PowerShell
4. Verify installation: `python --version`

### Issue 4: Port Already in Use
**Error**: `Port 3000 is already in use` or `Port 5000 is already in use`

**Solution**:
```bash
# Kill processes using these ports
npx kill-port 3000 5000

# Or find and kill manually
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F
```

### Issue 5: Module Import Errors
**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### Issue 6: Frontend Dependencies Not Found
**Error**: `Cannot find module 'react'`

**Solution**:
```bash
# Install frontend dependencies
cd frontend
npm install
cd ..
```

## 🚀 Quick Fix Commands

### Option 1: Use the Batch File (Recommended for Windows)
```bash
# Double-click start.bat or run in Command Prompt
start.bat
```

### Option 2: Use PowerShell Script
```powershell
# Run in PowerShell
.\start-windows.ps1
```

### Option 3: Manual Setup
```bash
# 1. Fix PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Install all dependencies
npm run install-all

# 3. Start both servers
npm run dev
```

## 🔍 Step-by-Step Troubleshooting

### Step 1: Check Prerequisites
```bash
# Check Node.js
node --version
# Should show: v18.x.x or higher

# Check npm
npm --version
# Should show: 9.x.x or higher

# Check Python
python --version
# Should show: Python 3.8.x or higher
```

### Step 2: Fix PowerShell Issues
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify
Get-ExecutionPolicy
# Should show: RemoteSigned
```

### Step 3: Install Dependencies
```bash
# Install root dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Step 4: Start Servers
```bash
# Start both servers
npm run dev
```

## 🎯 Success Indicators

✅ **Node.js installed**: `node --version` shows version
✅ **Python installed**: `python --version` shows version  
✅ **Dependencies installed**: No "module not found" errors
✅ **Ports available**: 3000 and 5000 are free
✅ **Servers start**: Both frontend and backend start without errors
✅ **Browser access**: http://localhost:3000 loads the login page

## 🆘 If Nothing Works

### Alternative Method 1: Manual Start
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend (new terminal)
cd frontend
npm run dev
```

### Alternative Method 2: Use Different Ports
```bash
# If ports 3000/5000 are busy, change them:

# In frontend/vite.config.ts
server: {
  port: 3001,  # Change from 3000
}

# In backend/app.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Change from 5000
```

### Alternative Method 3: Use Different Terminal
```bash
# Try Command Prompt instead of PowerShell
cmd
start.bat
```

## 📞 Still Having Issues?

1. **Check Windows Version**: Some older Windows versions have different PowerShell behavior
2. **Run as Administrator**: Right-click PowerShell/Command Prompt → "Run as administrator"
3. **Restart Computer**: Sometimes a restart fixes path issues
4. **Check Antivirus**: Some antivirus software blocks npm/Python execution

## 🎉 Expected Result

After fixing the issues, you should see:
```
🎓 ResultHub Smart Result Management System
================================================
✅ Node.js v22.20.0 found
✅ Python 3.14.0 found
📦 Installing dependencies...
✅ Root dependencies installed
✅ Backend dependencies installed  
✅ Frontend dependencies installed
🚀 Starting ResultHub servers...
   Backend:  http://localhost:5000
   Frontend: http://localhost:3000
```

Then open your browser to http://localhost:3000 and login with:
- **Username**: admin
- **Password**: admin123

---

**🎓 ResultHub - Smart Result Management System**
**Made with ❤️ for educational institutions**

