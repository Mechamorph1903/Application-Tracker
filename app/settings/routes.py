from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, send_file, current_app
from app.models import db, User, UserSettings, Internship
import json
import csv
import io
import os
import uuid
import base64
from datetime import datetime, timezone
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from PIL import Image
from app.auth.compatibility import require_supabase_user
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(override=True)
SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'profile-pics')


# Try to import pandas for Excel export, fallback to CSV if not available
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# File upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

settings = Blueprint('settings', __name__)

@settings.route('/', methods=['GET', 'POST'])
@require_supabase_user
def settings_page(user):
    # Ensure user has settings
    if not user.settings:
        user.create_user_settings()
    
    return render_template('settings.html', user=user, pandas_available=PANDAS_AVAILABLE)

@settings.route('/update-user-settings', methods=['POST'])
@require_supabase_user
def update_user_settings(user):
    """Update user personal information"""
    try:
        # Handle profile picture upload (Supabase)
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            print(f"[DEBUG] Received profile_picture: {getattr(file, 'filename', None)}")
            if file and file.filename:
                # Check file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                print(f"[DEBUG] Uploaded file size: {file_size}")
                file.seek(0)
                if file_size > MAX_FILE_SIZE:
                    print(f"[DEBUG] File too large: {file_size} > {MAX_FILE_SIZE}")
                    return jsonify({'success': False, 'error': 'File size too large. Maximum 5MB allowed.'}), 400
                
                # Save to Supabase
                print("[DEBUG] Calling upload_profile_picture_to_supabase...")
                supa_url = upload_profile_picture_to_supabase(file, user.id, user.username)
                print(f"[DEBUG] supa_url returned: {supa_url}")
                if supa_url:
                    # Update user's profile picture
                    user.profile_picture = supa_url
                    print(f"[DEBUG] Updated profile_picture to: {supa_url}")
                else:
                    print("[DEBUG] Failed to upload to Supabase or invalid file type.")
                    return jsonify({'success': False, 'error': 'Failed to upload to Supabase or invalid file type.'}), 400
        
        # Update User model fields
        user.firstName = request.form.get('firstName', user.firstName)
        user.lastName = request.form.get('lastName', user.lastName)
        user.username = request.form.get('username', user.username)
        user.phone = request.form.get('phone', user.phone)
        user.bio = request.form.get('bio', user.bio)
        user.school = request.form.get('school', user.school)
        user.year = request.form.get('year', user.year)
        user.major = request.form.get('major', user.major)

        #Update Email logic to also reflectyin supabaseAuth
        new_email = request.form.get('email') 
        
        if new_email and new_email != user.email:
            try:
                
                response = current_app.supabase.auth.update_user(
                    {"email": new_email}
                )
                user.email = new_email
                current_app.send_welcome_email(user=user)

                if not response or getattr(response, "error", None):
                    raise Exception(f"Supabase update failed: {getattr(response, 'error', 'Unknown error')}")
            except Exception as e:
                print(f"⚠️ Update email failed: {e}")
               



        # Handle social media JSON
        if 'social_media' in request.form:
            try:
                social_media_json = request.form.get('social_media', '[]')
                user.social_media = json.loads(social_media_json)
            except json.JSONDecodeError:
                user.social_media = []

        # Ensure user has settings
        if not user.settings:
            user.create_user_settings()
        
        # Update UserSettings model fields
        user.settings.profile_visibility = request.form.get('profile_visibility', user.settings.profile_visibility)
        user.settings.show_application_stats = request.form.get('show_application_stats') == 'true'
        user.settings.timezone = request.form.get('timezone', user.settings.timezone)
        user.settings.two_factor_enabled = request.form.get('two_factor_enabled') == 'true'
        user.settings.login_notifications = request.form.get('login_notifications') == 'true'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User settings updated successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings.route('/upload-cropped-profile-picture', methods=['POST'])
