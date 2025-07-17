#!/usr/bin/env python3
"""Debug contacts field issue"""

from app import create_app
from app.models import Internship
import json

app = create_app()

with app.app_context():
    # Find internships with contacts
    internships = Internship.query.filter(Internship.contacts.isnot(None)).all()
    
    print(f"Found {len(internships)} internships with contacts")
    
    for internship in internships:
        print(f"\n--- Internship: {internship.company_name} - {internship.position} ---")
        print(f"Contacts type: {type(internship.contacts)}")
        print(f"Contacts value: {internship.contacts}")
        
        # Try to parse if it's a string
        if isinstance(internship.contacts, str):
            try:
                parsed = json.loads(internship.contacts)
                print(f"Parsed contacts: {parsed}")
                print(f"Parsed type: {type(parsed)}")
                print(f"Number of contacts: {len(parsed)}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
        
        # Check if it's already a list
        elif isinstance(internship.contacts, list):
            print(f"Already a list with {len(internship.contacts)} items")
            for i, contact in enumerate(internship.contacts):
                print(f"  Contact {i}: {contact}")
        
        print("-" * 50)
