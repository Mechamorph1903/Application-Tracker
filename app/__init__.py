"""
InternIn - Personal Internship Tracking Hub
Copyright © 2025 DEN. All rights reserved.
Licensed under Apache 2.0 License
"""

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
	login_manager.login_view = 'auth.register'  # Redirect to login/register page if not authenticated
	login_manager.login_message = 'Please log in to access this page.'
	login_manager.login_message_category = 'info'
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
	app.register_blueprint(settings, url_prefix='/settings')  # Register the settings blueprint with settings prefix
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
	
	@app.route('/acquaintance')
	@login_required
	def limited_profile():
		return render_template('acquaintance.html')
	
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
	
	@app.template_filter('social_icon')
	def get_social_icon(platform):
		"""Get Font Awesome icon class for social media platform"""
		icons = {
			'LinkedIn': 'fa-brands fa-linkedin',
			'GitHub': 'fa-brands fa-github',
			'Facebook': 'fa-brands fa-facebook',
			'Instagram': 'fa-brands fa-instagram',
			'Twitter': 'fa-brands fa-twitter',
			'YouTube': 'fa-brands fa-youtube',
			'Discord': 'fa-brands fa-discord',
			'Twitch': 'fa-brands fa-twitch',
			'DeviantArt': 'fa-brands fa-deviantart',
			'Steam': 'fa-brands fa-steam',
			'Xbox': 'fa-brands fa-xbox',
			'PlayStation': 'fa-brands fa-playstation',
			'Nintendo': 'fa-solid fa-gamepad',
			'Personal Website': 'fa-solid fa-globe'
		}
		return icons.get(platform, 'fa-solid fa-link')
	
	@app.template_filter('initials')
	def get_user_initials(user):
		"""Get user initials from first and last name"""
		if not user or not hasattr(user, 'firstName') or not hasattr(user, 'lastName'):
			return 'U'
		
		first_initial = user.firstName[0].upper() if user.firstName else ''
		last_initial = user.lastName[0].upper() if user.lastName else ''
		
		return first_initial + last_initial if first_initial and last_initial else 'U'
	
	@app.template_filter('safe_date')
	def safe_date_format(date_obj, format_str='%B %d, %Y'):
		"""Safely format a date object, return 'Never' if None or invalid"""
		try:
			if date_obj:
				return date_obj.strftime(format_str)
			return 'Never'
		except (AttributeError, ValueError):
			return 'Never'
	

	# user statuses
	@app.before_request
	def track_user_activity():
		"""Update user's last_seen on every request"""
		if current_user.is_authenticated:
			current_user.last_seen = datetime.datetime.now(datetime.timezone.utc)
			db.session.commit()  # Commit the changes to the database

	return app
# This function creates and configures the Flask application
