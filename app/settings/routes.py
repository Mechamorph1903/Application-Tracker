from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, send_file, current_app
from flask_login import current_user, login_required
from app.models import db, User, UserSettings, Internship
import json
import csv
import io
import os
import uuid
import base64
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from PIL import Image

from supabase import create_client
from dotenv import load_dotenv

load_dotenv(override=True)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'profile-pics')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Try to import pandas for Excel export, fallback to CSV if not available
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# File upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

settings = Blueprint('settings', __name__)

@settings.route('/', methods=['GET', 'POST'])
@login_required
def settings_page():
    # Ensure user has settings
    if not current_user.settings:
        current_user.create_user_settings()
    
    return render_template('settings.html', user=current_user, pandas_available=PANDAS_AVAILABLE)

@settings.route('/update-user-settings', methods=['POST'])
@login_required
def update_user_settings():
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
                
                # Store old profile picture URL to potentially delete later
                old_profile_picture = current_user.profile_picture
                
                # Save to Supabase
                print("[DEBUG] Calling upload_profile_picture_to_supabase...")
                supa_url = upload_profile_picture_to_supabase(file, current_user.id)
                print(f"[DEBUG] supa_url returned: {supa_url}")
                if supa_url:
                    # Update user's profile picture (this overrides any existing one in database)
                    current_user.profile_picture = supa_url
                    
                    # Optional: Delete old file from Supabase storage to save space
                    if old_profile_picture and old_profile_picture != 'default.jpg' and old_profile_picture.startswith('http'):
                        try:
                            # Extract filename from old URL for deletion
                            old_filename = old_profile_picture.split('/')[-1]
                            if old_filename:
                                supabase.storage.from_(SUPABASE_BUCKET).remove([old_filename])
                                print(f"[DEBUG] Deleted old profile picture: {old_filename}")
                        except Exception as e:
                            print(f"[DEBUG] Could not delete old profile picture: {e}")
                else:
                    print("[DEBUG] Failed to upload to Supabase or invalid file type.")
                    return jsonify({'success': False, 'error': 'Failed to upload to Supabase or invalid file type.'}), 400
        
        # Update User model fields
        current_user.firstName = request.form.get('firstName', current_user.firstName)
        current_user.lastName = request.form.get('lastName', current_user.lastName)
        current_user.username = request.form.get('username', current_user.username)
        current_user.email = request.form.get('email', current_user.email)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.bio = request.form.get('bio', current_user.bio)
        current_user.school = request.form.get('school', current_user.school)
        current_user.year = request.form.get('year', current_user.year)
        current_user.major = request.form.get('major', current_user.major)
        
        # Handle social media JSON
        if 'social_media' in request.form:
            try:
                social_media_json = request.form.get('social_media', '[]')
                current_user.social_media = json.loads(social_media_json)
            except json.JSONDecodeError:
                current_user.social_media = []
        
        # Ensure user has settings
        if not current_user.settings:
            current_user.create_user_settings()
        
        # Update UserSettings model fields
        current_user.settings.profile_visibility = request.form.get('profile_visibility', current_user.settings.profile_visibility)
        current_user.settings.show_application_stats = request.form.get('show_application_stats') == 'true'
        current_user.settings.timezone = request.form.get('timezone', current_user.settings.timezone)
        current_user.settings.two_factor_enabled = request.form.get('two_factor_enabled') == 'true'
        current_user.settings.login_notifications = request.form.get('login_notifications') == 'true'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User settings updated successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings.route('/upload-cropped-profile-picture', methods=['POST'])
