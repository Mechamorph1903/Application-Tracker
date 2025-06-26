from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST']) #GET: Display registration form, POST: Handle form submission
def register():
	if request.method == 'POST':
		username = request.form.get('username')
		email = request.form.get('email')
		password = request.form.get('password')

		if not username or not email or not password:
			flash('Please fill out all fields.', 'danger')
			return redirect(url_for('auth.register'))
		
		if User.query.filter_by(email=email).first():
			flash('Email already registered. Please log in.', 'danger')
			return redirect(url_for('auth.register'))
		
		new_user = User(username=username, email=email)
		new_user.set_password(password)

		db.session.add(new_user) # Add the new user to the session
		db.session.commit() # Commit the session to save the user to the database

		login_user(new_user) # Log in the user after registration

		flash('Registration successful! You are now logged in.')
		import os
		print("DB Path:", os.path.abspath("internships.db"))

		return redirect(url_for('auth.register'))  # Later change this to go to dashboard
	tab = request.args.get('tab', 'register')
	return render_template('register.html', tab=tab)  # Render the registration form with the specified tab	

@auth.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')

		currentUser = User.query.filter_by(email=email).first()  # Find user by email

		if currentUser and currentUser.check_password(password):
			login_user(currentUser)
			flash('Login successful!', 'success')
			return redirect(url_for('auth.register', tab = 'login'))  # Redirect to ddashboard page later
		else:
			flash('Invalid email or password.', 'danger')
			return redirect(url_for('auth.register', tab ='login'))  # Redirect to login tab
	
	# GET request - show login form
	tab = request.args.get('tab', 'login')
	return render_template('register.html', tab=tab)