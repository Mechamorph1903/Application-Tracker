#!/usr/bin/env python3
"""
Migration script to add next_action fields to the Internship model
Run this after updating your models.py file
"""

from app import create_app, db
from app.models import Internship
from sqlalchemy import text

def migrate_next_action_fields():
    """Add next_action fields to existing database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("PRAGMA table_info(internship)"))
            columns = [column[1] for column in result.fetchall()]
            
            # Add next_action column if it doesn't exist
            if 'next_action' not in columns:
                db.session.execute(text("""
                    ALTER TABLE internship 
                    ADD COLUMN next_action VARCHAR(50);
                """))
                print("✅ Added next_action column")
            else:
                print("ℹ️  next_action column already exists")
            
            # Add next_action_date column if it doesn't exist
            if 'next_action_date' not in columns:
                db.session.execute(text("""
                    ALTER TABLE internship 
                    ADD COLUMN next_action_date DATETIME;
                """))
                print("✅ Added next_action_date column")
            else:
                print("ℹ️  next_action_date column already exists")
            
            # Add next_action_notes column if it doesn't exist
            if 'next_action_notes' not in columns:
                db.session.execute(text("""
                    ALTER TABLE internship 
                    ADD COLUMN next_action_notes TEXT;
                """))
                print("✅ Added next_action_notes column")
            else:
                print("ℹ️  next_action_notes column already exists")
            
            # Migrate existing data
            print("\n🔄 Migrating existing data...")
            
            internships = Internship.query.all()
            for internship in internships:
                # Only set next_action if it's not already set
                if not internship.next_action:
                    # If they have interview_date, set next_action to 'interview'
                    if internship.interview_date:
                        internship.next_action = 'interview'
                        internship.next_action_date = internship.interview_date
                    # If they have follow_up_date, set next_action to 'follow_up'
                    elif internship.follow_up_date:
                        internship.next_action = 'follow_up'
                        internship.next_action_date = internship.follow_up_date
            
            db.session.commit()
            print(f"✅ Migrated {len(internships)} internship records")
            print("\n🎉 Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_next_action_fields()
