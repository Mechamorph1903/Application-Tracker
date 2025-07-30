#!/usr/bin/env python3
"""
Debug script to check Supabase configuration
Run this to see why new users might be getting migration warnings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_supabase_config():
    print("=== SUPABASE CONFIGURATION DEBUG ===")
    print()
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
    supabase_database_url = os.getenv('SUPABASE_DATABASE_URL')
    force_supabase = os.getenv('FORCE_SUPABASE', 'False').lower() == 'true'
    
    print("Environment Variables:")
    print(f"  SUPABASE_URL: {'✅ SET' if supabase_url else '❌ MISSING'}")
    print(f"  SUPABASE_SERVICE_KEY: {'✅ SET' if supabase_service_key else '❌ MISSING'}")
    print(f"  SUPABASE_DATABASE_URL: {'✅ SET' if supabase_database_url else '❌ MISSING'}")
    print(f"  FORCE_SUPABASE: {force_supabase}")
    print()
    
    if supabase_url:
        print(f"  SUPABASE_URL value: {supabase_url}")
    if supabase_service_key:
        print(f"  SUPABASE_SERVICE_KEY: {supabase_service_key[:20]}...{supabase_service_key[-10:] if len(supabase_service_key) > 30 else supabase_service_key}")
    print()
    
    # Test Supabase client creation
    if supabase_url and supabase_service_key:
        try:
            from supabase import create_client
            print("Testing Supabase client creation...")
            supabase = create_client(supabase_url, supabase_service_key)
            print("✅ Supabase client created successfully!")
            
            # Test auth admin access (this is what's used for user creation)
            try:
                # Test if we can access the admin functions
                print("Testing admin auth access...")
                # This should not error if the service key has proper permissions
                auth_admin = supabase.auth.admin
                print("✅ Admin auth access available!")
            except Exception as e:
                print(f"❌ Admin auth access failed: {e}")
                print("   This means your SUPABASE_SERVICE_KEY may not have admin permissions")
                
        except ImportError as e:
            print(f"❌ Cannot import supabase: {e}")
            print("   Run: pip install supabase")
        except Exception as e:
            print(f"❌ Supabase client creation failed: {e}")
            print("   Check your SUPABASE_URL and SUPABASE_SERVICE_KEY")
    else:
        print("❌ Cannot test Supabase client - missing required environment variables")
        print("   You need both SUPABASE_URL and SUPABASE_SERVICE_KEY")
    
    print()
    print("=== RECOMMENDATIONS ===")
    
    if not supabase_url or not supabase_service_key:
        print("1. Create a .env file in your project root with:")
        print("   SUPABASE_URL=https://your-project.supabase.co")
        print("   SUPABASE_SERVICE_KEY=your-service-role-key")
        print("   SUPABASE_DATABASE_URL=postgresql://...")
        print()
        print("2. Get these values from your Supabase dashboard:")
        print("   - Go to Settings > API")
        print("   - Copy the 'URL' and 'service_role' key")
        print("   - For DATABASE_URL, go to Settings > Database")
        print()
    
    print("3. If you don't want to use Supabase at all:")
    print("   - Remove or comment out the Supabase environment variables")
    print("   - The app will work in local SQLite mode")
    print("   - New users won't need migration warnings")
    print()
    print("4. Check your Supabase project settings:")
    print("   - Ensure email auth is enabled")
    print("   - Check if your service key has admin permissions")
    
    print()
    print("=== DATABASE CHECK ===")
    
    # Check if local database exists
    local_db_path = os.path.join(os.getcwd(), 'instance', 'internships.db')
    if os.path.exists(local_db_path):
        print(f"✅ Local SQLite database exists: {local_db_path}")
    else:
        print(f"❌ Local SQLite database not found: {local_db_path}")
    
    print()

if __name__ == "__main__":
    check_supabase_config()