@require_supabase_user
def upload_cropped_profile_picture(user):
    """Handle cropped profile picture upload"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data provided'}), 400
        
        # Extract base64 image data
        image_data = data['image']
        if image_data.startswith('data:image/'):
            # Remove data URL prefix
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'success': False, 'error': 'Invalid image data'}), 400
        
        # Check file size
        if len(image_bytes) > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': 'Image too large after cropping'}), 400
        
        # Use username with jpg extension for cropped images
        filename = f"{user.username}.jpg"
        
        # Upload to Supabase
        try:
            res = current_app.supabase.storage.from_(SUPABASE_BUCKET).upload(
                filename, 
                image_bytes, 
                {
                    'content-type': 'image/jpeg',
                    'upsert': 'true'  # Replace existing file
                }
            )
            
            if hasattr(res, "error") and res.error:
                print("[DEBUG] Supabase upload error:", res.error)
                return jsonify({'success': False, 'error': 'Failed to upload cropped image'}), 500
            
            # Get public URL (bucket should now be public)
            public_url = current_app.supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
            
            # Clean up any trailing ? characters
            if public_url.endswith('?'):
                public_url = public_url[:-1]
                
            print(f"[DEBUG] Generated public URL for cropped image: {public_url}")
            
            # Verify it's actually a public URL
            if '/public/' not in public_url:
                print(f"[DEBUG] WARNING: Bucket may not be public! URL: {public_url}")
            
            # Update user's profile picture
            user.profile_picture = public_url
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': 'Profile picture updated successfully!',
                'new_image_url': public_url
            })
            
        except Exception as e:
            print(f"[DEBUG] Supabase upload exception: {e}")
            return jsonify({'success': False, 'error': 'Failed to upload to cloud storage'}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings.route('/update-app-settings', methods=['POST'])
@require_supabase_user
def update_app_settings(user):
    """Update application preferences"""
    try:
        # Ensure user has settings
        if not user.settings:
            user.create_user_settings()
        
        # Update app settings
        user.settings.theme = request.form.get('theme', user.settings.theme)
        user.settings.dashboard_layout = request.form.get('dashboard_layout', user.settings.dashboard_layout)
        user.settings.items_per_page = int(request.form.get('items_per_page', user.settings.items_per_page))
        user.settings.date_format = request.form.get('date_format', user.settings.date_format)
        user.settings.time_format = request.form.get('time_format', user.settings.time_format)
        
        # Notification settings
        user.settings.email_notifications = request.form.get('email_notifications') == 'true'
        user.settings.friend_request_notifications = request.form.get('friend_request_notifications') == 'true'
        user.settings.application_reminders = request.form.get('application_reminders') == 'true'
        user.settings.interview_reminders = request.form.get('interview_reminders') == 'true'
        user.settings.reminder_days_before_followup = int(request.form.get('reminder_days_before_followup', user.settings.reminder_days_before_followup))
        
        # Application tracking settings
        user.settings.auto_archive_rejected = request.form.get('auto_archive_rejected') == 'true'
        user.settings.default_application_status = request.form.get('default_application_status', user.settings.default_application_status)
        
        # Data settings
        user.settings.auto_backup = request.form.get('auto_backup') == 'true'
        user.settings.export_format = request.form.get('export_format', user.settings.export_format)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'App settings updated successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings.route('/export-internships')
@require_supabase_user
def export_internships(user):
    """Export user's internships based on their preferred format"""
    try:
        # Get user's internships
        internships = Internship.query.filter_by(user_id=user.id).all()
        
        # Get export format preference
        export_format = user.settings.export_format if user.settings else 'csv'
        
        # If Excel is requested but pandas is not available, fallback to CSV
        if export_format == 'excel' and not PANDAS_AVAILABLE:
            export_format = 'csv'
            flash('Excel export requires pandas. Exporting as CSV instead.', 'warning')
        
        # Prepare data
        data = []
        for internship in internships:
            data.append({
                'Job Name': internship.job_name,
                'Company': internship.company_name,
                'Position': internship.position,
                'Status': internship.application_status,
                'Applied Date': internship.applied_date.strftime('%Y-%m-%d') if internship.applied_date else '',
                'Location': internship.location or '',
                'Next Action': internship.next_action or '',
                'Next Action Date': internship.next_action_date.strftime('%Y-%m-%d %H:%M') if internship.next_action_date else '',
                'Notes': internship.notes or ''
            })
        
        if export_format == 'csv':
            # Create CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            
            # Create response
            response = io.BytesIO()
            response.write(output.getvalue().encode('utf-8'))
            response.seek(0)
            
            return send_file(
                response,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'internships_{datetime.now().strftime("%Y%m%d")}.csv'
            )
            
        elif export_format == 'excel' and PANDAS_AVAILABLE:
            # Create Excel
            df = pd.DataFrame(data)
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'internships_{datetime.now().strftime("%Y%m%d")}.xlsx'
            )
            
        else:
            return jsonify({'error': 'Unsupported export format or pandas not available'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings.route('/change-password', methods=['POST'])
@require_supabase_user
def change_password(user):
    """Change user's password"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        # Check if current password is correct
        if not user.check_password(current_password):
            return jsonify({'success': False, 'error': 'Current password is incorrect'}), 400
        
        # Check if new passwords match
        if new_password != confirm_password:
            return jsonify({'success': False, 'error': 'New passwords do not match'}), 400
        
        # Validate new password strength
        if len(new_password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'}), 400
        
        # Check if new password is different from current
        if user.check_password(new_password):
            return jsonify({'success': False, 'error': 'New password must be different from current password'}), 400
        
        # Update password
        user.set_password(new_password)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Password changed successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings.route('/cleanup-profile-url', methods=['GET', 'POST'])
@require_supabase_user
def cleanup_profile_url(user):
    """Clean up profile picture URL by removing trailing ? and updating to new format"""
    try:
        if user.profile_picture:
            # Remove trailing ?
            clean_url = user.profile_picture.rstrip('?')
            user.profile_picture = clean_url
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': 'Profile picture URL cleaned up!',
                'new_url': clean_url
            })
        else:
            return jsonify({'success': False, 'message': 'No profile picture to clean up'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings.route('/debug-profile-pic')
@require_supabase_user
def debug_profile_pic(user):
    """Debug profile picture issues"""
    return jsonify({
        'user_id': user.id,
        'username': user.username,
        'profile_picture': user.profile_picture,
        'profile_picture_length': len(user.profile_picture) if user.profile_picture else 0,
        'has_trailing_question': user.profile_picture.endswith('?') if user.profile_picture else False
    })

# Helper functions for file upload
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- DEBUG ENHANCED ---
def upload_profile_picture_to_supabase(file, user_id, username):
    """Upload profile picture to Supabase Storage and return public URL"""
    print("[DEBUG] upload_profile_picture_to_supabase called")
    print(f"[DEBUG] supabase is None: {current_app.supabase is None}")
    print(f"[DEBUG] file: {file}")
    print(f"[DEBUG] username: {username}")
    
    if not hasattr(current_app, 'supabase') or not current_app.supabase:
        print("[DEBUG] Supabase client is not initialized!")
        return None
        
    if file and allowed_file(file.filename):
        print(f"[DEBUG] Allowed file: {file.filename}")
        
        # Extract file extension from uploaded file
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{username}.{file_extension}"
        print(f"[DEBUG] filename: {filename}")
        
        file.seek(0)
        try:
            file_bytes = file.read()
            print(f"[DEBUG] file_bytes length: {len(file_bytes)}")
            print(f"[DEBUG] Uploading to bucket: {SUPABASE_BUCKET}")
            
            # Upload with upsert=True to replace existing file
            res = current_app.supabase.storage.from_(SUPABASE_BUCKET).upload(
                filename, 
                file_bytes, 
                {
                    'content-type': file.mimetype,
                    'upsert': 'true'  # This replaces existing file with same name
                }
            )
            
            print("[DEBUG] Supabase upload response:", res)
            
            if hasattr(res, "error") and res.error:
                print("[DEBUG] Supabase upload error:", res.error)
                return None
                
            # Get public URL (bucket should now be public)
            public_url = current_app.supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
            
            # Clean up any trailing ? characters  
            if public_url.endswith('?'):
                public_url = public_url[:-1]
                
            print(f"[DEBUG] Generated public URL: {public_url}")
            
            # Verify it's actually a public URL
            if '/public/' not in public_url:
                print(f"[DEBUG] WARNING: Bucket may not be public! URL: {public_url}")
                
            return public_url
            
        except Exception as e:
            print('[DEBUG] Supabase upload exception:', e)
            return None
    else:
        print(f"[DEBUG] File not allowed or missing: {getattr(file, 'filename', None)}")
    return None