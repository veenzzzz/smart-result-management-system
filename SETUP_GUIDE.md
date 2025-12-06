# 🎓 ResultHub Setup Guide

## 🚀 Quick Start (Single Command)

### Option 1: Using npm (Recommended)
```bash
# Install all dependencies and start both servers
npm run dev
```

### Option 2: Using Python script
```bash
# Start both servers with Python
python start.py
```

### Option 3: Using Windows batch file
```bash
# Double-click start.bat or run in terminal
start.bat
```

## 🔧 Manual Setup

### Step 1: Install Dependencies

#### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
cd frontend
npm install
```

#### Root Dependencies (for concurrently)
```bash
npm install
```

### Step 2: Start Servers

#### Option A: Start Both Together
```bash
# From project root
npm run dev
```

#### Option B: Start Separately
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## 🌐 How Localhost Communication Works

### Why Both Use Localhost?

**Frontend (React/Vite)**: `http://localhost:3000`
- Serves the user interface
- Handles user interactions
- Makes API calls to backend

**Backend (Flask API)**: `http://localhost:5000`
- Serves the API endpoints
- Handles database operations
- Processes business logic

### Communication Flow

```
User Browser (localhost:3000)
    ↓ HTTP Request
Frontend React App
    ↓ API Call (/api/students)
Vite Proxy Server
    ↓ Proxy to backend
Backend Flask API (localhost:5000)
    ↓ Database Query
SQLite Database
    ↓ Response
Backend Flask API
    ↓ JSON Response
Vite Proxy Server
    ↓ Forward response
Frontend React App
    ↓ Update UI
User Browser
```

### CORS Configuration

The backend is configured with CORS to allow frontend requests:

```python
from flask_cors import CORS
CORS(app, supports_credentials=True)
```

### Vite Proxy Configuration

The frontend uses Vite's proxy to forward API requests:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
    },
  },
}
```

## 🔧 Troubleshooting Common Issues

### Issue 1: Port Already in Use

**Error**: `Port 3000 is already in use`

**Solution**:
```bash
# Kill process using port 3000
npx kill-port 3000

# Or change port in vite.config.ts
server: {
  port: 3001,  // Change to different port
}
```

### Issue 2: Backend Import Errors

**Error**: `ModuleNotFoundError: No module named 'database'`

**Solution**: The backend app.py is configured to import from the parent directory:
```python
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
```

### Issue 3: CORS Errors

**Error**: `Access to fetch at 'http://localhost:5000/api/auth/login' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution**: The backend already has CORS configured, but if issues persist:
```python
# In backend/app.py
CORS(app, 
     origins=["http://localhost:3000"],
     supports_credentials=True)
```

### Issue 4: Database Connection Errors

**Error**: `Database connection failed`

**Solution**: Ensure the database directory exists and is writable:
```bash
# Check if database exists
ls database/result_tracker.db

# If not, the backend will create it automatically
```

### Issue 5: Node.js/React Errors

**Error**: `Cannot find module 'react'`

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue 6: Python Module Errors

**Error**: `No module named 'flask'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

## 🎯 Verification Steps

### 1. Check Backend is Running
```bash
curl http://localhost:5000/api/auth/me
# Should return authentication error (expected)
```

### 2. Check Frontend is Running
Open `http://localhost:3000` in browser
- Should show login page
- No console errors

### 3. Test Full Flow
1. Open `http://localhost:3000`
2. Login with `admin` / `admin123`
3. Should redirect to dashboard
4. Check browser network tab for API calls

## 📱 Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api (if implemented)

## 🔑 Default Credentials

- **Admin**: `admin` / `admin123`
- **Students**: Use roll number and password (created by admin)

## 🛠️ Development Commands

### Frontend Only
```bash
cd frontend
npm run dev
```

### Backend Only
```bash
cd backend
python app.py
```

### Build Frontend
```bash
cd frontend
npm run build
```

### Install All Dependencies
```bash
npm run install-all
```

## 🚀 Production Deployment

### Frontend (Static Files)
```bash
cd frontend
npm run build
# Deploy 'dist' folder to any static hosting
```

### Backend (Python)
```bash
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📞 Support

If you encounter issues:

1. **Check Console**: Browser developer tools
2. **Check Terminal**: Look for error messages
3. **Verify Ports**: Ensure 3000 and 5000 are available
4. **Check Dependencies**: All packages installed correctly
5. **Database**: SQLite file exists and is writable

## 🎉 Success Indicators

✅ Frontend loads at http://localhost:3000
✅ Backend responds at http://localhost:5000
✅ Login page displays correctly
✅ Can login with admin credentials
✅ Dashboard loads after login
✅ No console errors
✅ API calls work between frontend and backend

---

**🎓 ResultHub - Smart Result Management System**
**Made with ❤️ for educational institutions**


