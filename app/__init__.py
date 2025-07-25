"""
InternIn - Personal Internship Tracking Hub
Copyright © 2025 DEN. All rights reserved.
Licensed under Apache 2.0 License
"""

# "This folder is a package — and you can import from it."
import datetime
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail
from dotenv import load_dotenv
from .models import db, User
from .auth.routes import auth
from .profile.routes import userprofile
from .settings.routes import settings
from .applications.routes import applications
from .friends import friends
from .friends.routes import friends

import os

mail = Mail()

# Load environment variables
load_dotenv()

def create_app():
	app = Flask(__name__)
	# Configure database connection - prioritize Supabase for dynamic sync
	force_supabase = os.getenv('FORCE_SUPABASE', 'False').lower() == 'true'
	database_url = os.getenv('SUPABASE_DATABASE_URL')
	
	if database_url and (force_supabase or not os.path.exists(os.path.join(app.instance_path, 'internships.db'))):
		try:
			# Test Supabase PostgreSQL connection
			import psycopg2
			test_conn = psycopg2.connect(database_url, connect_timeout=10)
			test_conn.close()
			
			app.config['SQLALCHEMY_DATABASE_URI'] = database_url
			app.config['USE_SUPABASE'] = True
			print("✅ Connected to Supabase PostgreSQL (Dynamic Sync Enabled)")
			
		except ImportError:
			print("⚠️  psycopg2 not available, using SQLite")
			app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'internships.db')
			app.config['USE_SUPABASE'] = False
		except Exception as e:
			# PostgreSQL connection failed, use SQLite
			print(f"⚠️  PostgreSQL connection failed: {e}")
			print("📁 Falling back to SQLite database")
			app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'internships.db')
			app.config['USE_SUPABASE'] = False
	else:
		# Use SQLite for local development
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'internships.db')
		app.config['USE_SUPABASE'] = False
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable track modifications to save resources
	app.config['SECRET_KEY'] = 'Tinubu'  # Change this to a secure key

	# Flask-Mail configuration
	app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
	app.config['MAIL_PORT'] = 587
	app.config['MAIL_USE_TLS'] = True
	app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Set this environment variable
	app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Set this environment variable
	app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Use the same email as sender

	# Print database information
	db_uri = app.config['SQLALCHEMY_DATABASE_URI']
	if 'sqlite' in db_uri:
		db_path = db_uri.replace('sqlite:///', '')
		print("Database file will be at:", os.path.abspath(db_path))
	else:
		print("Database URI:", db_uri[:50] + "..." if len(db_uri) > 50 else db_uri)



	# Initialize extensions
	db.init_app(app)
	login_manager = LoginManager()
	login_manager.login_view = 'auth.register'  # Redirect to login/register page if not authenticated
	login_manager.login_message = 'Please log in to access this page.'
	login_manager.login_message_category = 'info'
	login_manager.init_app(app)
	mail.init_app(app)

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
	app.register_blueprint(friends, url_prefix='/friends')  # Register the friends blueprint

	@app.route('/')
	def landing():
		return render_template('landing.html')
	
	@app.route('/home')
	@app.route('/dashboard')
	@login_required
	def home():
		# Get user's applications for dashboard
		applications = current_user.internships
		
		# Get recent applications (5 most recent)
		recent_applications = []
		if applications:
			try:
				recent_applications = sorted(
					[app for app in applications if app.applied_date], 
					key=lambda x: x.applied_date, 
					reverse=True
				)[:5]
			except Exception as e:
				print(f"Error sorting applications: {e}")
				recent_applications = list(applications)[:5]
		
		# Quick stats for dashboard
		total_applications = len(applications)
		status_counts = {}
		for app in applications:
			status = app.application_status.lower() if app.application_status else ''
			status_counts[status] = status_counts.get(status, 0) + 1
		# Case-insensitive and robust interview/offer stats
		interviews = 0
		for key in status_counts:
			if key in ['interview', 'interviewing', 'interview scheduled']:
				interviews += status_counts[key]
		offers = 0
		for key in status_counts:
			if key in ['offer', 'offered', 'accepted']:
				offers += status_counts[key]
		
		stats = {
			'total_applications': total_applications,
			'interviews': interviews,
			'offers': offers,
			'pending': status_counts.get('applied', 0) + status_counts.get('under review', 0)
		}
		
		return render_template('home.html', stats=stats, recent_applications=recent_applications)
	
	@app.route('/calendar')
	@login_required
	def calendar():
		return render_template('calendar.html')
	


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
	
	@app.template_filter('nl2br')
	def nl2br_filter(text):
		"""Convert newlines to HTML line breaks"""
		if text:
			return text.replace('\n', '<br>\n').replace('\r\n', '<br>\n')
		return text
	

	# user statuses
	@app.before_request
	def track_user_activity():
		"""Update user's last_seen on every request"""
		if current_user.is_authenticated:
			current_user.last_seen = datetime.datetime.now(datetime.timezone.utc)
			db.session.commit()  # Commit the changes to the database

	return app
# This function creates and configures the Flask application
