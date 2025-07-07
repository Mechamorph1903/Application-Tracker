#!/usr/bin/env python3
"""
Database migration to remove next_action columns from internships table
This script safely removes the next_action_date and next_action_type columns
from the internships table while preserving all other data.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Remove next_action columns from internships table"""
    
    # Database path
    db_path = os.path.join('instance', 'internships.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    # Create backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Created backup at {backup_path}")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(internship)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        has_next_action_date = 'next_action_date' in column_names
        has_next_action_type = 'next_action_type' in column_names
        
        if not has_next_action_date and not has_next_action_type:
            print("No next_action columns found. Migration not needed.")
            conn.close()
            return True
        
        print("Found next_action columns. Starting migration...")
        
        # Get current table structure (excluding next_action columns)
        create_table_sql = """
        CREATE TABLE internship_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name VARCHAR(250) NOT NULL,
            company_name VARCHAR(100) NOT NULL,
            position VARCHAR(100) NOT NULL,
            application_status VARCHAR(50) NOT NULL DEFAULT 'Applied',
            application_link VARCHAR(200),
            application_description TEXT,
            applied_date DATE,
            status_change_date DATE,
            notes TEXT,
            visibility VARCHAR(20) DEFAULT 'friends',
            location VARCHAR(200),
            contacts JSON,
            interview_date DATETIME,
            follow_up_date DATETIME,
            deadline_date DATETIME,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(id)
        );
        """
        
        # Create new table
        cursor.execute(create_table_sql)
        
        # Copy data from old table (excluding next_action columns)
        insert_sql = """
        INSERT INTO internship_new (
            id, job_name, company_name, position, application_status,
            application_link, application_description, applied_date,
            status_change_date, notes, visibility, location, contacts,
            interview_date, follow_up_date, deadline_date, user_id
        )
        SELECT 
            id, job_name, company_name, position, application_status,
            application_link, application_description, applied_date,
            status_change_date, notes, visibility, location, contacts,
            interview_date, follow_up_date, deadline_date, user_id
        FROM internship;
        """
        
        cursor.execute(insert_sql)
        
        # Drop old table
        cursor.execute("DROP TABLE internship")
        
        # Rename new table
        cursor.execute("ALTER TABLE internship_new RENAME TO internship")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("Migration completed successfully!")
        print("Next action columns have been removed from the database.")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        # Restore backup if migration failed
        if os.path.exists(backup_path):
            try:
                shutil.copy2(backup_path, db_path)
                print(f"Restored database from backup: {backup_path}")
            except Exception as restore_error:
                print(f"Failed to restore backup: {str(restore_error)}")
        return False

if __name__ == "__main__":
    print("Starting database migration to remove next_action columns...")
    success = migrate_database()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed. Please check the error messages above.")
