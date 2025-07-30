#!/usr/bin/env python3
"""
Add CASCADE DELETE foreign key constraints
When a user is deleted, automatically delete their friend requests and internships
"""

import os
import sys
import sqlite3

def add_cascade_constraints_sqlite():
    """Add CASCADE DELETE constraints to SQLite database"""
    
    # Find the SQLite database file
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    db_path = os.path.join(instance_path, 'internships.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    print(f"🔍 Adding CASCADE constraints to: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key support (required for SQLite)
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("🔧 Current table structures:")
        
        # Check current foreign keys
        for table in ['friend_request', 'internship']:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fkeys = cursor.fetchall()
            print(f"   {table}: {len(fkeys)} foreign keys")
            for fk in fkeys:
                print(f"     - Column {fk[3]} -> {fk[2]}.{fk[4]} (ON DELETE: {fk[6]})")
        
        print("\n🚧 SQLite doesn't support ALTER TABLE for foreign keys.")
        print("We need to recreate tables with proper constraints...")
        
        # Backup existing data
        print("📋 Backing up existing data...")
        
        # Get friend_request data
        cursor.execute("SELECT * FROM friend_request")
        friend_requests = cursor.fetchall()
        cursor.execute("PRAGMA table_info(friend_request)")
        fr_columns = [col[1] for col in cursor.fetchall()]
        
        # Get internship data  
        cursor.execute("SELECT * FROM internship")
        internships = cursor.fetchall()
        cursor.execute("PRAGMA table_info(internship)")
        int_columns = [col[1] for col in cursor.fetchall()]
        
        print(f"   - {len(friend_requests)} friend requests backed up")
        print(f"   - {len(internships)} internships backed up")
        
        # Drop existing tables
        print("\n🗑️  Dropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS friend_request")
        cursor.execute("DROP TABLE IF EXISTS internship")
        
        # Recreate friend_request table with CASCADE
        print("🔨 Creating friend_request table with CASCADE DELETE...")
        cursor.execute("""
            CREATE TABLE friend_request (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester_id INTEGER NOT NULL,
                addressee_id INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (requester_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (addressee_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Recreate internship table with CASCADE
        print("🔨 Creating internship table with CASCADE DELETE...")
        cursor.execute("""
            CREATE TABLE internship (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company_name VARCHAR(100) NOT NULL,
                position_title VARCHAR(100) NOT NULL,
                application_date DATE,
                applied_date DATE,
                application_status VARCHAR(50) DEFAULT 'Applied',
                notes TEXT,
                location VARCHAR(100),
                salary VARCHAR(50),
                application_url VARCHAR(200),
                contact_person VARCHAR(100),
                contact_email VARCHAR(150),
                deadline DATE,
                interview_date DATETIME,
                offer_date DATE,
                rejection_date DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Restore data
        print("\n📥 Restoring data...")
        
        # Restore friend_requests
        if friend_requests:
            placeholders = ','.join(['?' for _ in fr_columns])
            cursor.executemany(
                f"INSERT INTO friend_request ({','.join(fr_columns)}) VALUES ({placeholders})",
                friend_requests
            )
            print(f"   ✅ {len(friend_requests)} friend requests restored")
        
        # Restore internships
        if internships:
            placeholders = ','.join(['?' for _ in int_columns])
            cursor.executemany(
                f"INSERT INTO internship ({','.join(int_columns)}) VALUES ({placeholders})",
                internships
            )
            print(f"   ✅ {len(internships)} internships restored")
        
        # Commit changes
        conn.commit()
        
        # Verify new constraints
        print("\n✅ Verifying new constraints:")
        for table in ['friend_request', 'internship']:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fkeys = cursor.fetchall()
            print(f"   {table}: {len(fkeys)} foreign keys")
            for fk in fkeys:
                print(f"     - Column {fk[3]} -> {fk[2]}.{fk[4]} (ON DELETE: {fk[6]})")
        
        conn.close()
        print("\n🎉 CASCADE DELETE constraints added successfully!")
        print("\nNow when you delete a user:")
        print("✅ All their friend requests will be automatically deleted")
        print("✅ All their internships will be automatically deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

def create_postgresql_migration():
    """Create PostgreSQL migration script for Render"""
    
    migration_sql = """
-- PostgreSQL CASCADE DELETE Migration
-- Run this in Render Shell or PostgreSQL console

BEGIN;

-- Add CASCADE DELETE to friend_request table
ALTER TABLE friend_request 
DROP CONSTRAINT IF EXISTS friend_request_requester_id_fkey;

ALTER TABLE friend_request 
DROP CONSTRAINT IF EXISTS friend_request_addressee_id_fkey;

ALTER TABLE friend_request 
ADD CONSTRAINT friend_request_requester_id_fkey 
FOREIGN KEY (requester_id) REFERENCES users (id) ON DELETE CASCADE;

ALTER TABLE friend_request 
ADD CONSTRAINT friend_request_addressee_id_fkey 
FOREIGN KEY (addressee_id) REFERENCES users (id) ON DELETE CASCADE;

-- Add CASCADE DELETE to internship table
ALTER TABLE internship 
DROP CONSTRAINT IF EXISTS internship_user_id_fkey;

ALTER TABLE internship 
ADD CONSTRAINT internship_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;

COMMIT;

-- Verify constraints
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND tc.table_name IN ('friend_request', 'internship');
"""
    
    with open('postgresql_cascade_migration.sql', 'w') as f:
        f.write(migration_sql)
    
    print("📄 Created postgresql_cascade_migration.sql")
    print("To use on Render:")
    print("1. Go to Render Shell")
    print("2. Run: psql $DATABASE_URL -f postgresql_cascade_migration.sql")

if __name__ == "__main__":
    print("🔧 CASCADE DELETE Constraints Setup")
    print("=" * 50)
    
    # Handle SQLite locally
    add_cascade_constraints_sqlite()
    
    # Create PostgreSQL migration for Render
    print("\n" + "=" * 50)
    create_postgresql_migration()
