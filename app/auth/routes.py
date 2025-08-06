from datetime import datetime
import os
from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app, session
from flask_login import login_user, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST']) #GET: Display registration form, POST: Handle form submission
def register():
    if request.method == 'POST':
        """Handle user registration."""
        first_name = request.form.get('First Name')
        last_name = request.form.get('Last Name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password or not first_name or not last_name:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('auth.register') + '?tab=register')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('auth.register') + '?tab=login')

        # Create Supabase user FIRST (mandatory)
        supabase_user_id = None
        try:
            if not current_app.supabase:
                flash('Registration service unavailable. Please check your internet connection and try again.', 'danger')
                return redirect(url_for('auth.register') + '?tab=register')
            
            print(f"🔄 Creating mandatory Supabase Auth user for: {email}")
            auth_user = current_app.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "username": username,
                        "display_name": f"{first_name} {last_name}"
                    }
                }
            })
            
            # Strict validation of Supabase response
            if not auth_user:
                raise Exception("Supabase returned None response")
            
            if not hasattr(auth_user, 'user') or not auth_user.user:
                raise Exception("Supabase response missing user object")
            
            if not hasattr(auth_user.user, 'id') or not auth_user.user.id:
                raise Exception("Supabase user missing ID")
            
            supabase_user_id = auth_user.user.id
            print(f"✅ Supabase user created successfully with ID: {supabase_user_id}")
            print(f"✅ User metadata: {getattr(auth_user.user, 'user_metadata', 'No metadata')}")
            
        except Exception as e:
            print(f"❌ MANDATORY Supabase user creation failed: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            flash('Account creation failed. Please try again or contact support if the problem persists.', 'danger')
            return redirect(url_for('auth.register') + '?tab=register')

        # Only create local user if Supabase succeeded
        try:
            new_user = User(firstName=first_name, lastName=last_name, username=username, email=email)
            new_user.set_password(password)
            
            # Set Supabase fields (these should exist after migration)
            if not hasattr(new_user, 'supabase_user_id'):
                print("❌ Database missing 'supabase_user_id' column - migration needed")
                flash('Database configuration error. Please contact support.', 'danger')
                return redirect(url_for('auth.register') + '?tab=register')
            
            if not hasattr(new_user, 'needs_migration'):
                print("❌ Database missing 'needs_migration' column - migration needed")
                flash('Database configuration error. Please contact support.', 'danger')
                return redirect(url_for('auth.register') + '?tab=register')
            
            new_user.supabase_user_id = supabase_user_id
            new_user.needs_migration = False  # New users are already in Supabase
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f"✅ Local user created with supabase_user_id: {supabase_user_id}")
            
        except Exception as e:
            print(f"❌ Local user creation failed: {e}")
            # If local user creation fails, we should clean up the Supabase user
            try:
                if supabase_user_id and current_app.supabase:
                    current_app.supabase.auth.admin.delete_user(supabase_user_id)
                    print(f"🧹 Cleaned up Supabase user {supabase_user_id}")
            except Exception as cleanup_error:
                print(f"⚠️ Failed to cleanup Supabase user: {cleanup_error}")
            
            flash('Account creation failed. Please try again.', 'danger')
            return redirect(url_for('auth.register') + '?tab=register')

        # Login the user
        login_user(new_user)

        # Send welcome email
        try:
            current_app.send_welcome_email(user=new_user)
        except Exception as e:
            print(f"⚠️ Welcome email failed: {e}")
            # Don't fail registration for email issues

        flash(f'Registration successful! Welcome to InternIn {new_user.username}!', 'success')
        return redirect(url_for('home'))
    
    tab = request.args.get('tab', 'register')
    return render_template('register.html', tab=tab)  # Render the registration form with the specified tab

@auth.route('/login', methods=['POST'])
def login():
	email = request.form.get('email')
	password = request.form.get('password')

	currentUser = User.query.filter_by(email=email).first()  # Find user by email
	if currentUser and currentUser.check_password(password):
		# Check if user needs migration (handle missing column gracefully)
		try:
			needs_migration = getattr(currentUser, 'needs_migration', True)
		except AttributeError:
			# Column doesn't exist yet, assume user needs migration
			needs_migration = True
		
		if needs_migration:
			login_user(currentUser)  # Log them in temporarily
			flash('Please set a new password to complete account migration.', 'info')
			return redirect(url_for('migrate_account'))
		
		# Normal login flow for migrated users
		try:
			# Try to authenticate with Supabase to get token
			if current_app.supabase:
				auth_response = current_app.supabase.auth.sign_in_with_password({
					"email": email,
					"password": password
				})
				
				# Store Supabase token in session
				session['supabase_access_token'] = auth_response.session.access_token
				print("✅ Supabase token stored in session")
			
		except Exception as e:
			print(f"⚠️  Supabase auth error: {e}")
			# Continue with local login if Supabase fails
		
		login_user(currentUser)
		# Send welcome email for first-time login (if this is intended)
		
		currentUser.last_seen = datetime.now()
		db.session.commit()  # Commit the changes to the database
		flash('Login successful!', 'success')
		return redirect(url_for('home'))  # Redirect to dashboard after login
	else:
		flash('Invalid email or password.', 'danger')
		return redirect(url_for('auth.register') + '?tab=login')  # Stay on login tab
	
