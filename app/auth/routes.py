from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user
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
		currentUser.online_status = 'online'
		currentUser.last_seen = datetime.now()
		db.session.commit()  # Commit the changes to the database
		flash('Login successful!', 'success')
		return redirect(url_for('home'))  # Redirect to dashboard after login
	else:
		flash('Invalid email or password.', 'danger')
		return redirect(url_for('auth.register') + '?tab=login')  # Stay on login tab
	

from flask_login import current_user

@auth.route('/logout')
def logout():
	"""Log out the current user and redirect to landing page."""
	if current_user.is_authenticated:
		current_user.online_status = 'offline'  # Update user's online status
		current_user.last_seen = datetime.now()  # Update last seen time
		db.session.commit()
	logout_user()
	return redirect(url_for('landing'))  # Redirect to landing page after logout