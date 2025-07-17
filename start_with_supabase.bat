@echo off
echo.
echo 🚀 Starting Flask App with Supabase Dynamic Sync
echo.

REM Set environment variable to force Supabase connection
set FORCE_SUPABASE=true

echo Testing Supabase connection...
python -c "import psycopg2; conn = psycopg2.connect('postgresql://postgres:OndomuAganahAnorue@db.yzrfoxjwqlthhmwvqguu.supabase.co:5432/postgres'); print('✅ Supabase connection successful!'); conn.close()" 2>nul && (
    echo ✅ Supabase PostgreSQL connection successful!
    echo 🔄 Dynamic sync will be enabled
) || (
    echo ⚠️  Supabase connection failed - using SQLite with manual sync
    set FORCE_SUPABASE=false
)

echo.
echo Starting Flask application...
python run.py
pause
