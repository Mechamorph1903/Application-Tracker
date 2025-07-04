#!/usr/bin/env python3
"""
Script to recreate the database with updated models.
This will drop all existing tables and recreate them with the new schema.
WARNING: This will delete all existing data!
"""

import os
import sys
from flask import Flask
from app import create_app, db
from app.models import User, Internship, FriendRequest, UserSettings

def recreate_database():
    """Drop and recreate all database tables"""
    app = create_app()
    
    with app.app_context():
        print("Dropping all existing tables...")
        db.drop_all()
        
        print("Creating new tables with updated schema...")
        db.create_all()
        
        print("Database recreated successfully!")
        print("\nNew tables created:")
        print("- User (with social_media JSON, online status, location)")
        print("- Internship (with location, dates, next actions)")
        print("- FriendRequest (for friend system)")
        print("- UserSettings (for app settings)")
        
        # Optionally create a test admin user
        create_test = input("\nWould you like to create a test admin user? (y/n): ").lower().strip()
        if create_test == 'y':
            admin_user = User(
                firstName='Admin',
                lastName='User',    
                username='admin',
                email='admin@example.com',
                major='Computer Science',
                school='Test University',
                year='Senior',
                is_admin=True
            )
            admin_user.set_password('admin123')  # Set a default password
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("Test admin user created successfully!")
            print("  Username: admin")
            print("  Password: admin123")
            print("  Email: admin@example.com")
            
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        recreate_database()
    else:
        print("WARNING: This will delete all existing data in the database!")
        print("To proceed, run: python recreate_db.py --force")
        print("Or just run the script and confirm when prompted.")
        
        confirm = input("Are you sure you want to recreate the database? (yes/no): ").lower().strip()
        if confirm == 'yes':
            recreate_database()
        else:
            print("Database recreation cancelled.")