@login_required
def upload_cropped_profile_picture():
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
        
        # Store old profile picture URL
        old_profile_picture = current_user.profile_picture
        
        # Create a unique filename
        file_extension = 'jpg'  # We'll standardize cropped images as JPG
        unique_filename = f"{current_user.id}_cropped_{uuid.uuid4().hex}.{file_extension}"
        
        # Upload to Supabase
        try:
            res = supabase.storage.from_(SUPABASE_BUCKET).upload(
                unique_filename, 
                image_bytes, 
                {'content-type': 'image/jpeg'}
            )
            
            if hasattr(res, "error") and res.error:
                print("[DEBUG] Supabase upload error:", res.error)
                return jsonify({'success': False, 'error': 'Failed to upload cropped image'}), 500
            
            # Get public URL
            public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(unique_filename)
            
            # Update user's profile picture
            current_user.profile_picture = public_url
            db.session.commit()
            
            # Delete old profile picture from storage
            if old_profile_picture and old_profile_picture != 'default.jpg' and old_profile_picture.startswith('http'):
                try:
                    old_filename = old_profile_picture.split('/')[-1]
                    if old_filename:
                        supabase.storage.from_(SUPABASE_BUCKET).remove([old_filename])
                        print(f"[DEBUG] Deleted old profile picture: {old_filename}")
                except Exception as e:
                    print(f"[DEBUG] Could not delete old profile picture: {e}")
            
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
@login_required
def update_app_settings():
    """Update application preferences"""
    try:
        # Ensure user has settings
        if not current_user.settings:
            current_user.create_user_settings()
        
        # Update app settings
        current_user.settings.theme = request.form.get('theme', current_user.settings.theme)
        current_user.settings.dashboard_layout = request.form.get('dashboard_layout', current_user.settings.dashboard_layout)
        current_user.settings.items_per_page = int(request.form.get('items_per_page', current_user.settings.items_per_page))
        current_user.settings.date_format = request.form.get('date_format', current_user.settings.date_format)
        current_user.settings.time_format = request.form.get('time_format', current_user.settings.time_format)
        
        # Notification settings
        current_user.settings.email_notifications = request.form.get('email_notifications') == 'true'
        current_user.settings.friend_request_notifications = request.form.get('friend_request_notifications') == 'true'
        current_user.settings.application_reminders = request.form.get('application_reminders') == 'true'
        current_user.settings.interview_reminders = request.form.get('interview_reminders') == 'true'
        current_user.settings.reminder_days_before_followup = int(request.form.get('reminder_days_before_followup', current_user.settings.reminder_days_before_followup))
        
        # Application tracking settings
        current_user.settings.auto_archive_rejected = request.form.get('auto_archive_rejected') == 'true'
        current_user.settings.default_application_status = request.form.get('default_application_status', current_user.settings.default_application_status)
        
        # Data settings
        current_user.settings.auto_backup = request.form.get('auto_backup') == 'true'
        current_user.settings.export_format = request.form.get('export_format', current_user.settings.export_format)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'App settings updated successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@settings.route('/export-internships')
@login_required
def export_internships():
    """Export user's internships based on their preferred format"""
    try:
        # Get user's internships
        internships = Internship.query.filter_by(user_id=current_user.id).all()
        
        # Get export format preference
        export_format = current_user.settings.export_format if current_user.settings else 'csv'
        
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
@login_required
def change_password():
    """Change user's password"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        # Check if current password is correct
        if not current_user.check_password(current_password):
            return jsonify({'success': False, 'error': 'Current password is incorrect'}), 400
        
        # Check if new passwords match
        if new_password != confirm_password:
            return jsonify({'success': False, 'error': 'New passwords do not match'}), 400
        
        # Validate new password strength
        if len(new_password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'}), 400
        
        # Check if new password is different from current
        if current_user.check_password(new_password):
            return jsonify({'success': False, 'error': 'New password must be different from current password'}), 400
        
        # Update password
        current_user.set_password(new_password)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Password changed successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Helper functions for file upload
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- DEBUG ENHANCED ---
def upload_profile_picture_to_supabase(file, user_id):
    """Upload profile picture to Supabase Storage and return public URL"""
    print("[DEBUG] upload_profile_picture_to_supabase called")
    print(f"[DEBUG] supabase is None: {supabase is None}")
    print(f"[DEBUG] file: {file}")
    if not supabase:
        print("[DEBUG] Supabase client is not initialized!")
        return None
    if file and allowed_file(file.filename):
        print(f"[DEBUG] Allowed file: {file.filename}")
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{user_id}_{uuid.uuid4().hex}.{file_extension}"
        print(f"[DEBUG] unique_filename: {unique_filename}")
        file.seek(0)
        try:
            file_bytes = file.read()
            print(f"[DEBUG] file_bytes length: {len(file_bytes)}")
            print(f"[DEBUG] Uploading to bucket: {SUPABASE_BUCKET}")
            res = supabase.storage.from_(SUPABASE_BUCKET).upload(unique_filename, file_bytes, {'content-type': file.mimetype})
            print("[DEBUG] Supabase upload response:", res)
            if hasattr(res, "error") and res.error:
                print("[DEBUG] Supabase upload error:", res.error)
                return None
            if hasattr(res, "data") and res.data is None:
                print("[DEBUG] Supabase upload failed, no data returned.")
                return None
            public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(unique_filename)
            print(f"[DEBUG] public_url: {public_url}")
            return public_url
        except Exception as e:
            print('[DEBUG] Supabase upload exception:', e)
            return None
    else:
        print(f"[DEBUG] File not allowed or missing: {getattr(file, 'filename', None)}")
    return None