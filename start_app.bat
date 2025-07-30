@echo off
echo ================================
echo    InternIn - Startup Options
echo ================================
echo.
echo Choose how to run the application:
echo.
echo 1. Development Server (Flask - with warning)
echo    - Fast restart on code changes
echo    - Shows debugging information
echo    - ⚠️  "development server" warning (NORMAL)
echo.
echo 2. Production Server (Gunicorn - no warning)
echo    - Production-ready WSGI server
echo    - No development warning
echo    - Slower restart, but production-like
echo.
choice /c 12 /m "Enter your choice (1 or 2)"

if %errorlevel%==1 (
    echo.
    echo 🔧 Starting Development Server...
    echo 📍 Available at: http://localhost:5000
    echo 🛑 Press Ctrl+C to stop
    echo.
    python run.py
) else (
    echo.
    echo 🚀 Starting Production Server...
    echo 📍 Available at: http://localhost:5000  
    echo 🛑 Press Ctrl+C to stop
    echo.
    gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 run:app
)