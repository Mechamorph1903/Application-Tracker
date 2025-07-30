from datetime import datetime
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
				
				# Set Supabase user ID and mark as not needing migration
				try:
					new_user.supabase_user_id = auth_user.user.id
					new_user.needs_migration = False  # New users don't need migration
					supabase_success = True
					print(f"✅ Supabase user created with ID: {auth_user.user.id}")
				except AttributeError as e:
					print(f"⚠️  Database columns not ready: {e}")
					# Columns don't exist yet, skip setting them
					pass
			else:
				print("⚠️  Supabase client not available")
				# If Supabase is not available, NEW users still don't need migration
				try:
					new_user.needs_migration = False  # They're already using the new system
				except AttributeError:
					# Column doesn't exist yet, skip
					pass
		except Exception as e:
			print(f"❌ Supabase user creation failed: {e}")
			flash(f'Account created locally, but Supabase integration failed: {str(e)}', 'warning')
			# Continue with local registration, NEW users still don't need migration
			try:
				new_user.needs_migration = False  # They're registering post-migration
			except AttributeError:
				# Column doesn't exist yet, skip
				pass

		db.session.add(new_user) # Add the new user to the session
		db.session.commit() # Commit the session to save the user to the database
		
		
	
		login_user(new_user) # Log in the user after registration

		# Send welcome email using centralized function
		current_app.send_welcome_email(user=new_user)
		
		if supabase_success:
			flash(f'Registration successful! Welcome to InternIn {new_user.username}!', 'success')
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
					app_url = current_app.config.get('APP_URL', 'http://localhost:5000')
					redirect_to = f"{app_url}/auth/reset-password-callback"
					
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
	# Get the access token and type from URL parameters
	access_token = request.args.get('access_token')
	token_type = request.args.get('type')
	
	if token_type == 'recovery' and access_token:
		# Store the recovery token in session for the password update form
		session['recovery_token'] = access_token
		flash('Please enter your new password below.', 'info')
		return render_template('reset_password.html', supabase_recovery=True)
	else:
		flash('Invalid password reset link.', 'danger')
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