@auth.route('/logout')
def logout():
	"""Log out the current user and redirect to landing page."""
	if current_user.is_authenticated:
		current_user.last_seen = datetime.now()  # Update last seen time
		db.session.commit()
	logout_user()
	return redirect(url_for('landing'))  # Redirect to landing page after logout


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
	if request.method == 'POST':
		email = request.form.get('email')
		user = User.query.filter_by(email=email).first()
		
		if user:
			# Try Supabase password reset first
			try:
				if current_app.supabase:
					# Use Supabase's built-in password reset
					app_url = current_app.config.get('APP_URL', 'http://localhost:5000').rstrip('/')
					redirect_to = f"{app_url}/auth/reset-password-callback"  # Use proper callback URL
					
					print(f"🔄 Sending Supabase password reset to: {email}")
					print(f"🔄 Redirect URL: {redirect_to}")
					
					try:
						supabase_response = current_app.supabase.auth.reset_password_for_email(
							email, 
							{"redirect_to": redirect_to}
						)
						
						# In newer Supabase SDK, successful calls return None
						print(f"✅ Supabase password reset email sent to {email}")
						flash('Password reset link sent to your email. Please check your inbox.', 'info')
						return redirect(url_for('auth.forgot_password'))
						
					except Exception as supabase_error:
						print(f"❌ Supabase reset email failed: {supabase_error}")
						# Let it fall through to the fallback below
					
			except Exception as e:
				print(f"⚠️  Supabase password reset failed: {e}")
				# Fall back to local password reset
			
			# Fallback: Local password reset using our email system
			# try:
			# 	s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
			# 	token = s.dumps(user.email, salt='password-reset-salt')
			# 	reset_url = url_for('auth.reset_password', token=token, _external=True)
				
			# 	# Use centralized email function
			# 	success = current_app.send_password_reset_email(user.email, reset_url)
				
			# 	if success:
			# 		flash('Password reset link sent to your email.', 'info')
			# 	else:
			# 		flash('Error sending email. Please try again later.', 'danger')
					
			# except Exception as e:
			# 	print(f"❌ Local password reset error: {e}")
			# 	flash('Error processing password reset. Please try again later.', 'danger')
		else:
			# Don't reveal whether email exists or not for security
			flash('If an account with that email exists, a password reset link has been sent.', 'info')
		
		return redirect(url_for('auth.forgot_password'))
	
	return render_template('forgot_password.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
	try:
		email = s.loads(token, salt='password-reset-salt', max_age=3600)
	except Exception:
		flash('The reset link is invalid or has expired.', 'danger')
		return redirect(url_for('auth.forgot_password'))
	
	user = User.query.filter_by(email=email).first()
	if not user:
		flash('User not found.', 'danger')
		return redirect(url_for('auth.forgot_password'))
		
	if request.method == 'POST':
		new_password = request.form.get('password')
		confirm_password = request.form.get('confirm_password')
		
		if not new_password or not confirm_password:
			flash('Please fill out all fields.', 'danger')
			return render_template('reset_password.html', token=token)
			
		if new_password != confirm_password:
			flash('Passwords do not match.', 'danger')
			return render_template('reset_password.html', token=token)
			
		if len(new_password) < 6:
			flash('Password must be at least 6 characters long.', 'danger')
			return render_template('reset_password.html', token=token)
		
		# Update password in both local database and Supabase
		try:
			# Update local password
			user.set_password(new_password)
			
			# Update Supabase password if user has Supabase ID
			if current_app.supabase and hasattr(user, 'supabase_user_id'):
				try:
					current_app.supabase.auth.update_user(
						{"password": new_password},
						access_token=session['recovery_token']  # Use the recovery token

					)
					print(f"✅ Supabase password updated for user {user.email}")
				except Exception as e:
					print(f"⚠️  Supabase password update failed: {e}")
					# Continue with local update
			
			db.session.commit()
			flash('Your password has been updated! You can now log in.', 'success')
			return redirect(url_for('auth.register') + '?tab=login')
			
		except Exception as e:
			print(f"❌ Password reset error: {e}")
			flash('Error updating password. Please try again.', 'danger')
			return render_template('reset_password.html', token=token)
	
	return render_template('reset_password.html', token=token)


@auth.route('/reset-password-callback', methods=['GET'])
def reset_password_callback():
	"""Handle Supabase password reset callback"""
	# Debug: Log all parameters received
	print("=== SUPABASE CALLBACK DEBUG ===")
	print("All URL parameters:")
	for key, value in request.args.items():
		print(f"  {key}: {value}")
	print("================================")
	
	# Get all possible parameters
	access_token = request.args.get('access_token')
	refresh_token = request.args.get('refresh_token')
	token_type = request.args.get('type')
	error = request.args.get('error')
	error_description = request.args.get('error_description')
	
	# Check for errors first
	if error:
		print(f"❌ Supabase error: {error} - {error_description}")
		flash(f'Password reset error: {error_description or error}', 'danger')
		return redirect(url_for('auth.forgot_password'))
	
	# Try to find any token in the parameters
	token = access_token or refresh_token
	
	if token and token_type == 'recovery':
		print(f"✅ Recovery token found: {token[:20]}... (type: {token_type})")
		# Store the recovery token in session for the password update form
		session['recovery_token'] = token
		flash('Please enter your new password below.', 'info')
		return render_template('reset_password.html', supabase_recovery=True)
	
	# If no token found, show what we got
	print(f"❌ No valid recovery token found in parameters")
	print(f"   access_token: {access_token}")
	print(f"   refresh_token: {refresh_token}")
	print(f"   type: {token_type}")
	
	# Check if this is coming from URL fragments (common with Supabase)
	# Show a page that extracts fragment parameters using JavaScript
	if not request.args:
		print("⚠️ No query parameters - tokens might be in URL fragment")
		return render_template('auth_callback.html')
	
	# If we get here, the link is invalid
	flash('Invalid password reset link. Please request a new one.', 'danger')
	return redirect(url_for('auth.forgot_password'))


@auth.route('/update-password', methods=['POST'])
def update_password():
    """Handle Supabase password update from recovery token"""
    recovery_token = session.get('recovery_token')
    
    if not recovery_token:
        flash('Invalid session. Please request a new password reset.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    new_password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not new_password or not confirm_password:
        flash('Please fill out all fields.', 'danger')
        return render_template('reset_password.html', supabase_recovery=True)
        
    if new_password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return render_template('reset_password.html', supabase_recovery=True)
        
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long.', 'danger')
        return render_template('reset_password.html', supabase_recovery=True)
    
    try:
        if current_app.supabase:
            # Decode the recovery token to get user info
            import jwt
            
            try:
                # Decode the JWT token (without verification for now)
                decoded_token = jwt.decode(recovery_token, options={"verify_signature": False})
                user_email = decoded_token.get('email')
                user_id = decoded_token.get('sub')
                
                print(f"🔍 Recovery token contains: email={user_email}, user_id={user_id}")
                
                if not user_email or not user_id:
                    raise Exception("Invalid recovery token: missing email or user_id")
                
                # Use admin API to update the user's password
                response = current_app.supabase.auth.admin.update_user_by_id(
                    user_id,
                    {"password": new_password}
                )
                
                print(f"✅ Supabase password updated via admin API")
                
                # Also update local database
                local_user = User.query.filter_by(email=user_email).first()
                if local_user:
                    local_user.set_password(new_password)
                    db.session.commit()
                    print(f"✅ Local password updated for user {user_email}")
                
                # Clear recovery token from session
                session.pop('recovery_token', None)
                
                flash('Your password has been updated successfully! You can now log in.', 'success')
                return redirect(url_for('auth.register') + '?tab=login')
                
            except jwt.InvalidTokenError as jwt_error:
                print(f"❌ JWT decode error: {jwt_error}")
                raise Exception("Invalid recovery token format")
            except Exception as admin_error:
                print(f"❌ Admin API error: {admin_error}")
                raise Exception(f"Failed to update password: {admin_error}")
                
        else:
            flash('Password update service unavailable.', 'danger')
            return render_template('reset_password.html', supabase_recovery=True)
            
    except Exception as e:
        print(f"❌ Supabase password update error: {e}")
        flash('Error updating password. Please try again or contact support.', 'danger')
        return render_template('reset_password.html', supabase_recovery=True)


@auth.route('/test-callback')
def test_callback():
	"""Test route to verify callback URL is working"""
	app_url = os.getenv('APP_URL', 'http://localhost:5000').rstrip('/')
	return f"""
	<h2>Callback Test Route Working!</h2>
	<p>APP_URL: {app_url}</p>
	<p>Full callback URL: {app_url}/auth/reset-password-callback</p>
	<p>This URL should be configured in your Supabase dashboard under Authentication > URL Configuration > Redirect URLs</p>
	<hr>
	<h3>Current Request Info:</h3>
	<p>URL: {request.url}</p>
	<p>Base URL: {request.base_url}</p>
	<p>Host: {request.host}</p>
	<hr>
	<p><a href="{url_for('auth.forgot_password')}">Test Password Reset</a></p>
	"""


@auth.route('/debug-callback')
def debug_callback():
	"""Debug route to see exactly what parameters are received"""
	params_html = "<h3>URL Parameters:</h3><ul>"
	for key, value in request.args.items():
		params_html += f"<li><strong>{key}:</strong> {value}</li>"
	params_html += "</ul>"
	
	if not request.args:
		params_html = "<p>No parameters received</p>"
	
	return f"""
	<h2>Debug Callback Route</h2>
	{params_html}
	<hr>
	<p>Full URL: {request.url}</p>
	<p>If you got here from a Supabase reset link, we can see what parameters it sent!</p>
	<hr>
	<p><a href="{url_for('auth.reset_password_callback', **request.args)}">Try Real Callback</a></p>
	"""
