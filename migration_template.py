#!/usr/bin/env python3
"""
Migration Template
Copy this file and modify it for your own migrations

Usage:
1. Copy this file: cp migration_template.py migrate_your_feature.py
2. Update the MIGRATION_INFO section
3. Modify the migrate_up() and migrate_down() functions
4. Run: python migrate_your_feature.py
"""

import sqlite3
import os
from datetime import datetime

# 📝 MIGRATION INFORMATION - UPDATE THIS SECTION
MIGRATION_INFO = {
    'name': 'Your Migration Name',
    'description': 'What this migration does',
    'version': '001',
    'date': '2025-07-12',
    'author': 'Your Name'
}

def backup_database():
    """Create a backup of the current database"""
    db_path = 'instance/internships.db'
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return False
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'instance/internships.db.backup_{timestamp}'
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def check_column_exists(cursor, table_name, column_name):
    """Check if a column already exists in the table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns

def check_table_exists(cursor, table_name):
    """Check if a table exists"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def migrate_up():
    """
    🔧 FORWARD MIGRATION - UPDATE THIS FUNCTION
    Add your migration logic here
    """
    db_path = 'instance/internships.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Running forward migration...")
        
        # 🎯 EXAMPLE: Add a new column
        # if not check_column_exists(cursor, 'internship', 'your_new_column'):
        #     cursor.execute('ALTER TABLE internship ADD COLUMN your_new_column VARCHAR(100)')
        #     print("✅ Added your_new_column")
        
        # 🎯 EXAMPLE: Create a new table
        # if not check_table_exists(cursor, 'your_new_table'):
        #     cursor.execute('''
        #         CREATE TABLE your_new_table (
        #             id INTEGER PRIMARY KEY,
        #             name VARCHAR(100),
        #             created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        #         )
        #     ''')
        #     print("✅ Created your_new_table")
        
        # 🎯 EXAMPLE: Update existing data
        # cursor.execute("UPDATE internship SET your_new_column = 'default_value' WHERE your_new_column IS NULL")
        # print("✅ Updated existing records")
        
        # 🎯 ADD YOUR MIGRATION CODE HERE 🎯
        print("⚠️  No migration logic defined yet!")
        print("   Edit the migrate_up() function in this file")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Forward migration failed: {e}")
        return False

def migrate_down():
    """
    ⏪ REVERSE MIGRATION - UPDATE THIS FUNCTION
    Remove the changes made by migrate_up()
    """
    db_path = 'instance/internships.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("⏪ Running reverse migration...")
        
        # 🎯 EXAMPLE: Remove column (SQLite doesn't support DROP COLUMN easily)
        # print("⚠️  SQLite doesn't support DROP COLUMN. You may need to recreate the table.")
        
        # 🎯 EXAMPLE: Drop table
        # cursor.execute("DROP TABLE IF EXISTS your_new_table")
        # print("✅ Dropped your_new_table")
        
        # 🎯 ADD YOUR REVERSE MIGRATION CODE HERE 🎯
        print("⚠️  No reverse migration logic defined yet!")
        print("   Edit the migrate_down() function in this file")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Reverse migration failed: {e}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    db_path = 'instance/internships.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verifying migration...")
        
        # 🎯 ADD YOUR VERIFICATION LOGIC HERE 🎯
        # Example: Check if columns exist
        # required_columns = ['your_new_column']
        # cursor.execute("PRAGMA table_info(internship)")
        # existing_columns = [column[1] for column in cursor.fetchall()]
        # 
        # for col in required_columns:
        #     if col in existing_columns:
        #         print(f"✅ {col}: Found")
        #     else:
        #         print(f"❌ {col}: Missing")
        
        print("⚠️  No verification logic defined yet!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main migration function"""
    print(f"🚀 Starting Migration: {MIGRATION_INFO['name']}")
    print(f"📝 Description: {MIGRATION_INFO['description']}")
    print(f"👤 Author: {MIGRATION_INFO['author']}")
    print(f"📅 Date: {MIGRATION_INFO['date']}")
    print("=" * 60)
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. 🔧 Run forward migration (migrate up)")
    print("2. ⏪ Run reverse migration (migrate down)")
    print("3. 🔍 Just verify current state")
    print("4. 📖 Show migration info")
    print("5. ❌ Cancel")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        # Forward migration
        print("\n📦 Creating backup...")
        if backup_database():
            if migrate_up():
                verify_migration()
            else:
                print("❌ Migration failed!")
    
    elif choice == '2':
        # Reverse migration
        print("\n📦 Creating backup...")
        if backup_database():
            if migrate_down():
                print("✅ Reverse migration completed")
            else:
                print("❌ Reverse migration failed!")
    
    elif choice == '3':
        # Just verify
        verify_migration()
    
    elif choice == '4':
        # Show info
        print(f"\n📋 Migration Info:")
        for key, value in MIGRATION_INFO.items():
            print(f"   {key.title()}: {value}")
    
    elif choice == '5':
        print("❌ Migration cancelled")
    
    else:
        print("❌ Invalid choice")

if __name__ == '__main__':
    main()
