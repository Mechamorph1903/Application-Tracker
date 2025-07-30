@echo off
echo 🚀 Starting InternIn with Gunicorn (Production-like server)
echo.
echo 📍 Server will be available at: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the server
echo.

gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 run:app
