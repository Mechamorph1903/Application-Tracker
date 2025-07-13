@echo off
echo.
echo 🔄 Syncing your data to Supabase...
echo.

python -c "import os; import sqlite3; from supabase import create_client; from dotenv import load_dotenv; load_dotenv(); supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); conn = sqlite3.connect('instance/internships.db'); conn.row_factory = sqlite3.Row; cursor = conn.cursor(); cursor.execute('SELECT * FROM internships'); internships = cursor.fetchall(); print('Syncing internships...'); [supabase.table('internships').upsert(dict(i)).execute() for i in internships]; cursor.execute('SELECT * FROM users'); users = cursor.fetchall(); print('Syncing users...'); [supabase.table('users').upsert(dict(u)).execute() for u in users]; conn.close(); print('✅ Sync completed!')"

echo.
echo ✅ Your data is now backed up to Supabase!
echo.
pause
