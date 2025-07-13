#!/usr/bin/env python3
"""
TUTORIAL: Database Migration Basics
Learn how to safely modify database schemas

This is a simplified migration example to teach you the concepts.
"""

import sqlite3
import os

def migration_tutorial():
    """
    🎓 TUTORIAL: Understanding Database Migrations
    
    What is a migration?
    - A script that modifies your database structure (schema)
    - Adds/removes tables, columns, indexes, constraints
    - Should be reversible (have an "undo" option)
    - Should be safe (backup first, check before running)
    
    Why do we need migrations?
    - Your app evolves, so does your data structure
    - Team members need the same database structure
    - Production databases need to be updated safely
    - You want to track database changes in version control
    """
    
    print("🎓 DATABASE MIGRATION TUTORIAL")
    print("=" * 50)
    
    # Example: Adding a single column
    print("\n📖 Example 1: Adding a Single Column")
    print("Problem: We want to add 'salary_range' to internships")
    print("Solution: ALTER TABLE command")
    print("""
    SQL Command:
    ALTER TABLE internship ADD COLUMN salary_range VARCHAR(50);
    
    Python Code:
    cursor.execute("ALTER TABLE internship ADD COLUMN salary_range VARCHAR(50)")
    """)
    
    # Example: Checking if column exists first
    print("\n📖 Example 2: Safe Column Addition (Check First)")
    print("Problem: What if we run the migration twice?")
    print("Solution: Check if column exists before adding")
    print("""
    Python Code:
    def check_column_exists(cursor, table_name, column_name):
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    
    if not check_column_exists(cursor, 'internship', 'salary_range'):
        cursor.execute("ALTER TABLE internship ADD COLUMN salary_range VARCHAR(50)")
        print("✅ Added salary_range column")
    else:
        print("⚠️  Column already exists, skipping")
    """)
    
    # Example: Multiple columns with transaction
    print("\n📖 Example 3: Adding Multiple Columns Safely")
    print("Problem: What if one column fails?")
    print("Solution: Use database transactions")
    print("""
    Python Code:
    try:
        conn.begin()  # Start transaction
        
        # Add multiple columns
        if not check_column_exists(cursor, 'internship', 'salary_range'):
            cursor.execute("ALTER TABLE internship ADD COLUMN salary_range VARCHAR(50)")
        
        if not check_column_exists(cursor, 'internship', 'remote_option'):
            cursor.execute("ALTER TABLE internship ADD COLUMN remote_option BOOLEAN DEFAULT 0")
        
        conn.commit()  # Save all changes
        print("✅ All columns added successfully")
        
    except Exception as e:
        conn.rollback()  # Undo all changes if something fails
        print(f"❌ Migration failed: {e}")
    """)
    
    # Example: Data migration
    print("\n📖 Example 4: Migrating Data (Not Just Schema)")
    print("Problem: We want to populate the new columns with data")
    print("Solution: UPDATE statements after adding columns")
    print("""
    Python Code:
    # First, add the column
    cursor.execute("ALTER TABLE internship ADD COLUMN job_type VARCHAR(20) DEFAULT 'on-site'")
    
    # Then, update existing records based on location data
    cursor.execute('''
        UPDATE internship 
        SET job_type = 'remote' 
        WHERE location LIKE '%Remote%' OR location LIKE '%remote%'
    ''')
    
    cursor.execute('''
        UPDATE internship 
        SET job_type = 'hybrid' 
        WHERE location LIKE '%Hybrid%' OR location LIKE '%hybrid%'
    ''')
    """)
    
    # Best practices
    print("\n📖 Best Practices for Migrations")
    best_practices = [
        "1. 📦 Always backup your database first",
        "2. 🧪 Test migrations on a copy of your data",
        "3. 🔍 Check if changes already exist (idempotent)",
        "4. 🔄 Use transactions for multiple operations",
        "5. 📝 Log what you're doing for debugging",
        "6. ⏪ Plan how to reverse the migration",
        "7. 🚀 Run on development, then staging, then production",
        "8. 📊 Verify the migration worked correctly"
    ]
    
    for practice in best_practices:
        print(f"   {practice}")
    
    print("\n🎯 Migration Workflow:")
    workflow = [
        "1. Backup database",
        "2. Create migration script",
        "3. Test on development database",
        "4. Run migration",
        "5. Verify results",
        "6. Update your models.py to match",
        "7. Test your app with new fields"
    ]
    
    for i, step in enumerate(workflow, 1):
        print(f"   {step}")

if __name__ == '__main__':
    migration_tutorial()
