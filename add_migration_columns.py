"""
Database migration script to add Supabase Auth migration columns
Run this script to add the missing columns to your database
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_migration_columns():
    # Get database URL
    database_url = os.getenv('SUPABASE_DATABASE_URL')
    
    if not database_url:
        print("❌ SUPABASE_DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("🔄 Adding migration columns to users table...")
                
                # Add needs_migration column
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS needs_migration BOOLEAN DEFAULT TRUE
                """))
                print("✅ Added needs_migration column")
                
                # Add supabase_user_id column
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS supabase_user_id VARCHAR(36)
                """))
                print("✅ Added supabase_user_id column")
                
                # Commit the transaction
                trans.commit()
                print("✅ Migration completed successfully!")
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    success = add_migration_columns()
    
    if success:
        print("\n🎉 Migration completed! You can now restart your app.")
    else:
        print("\n💥 Migration failed. Please check the errors above.")
