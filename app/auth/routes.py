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

		new_user = User(firstName=first_name, lastName=last_name, username=username, email=email)
		new_user.set_password(password)

		# Try to create user in Supabase Auth for new registrations
		supabase_success = False
		try:
			if current_app.supabase:
				print(f"🔄 Creating Supabase Auth user for: {email}")
				auth_user = current_app.supabase.auth.admin.create_user({
					"email": email,
					"password": password,
					"email_confirm": True,
					"user_metadata": {
						"first_name": first_name,
						"last_name": last_name,
						"username": username
					}
				})
				
				# Validate Supabase response
				if not auth_user or not hasattr(auth_user, 'user') or not auth_user.user:
					raise Exception("Invalid Supabase response: auth_user is None or missing user")
				
				if not hasattr(auth_user.user, 'id') or not auth_user.user.id:
					raise Exception("Invalid Supabase response: user.id is missing")
				
				# Set Supabase user ID and mark as not needing migration
				supabase_user_id = auth_user.user.id
				print(f"🔄 Setting supabase_user_id to: {supabase_user_id}")
				
				# Check if database columns exist before setting them
				if not hasattr(new_user, 'supabase_user_id'):
					raise Exception("Database column 'supabase_user_id' does not exist - database migration needed")
				if not hasattr(new_user, 'needs_migration'):
					raise Exception("Database column 'needs_migration' does not exist - database migration needed")
				
				new_user.supabase_user_id = supabase_user_id
				new_user.needs_migration = False  # New users don't need migration
				supabase_success = True
				print(f"✅ Supabase user created with ID: {supabase_user_id}")
				print(f"✅ Local user fields set: supabase_user_id={new_user.supabase_user_id}, needs_migration={new_user.needs_migration}")
				
			else:
				print("⚠️  Supabase client not available - likely missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
				# If Supabase is not available, NEW users still don't need migration
				if hasattr(new_user, 'needs_migration'):
					new_user.needs_migration = False  # They're already using the new system
					supabase_success = True  # Consider this successful for new users without Supabase
					print("ℹ️  Marked new user as not needing migration (no Supabase)")
				else:
					print("⚠️  Database column 'needs_migration' does not exist - treating as success anyway")
					supabase_success = True  # Still consider successful for new users
		except Exception as e:
			print(f"❌ Supabase user creation failed: {e}")
			print(f"❌ Error details: {type(e).__name__}: {str(e)}")
			# Continue with local registration, NEW users still don't need migration
			if hasattr(new_user, 'needs_migration'):
				new_user.needs_migration = False  # They're registering post-migration
				supabase_success = True  # Consider successful for new users even without Supabase
				print("ℹ️  Marked new user as not needing migration (Supabase failed)")
			else:
				print("⚠️  Database column 'needs_migration' does not exist - treating as success anyway")
				supabase_success = True  # Still consider successful for new users

		db.session.add(new_user) # Add the new user to the session
		db.session.commit() # Commit the session to save the user to the database
		
		
	
		login_user(new_user) # Log in the user after registration

		# Send welcome email using centralized function
		current_app.send_welcome_email(user=new_user)
		
		if supabase_success:
			if current_app.supabase:
				flash(f'Registration successful! Welcome to InternIn {new_user.username}!', 'success')
			else:
				flash(f'Registration successful! Welcome to InternIn {new_user.username}! (Running in local mode)', 'success')
		else:
			flash('Registration successful! You may need to migrate your account later for full functionality.', 'warning')
		
		import os
		print("DB Path:", os.path.abspath("internships.db"))

		return redirect(url_for('home'))  # Redirect to dashboard after registration
	
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
					redirect_to = f"{app_url}/auth/debug-callback"  # Use debug callback first
					
					print(f"🔄 Sending Supabase password reset to: {email}")
					print(f"🔄 Redirect URL: {redirect_to}")
					
					supabase_response = current_app.supabase.auth.reset_password_email(
						email, 
						{"redirect_to": redirect_to}
					)
					
					print(f"✅ Supabase password reset email sent to {email}")
					flash('Password reset link sent to your email. Please check your inbox.', 'info')
					return redirect(url_for('auth.forgot_password'))
					
			except Exception as e:
				print(f"⚠️  Supabase password reset failed: {e}")
				# Fall back to local password reset
			
			# Fallback: Local password reset using our email system
			try:
				s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
				token = s.dumps(user.email, salt='password-reset-salt')
				reset_url = url_for('auth.reset_password', token=token, _external=True)
				
				# Use centralized email function
				success = current_app.send_password_reset_email(user.email, reset_url)
				
				if success:
					flash('Password reset link sent to your email.', 'info')
				else:
					flash('Error sending email. Please try again later.', 'danger')
					
			except Exception as e:
				print(f"❌ Local password reset error: {e}")
				flash('Error processing password reset. Please try again later.', 'danger')
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
			if current_app.supabase and hasattr(user, 'supabase_user_id') and user.supabase_user_id:
				try:
					current_app.supabase.auth.admin.update_user_by_id(
						user.supabase_user_id,
						{"password": new_password}
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
	
	# Also check for fragment parameters (sometimes sent after #)
	fragment = request.args.get('fragment') or request.args.get('hash')
	
	# Check for errors first
	if error:
		print(f"❌ Supabase error: {error} - {error_description}")
		flash(f'Password reset error: {error_description or error}', 'danger')
		return redirect(url_for('auth.forgot_password'))
	
	# Try to find any token in the parameters
	token = access_token or refresh_token
	
	if token:
		print(f"✅ Token found: {token[:20]}... (type: {token_type})")
		# Store the recovery token in session for the password update form
		session['recovery_token'] = token
		flash('Please enter your new password below.', 'info')
		return render_template('reset_password.html', supabase_recovery=True)
	
	# If no token found, show what we got
	print(f"❌ No valid token found in parameters")
	print(f"   access_token: {access_token}")
	print(f"   refresh_token: {refresh_token}")
	print(f"   type: {token_type}")
	
	# Temporary: Accept ANY callback and show the reset form to test
	if request.args:
		print("⚠️ Accepting callback anyway for testing...")
		session['recovery_token'] = 'test_token'
		flash('Testing mode: Please enter your new password below.', 'warning')
		return render_template('reset_password.html', supabase_recovery=True)
	
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
			# Update password using recovery token
			response = current_app.supabase.auth.update_user(
				{"password": new_password},
				access_token=recovery_token
			)
			
			# Also update local database if user exists
			user_email = response.user.email
			local_user = User.query.filter_by(email=user_email).first()
			if local_user:
				local_user.set_password(new_password)
				db.session.commit()
			
			# Clear recovery token from session
			session.pop('recovery_token', None)
			
			flash('Your password has been updated successfully! You can now log in.', 'success')
			return redirect(url_for('auth.register') + '?tab=login')
		else:
			flash('Password update service unavailable.', 'danger')
			return render_template('reset_password.html', supabase_recovery=True)
			
	except Exception as e:
		print(f"❌ Supabase password update error: {e}")
		flash('Error updating password. Please try again.', 'danger')
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
