#!/usr/bin/env python3
"""
PostgreSQL Migration Script for Render Deployment
Add Supabase migration columns to production database
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_postgresql():
    """Add migration columns to PostgreSQL database"""
    try:
        from app import create_app
        from app.models import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("🔧 PostgreSQL Migration Script")
            print("=" * 50)
            
            # Check current database
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'postgresql' not in db_uri:
                print("❌ This script is for PostgreSQL databases only")
                return
                
            print(f"🔍 Connected to PostgreSQL database")
            
            try:
                # Check if columns exist
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name IN ('needs_migration', 'supabase_user_id')
                """))
                
                existing_columns = [row[0] for row in result.fetchall()]
                
                needs_migration_exists = 'needs_migration' in existing_columns
                supabase_user_id_exists = 'supabase_user_id' in existing_columns
                
                print(f"📋 Migration columns status:")
                print(f"   - needs_migration: {'✅ EXISTS' if needs_migration_exists else '❌ MISSING'}")
                print(f"   - supabase_user_id: {'✅ EXISTS' if supabase_user_id_exists else '❌ MISSING'}")
                
                # Add missing columns
                if not needs_migration_exists:
                    print("🔧 Adding needs_migration column...")
                    db.session.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN needs_migration BOOLEAN DEFAULT TRUE
                    """))
                    print("✅ needs_migration column added")
                
                if not supabase_user_id_exists:
                    print("🔧 Adding supabase_user_id column...")
                    db.session.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN supabase_user_id VARCHAR(36)
                    """))
                    print("✅ supabase_user_id column added")
                
                # Commit changes
                db.session.commit()
                
                if needs_migration_exists and supabase_user_id_exists:
                    print("✅ All migration columns already exist!")
                else:
                    print("✅ Migration completed successfully!")
                    
                # Check sample users
                result = db.session.execute(text("""
                    SELECT id, email, supabase_user_id, needs_migration 
                    FROM users 
                    LIMIT 3
                """))
                
                sample_users = result.fetchall()
                if sample_users:
                    print(f"\n👥 Sample users:")
                    for user in sample_users:
                        user_id, email, supabase_id, needs_migration = user
                        print(f"   - ID {user_id}: {email}")
                        print(f"     Supabase ID: {supabase_id or 'NULL'}")
                        print(f"     Needs Migration: {needs_migration}")
                        
            except Exception as e:
                print(f"❌ Migration failed: {e}")
                db.session.rollback()
                raise
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this in the correct environment")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    migrate_postgresql()
    print("\n🎉 PostgreSQL migration script complete!")
    print("\nTo run this on Render:")
    print("1. Go to your Render service dashboard")
    print("2. Open the Shell")
    print("3. Run: python postgresql_migration.py")
