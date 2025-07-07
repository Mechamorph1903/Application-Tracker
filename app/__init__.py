# "This folder is a package — and you can import from it."
import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from .models import db, User
from .auth.routes import auth
from .profile.routes import userprofile
from .settings.routes import settings
from .applications.routes import applications

import os

def create_app():
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'internships.db') # local DB
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable track modifications to save resources
	app.config['SECRET_KEY'] = 'Tinubu'  # Change this to a secure key

	
	db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
	print("Database file will be at:", os.path.abspath(db_path))


	# Initialize extensions
	db.init_app(app)
	login_manager = LoginManager()
	login_manager.login_view = 'landing'  # Redirect to landing page if not authenticated
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))  # Load user by ID for session management
	
	# Create database tables
	with app.app_context():
		db.create_all()

	# ⬇️ Import and register the blueprint
	
	app.register_blueprint(auth, url_prefix='/auth')  # Register the auth blueprint with a URL prefix
	app.register_blueprint(userprofile, url_prefix='/profile')  # Register the user profile blueprint with a URL prefix
	app.register_blueprint(settings)  # Register the settings blueprint without prefix
	app.register_blueprint(applications, url_prefix='/applications')  # Register the internships blueprint

	@app.route('/')
	def landing():
		return render_template('landing.html')
	
	@app.route('/home')
	@app.route('/dashboard')
	@login_required
	def home():
		return render_template('home.html')
	
	@app.route('/calendar')
	@login_required
	def calendar():
		return render_template('calendar.html')
	
	
	
	@app.route('/friends')
	@login_required
	def friends():
		return render_template('friends.html')
	
	@app.route('/profile')
	@login_required
	def profile():
		return render_template('profile.html', user=current_user)
	
	@app.route('/credits')
	def credits():
		"""Render the credits page with attributions"""
		return render_template('credits.html')
	

	# user statuses
	@app.before_request
	def track_user_activity():
		"""Update user's last_seen on every request"""
		if current_user.is_authenticated:
			current_user.last_seen = datetime.datetime.now(datetime.timezone.utc)
			db.session.commit()  # Commit the changes to the database

	return app
# This function creates and configures the Flask application
