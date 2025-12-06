@echo off
echo 🎓 ResultHub Smart Result Management System
echo ================================================
echo.

echo ✅ Starting Backend Server...
start "Backend" cmd /k "cd backend && python app.py"

echo ✅ Starting Frontend Server...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo 🌐 Servers starting...
echo    Backend:  http://localhost:5000
echo    Frontend: http://localhost:3000
echo.
echo ✅ Both servers are starting in separate windows
echo    Close the windows to stop the servers
echo.
pause















