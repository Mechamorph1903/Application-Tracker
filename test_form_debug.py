#!/usr/bin/env python3
"""
Simple test to debug form submission issue
"""

from app import create_app
from flask import url_for
import os

def test_form_submission():
    """Test form submission debugging"""
    
    app = create_app()
    
    # Test with a request context
    with app.test_request_context():
        print("=== URL TESTING ===")
        
        try:
            add_url = url_for('applications.add_application')
            print(f"Add URL: {add_url}")
            
            list_url = url_for('applications.applicationsList')
            print(f"List URL: {list_url}")
            
            print("\n=== ROUTE TESTING ===")
            # List all routes
            for rule in app.url_map.iter_rules():
                print(f"Route: {rule.rule} -> {rule.endpoint}")
            
        except Exception as e:
            print(f"URL generation error: {e}")
    
    # Test form submission
    print("\n=== FORM SUBMISSION TEST ===")
    
    with app.test_client() as client:
        # First, let's check if we need to login
        print("Testing login requirement...")
        response = client.get('/applications/add')
        print(f"GET Response status: {response.status_code}")
        
        if response.status_code == 302:
            print("Redirected - login required!")
            print(f"Redirect location: {response.headers.get('Location')}")
            
            # Let's test what happens if we try to access the route directly
            print("\n=== TESTING DIRECT ACCESS ===")
            
            # Check if there's a user in the database
            from app.models import User
            with app.app_context():
                users = User.query.all()
                print(f"Users in database: {len(users)}")
                if users:
                    print(f"First user: {users[0].username}")
                    
                    # Try to simulate a logged-in session
                    print("\n=== SIMULATING LOGIN SESSION ===")
                    with client.session_transaction() as sess:
                        sess['_user_id'] = str(users[0].id)
                        sess['_fresh'] = True
                    
                    # Now try the GET request again
                    response = client.get('/applications/add')
                    print(f"GET Response status (after login): {response.status_code}")
                    
                    if response.status_code == 200:
                        print("✓ GET request successful after login!")
                        
                        # Now test POST
                        print("Testing POST request with login...")
                        form_data = {
                            'app_name': 'Test Application',
                            'company': 'Test Company',
                            'role': 'Test Role',
                            'location': 'Test Location',
                            'link': 'http://test.com',
                            'description': 'Test Description',
                            'notes': 'Test Notes',
                            'applied': '2025-07-07',
                            'contacts': '[]'
                        }
                        
                        response = client.post('/applications/add', data=form_data, follow_redirects=True)
                        print(f"POST Response status: {response.status_code}")
                        print(f"POST Response URL: {response.request.url}")
                        
                        if response.status_code == 200:
                            print("✓ Form submission successful!")
                        else:
                            print("✗ Form submission failed!")
                    
                else:
                    print("No users found in database - login required!")
        else:
            print("No redirect - testing form directly...")
            # Continue with original test

if __name__ == "__main__":
    test_form_submission()
