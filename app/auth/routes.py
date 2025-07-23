from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app
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

		db.session.add(new_user) # Add the new user to the session
		db.session.commit() # Commit the session to save the user to the database
		login_user(new_user) # Log in the user after registration
		flash('Registration successful! You are now logged in.')
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
		login_user(currentUser)
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
		from app import mail
		s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
		email = request.form.get('email')
		user = User.query.filter_by(email=email).first()
		if user:
			token = s.dumps(user.email, salt='password-reset-salt')
			reset_url = url_for('auth.reset_password', token=token, _external=True)
			# Send email
			msg = Message(
				subject='Password Reset - InternIn',
				recipients=[user.email],
				sender=current_app.config.get('MAIL_DEFAULT_SENDER', email)
			)
			msg.body = (
				f"Hello {user.firstName},\n\n"
				f"You requested a password reset. Click the link below to reset your password:\n\n"
				f"{reset_url}\n\n"
				"This link will expire in 1 hour.\n\n"
				"If you did not request this, please ignore this email.\n\n"
				"Best regards,\nInternIn Team"
			)
			try:
				mail.send(msg)
				flash('Password reset link sent to your email.', 'info')
			except Exception as e:
				print("Error sending email:", e)
				flash('Error sending email. Please try again later.', 'danger')
		else:
			flash('Email not found.', 'danger')
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
			
		user.set_password(new_password)
		db.session.commit()
		flash('Your password has been updated! You can now log in.', 'success')
		return redirect(url_for('auth.register') + '?tab=login')
	
	return render_template('reset_password.html', token=token)
