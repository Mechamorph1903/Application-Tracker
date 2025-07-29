"""
InternIn - Personal Internship Tracking Hub
Copyright © 2025 DEN. All rights reserved.
Licensed under Apache 2.0 License
"""
# "This folder is a package — and you can import from it."
import datetime
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, logout_user
from flask_mail import Mail
from datetime import date
from dotenv import load_dotenv
from sqlalchemy.orm.attributes import flag_modified
from .models import db, User
from supabase import create_client
from werkzeug.security import generate_password_hash
from .auth.routes import auth
from .profile.routes import userprofile
from .settings.routes import settings
from .applications.routes import applications
from .friends import friends
from .friends.routes import friends
import os



# Load environment variables
load_dotenv()



def create_app():
	app = Flask(__name__)
	mail = Mail(app)
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
	app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'makenaijagreatgain')  # Change this to a secure key

	# Flask-Mail configuration
	app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
	app.config['MAIL_PORT'] = 587
	app.config['MAIL_USE_TLS'] = True
	app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Set this environment variable
	app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Set this environment variable
	app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Use the same email as sender

	# Initialize Supabase client for authentication
	supabase_url = os.getenv('SUPABASE_URL')
	supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
	
	if supabase_url and supabase_service_key:
		try:
			supabase = create_client(supabase_url, supabase_service_key)
			app.supabase = supabase
			print("✅ Supabase Auth client initialized")
		except Exception as e:
			print(f"⚠️  Supabase Auth initialization failed: {e}")
			app.supabase = None
	else:
		print("⚠️  Supabase credentials not found")
		app.supabase = None

	# Print database information


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

		MOTIVATIONALS = [
			   {"message": "Every rejection is just a redirection to something better. Keep applying!", "author": "Aisha Patel", "remark": "her resume has more stamps than her passport"},
			   {"message": "Your dream job is out there, and it’s looking for someone who doesn’t give up.", "author": "Liam O’Connor", "remark": "once interviewed in pajamas by accident"},
			   {"message": "Persistence beats resistance. One more application could be the one!", "author": "Chen Wei", "remark": "has a spreadsheet longer than his thesis"},
			   {"message": "You miss 100% of the shots you don’t take. Apply anyway!", "author": "Maria Gonzalez", "remark": "sent so many cover letters, she dreams in templates"},
			   {"message": "Every ‘no’ brings you closer to a ‘yes’. Don’t lose hope!", "author": "Segun Chibuzor", "remark": "applied to Google so many times they sent him a care package for effort. Did not still get an offer."},
			   {"message": "The journey is tough, but so are you. Keep moving forward!", "author": "Elena Popov", "remark": "her inbox is a graveyard of ‘We regret to inform you’ emails"},
			   {"message": "Success is built on a mountain of rejections. Climb higher!", "author": "Priya Singh", "remark": "once got ghosted by an AI recruiter"},
			   {"message": "Your effort will pay off, even if it’s not today. Stay strong!", "author": "David Kim", "remark": "has a collection of ‘Thank you for your interest’ mugs"},
			   {"message": "Don’t let a setback set you back. Tomorrow is another chance.", "author": "Fatima Al-Farsi", "remark": "her LinkedIn is now her diary"},
			   {"message": "The best opportunities often come after the hardest struggles.", "author": "Lucas Müller", "remark": "applied to so many places, he’s on a first-name basis with HR bots"},
			   {"message": "Keep applying, keep learning, keep growing. Your time will come.", "author": "Sara Ahmed", "remark": "her motivational playlist is just recruiter voicemails"},
			   {"message": "Every application is a step closer to your breakthrough.", "author": "Tomoko Sato", "remark": "once got rejected by a company she didn’t apply to"},
			   {"message": "Don’t measure your journey by the rejections, but by your resilience.", "author": "Jean-Pierre Dubois", "remark": "his cover letter is now a cry for help"},
			   {"message": "The right job is waiting for your persistence to pay off.", "author": "Nia Johnson", "remark": "her interview suit has frequent flyer miles"},
			   {"message": "You’re not alone—every student is hustling. Keep at it!", "author": "Mateo Silva", "remark": "his reference list is longer than his resume"},
			   {"message": "Rejection is just proof you’re trying. That’s already a win.", "author": "Anya Ivanova", "remark": "once got a rejection email addressed to someone else"},
			   {"message": "Your future self will thank you for not giving up today.", "author": "Omar Hassan", "remark": "has a folder called ‘Maybe Next Year’"},
			   {"message": "Every application is a seed. Some take time to grow.", "author": "Emily Brown", "remark": "could probably start a podcast based on the number of her daily affirmations"},
			   {"message": "The job market is tough, but you’re tougher. Keep going!", "author": "Rajesh Kumar", "remark": "applied to so many jobs, his browser autofills everything"},
			   {"message": "Celebrate small wins—every step counts!", "author": "Isabella Rossi", "remark": "her cat is now her mock interviewer"},
			   {"message": "Your persistence is your superpower. Use it!", "author": "Kwame Mensah", "remark": "once got an interview invite at 3am"},
			   {"message": "Don’t let today’s ‘no’ stop tomorrow’s ‘yes’.", "author": "Sofia Petrova", "remark": "her coffee budget is now a line item in her job search spreadsheet"},
			   {"message": "You’re building skills and stories with every application.", "author": "Jin Park", "remark": "his resume has more versions than Windows"},
			   {"message": "The right fit is worth the wait. Keep searching!", "author": "Leila Haddad", "remark": "her interview shoes are now her lucky charm"},
			   {"message": "Every effort counts, even if it feels invisible now.", "author": "Carlos Ramirez", "remark": "once got a rejection in comic sans"},
			   {"message": "You’re not failing, you’re learning. That’s progress!", "author": "Mia Andersen", "remark": "her ‘apply’ button is starting to look worn out"},
			   {"message": "Stay curious, stay brave, stay applying!", "author": "Ahmed Nour", "remark": "his motivational playlist is just elevator music from hold calls"},
			   {"message": "Your journey is unique—don’t compare, just continue.", "author": "Chloe Dubois", "remark": "her dog now recognizes the Zoom ringtone"},
			   {"message": "Keep your head up—your breakthrough could be one click away.", "author": "Yusuf Demir", "remark": "once got a job offer by replying to a spam email—by accident"},
			   {"message": "You’re closer than you think. Don’t stop now!", "author": "Hannah Lee", "remark": "her calendar is just color-coded interviews and rejections"},
			   {"message": "Keep watering your dreams—one day they’ll bloom into opportunities!", "author": "Kirabo Njoroge", "remark": "her Resume, Transcript and CV have all traveled more than she has"}
		]

		def getDailyMotivation():
			index = date.today().toordinal() % len(MOTIVATIONALS)
			return MOTIVATIONALS[index]
		
		motivation = getDailyMotivation()
		goals = current_user.goals


		return render_template('home.html', stats=stats, recent_applications=recent_applications, motivation=motivation, goals=goals)
	
	@app.route('/goal', methods=['POST'])
	@login_required
	def add_goal():
		try:
			regular_goal = request.form.get("regular_goal")
			app_count_goal = request.form.get("app_count_goal")
			if regular_goal:
				goal_obj = {
					'goal_id': str(uuid.uuid4()),
					'goal-type': 'regular',
					'goal-desc': regular_goal,
					'goal-status': 'active',
					'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
					'completed_at': None
				}
				# Ensure goals is a list
				if current_user.goals is None:
					current_user.goals = []
				current_user.goals.append(goal_obj)
				db.session.commit()
				flash('Successfully added regular goal', 'success')
			elif app_count_goal:
				goal_obj = {
					'goal_id': str(uuid.uuid4()),
					'goal-type': 'count',
					'goal-desc': f'Get {app_count_goal} applications',
					'target': app_count_goal,
					'count': 0,
					'goal-status': 'active',
					'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
					'completed_at': None
				}
				
				if current_user.goals is None:
					current_user.goals = []
				current_user.goals.append(goal_obj)
				db.session.commit()
				flash("Let's hit that goal of 1!", 'success')
			else:
				flash('Error: No goal data submitted.', 'error')
		except Exception as e:
			db.session.rollback()
			print(f"Error adding goal: {e}")
			flash(f"Error adding goal: {e}", 'error')
		return redirect(url_for('home'))

	@app.route('/complete_goal', methods=['POST'])
	@login_required
	def complete_goal():
		try:
			goal_id = request.form.get('goal_id')
			if not goal_id or not current_user.goals:
				return {'success': False, 'error': 'Goal ID not provided or no goals found'}, 400
			
			for goal in current_user.goals:
				if goal.get('goal_id') == goal_id:
					goal['goal-status'] = 'completed'
					goal['completed_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
					break
			
			flag_modified(current_user, "goals")
			db.session.commit()
			return {'success': True}, 200
		except Exception as e:
			db.session.rollback()
			return {'success': False, 'error': str(e)}, 500

	@app.route('/remove_goal', methods=['POST'])
	@login_required
	def remove_goal():
		try:
			goal_id = request.form.get('goal_id')
			if not goal_id or not current_user.goals:
				return {'success': False, 'error': 'Goal ID not provided or no goals found'}, 400
			
			current_user.goals = [goal for goal in current_user.goals if goal.get('goal_id') != goal_id]
			
			flag_modified(current_user, "goals")
			db.session.commit()
			return {'success': True}, 200
		except Exception as e:
			db.session.rollback()
			return {'success': False, 'error': str(e)}, 500

	@app.route('/calendar')
	@login_required
	def calendar():
		return render_template('calendar.html')
	


	@app.route('/credits')
	def credits():
		"""Render the credits page with attributions"""
		return render_template('credits.html')
	
	@app.route('/migrate-account', methods=['GET', 'POST'])
	@login_required
	def migrate_account():
		"""Handle Supabase Auth migration for existing users"""
		if not getattr(current_user, 'needs_migration', True):
			return redirect(url_for('home'))
		
		if request.method == 'POST':
			new_password = request.form.get('password')
			confirm_password = request.form.get('confirm_password')
			
			if not new_password or len(new_password) < 6:
				flash('Password must be at least 6 characters long', 'error')
				return render_template('migrate_account.html')
				
			if new_password != confirm_password:
				flash('Passwords do not match', 'error')
				return render_template('migrate_account.html')
			
			try:
				if app.supabase:
					# Create user in Supabase Auth
					auth_user = app.supabase.auth.admin.create_user({
						"email": current_user.email,
						"password": new_password,
						"email_confirm": True,
						"user_metadata": {
							"first_name": current_user.firstName,
							"last_name": current_user.lastName,
							"username": current_user.username
						}
					})
					
					# Update local user record
					current_user.supabase_user_id = auth_user.user.id
					current_user.needs_migration = False
					current_user.password_hash = generate_password_hash(new_password)
					db.session.commit()
					
					flash('Account migrated successfully! Please log in with your new password.', 'success')
					logout_user()
					return redirect(url_for('auth.register') + '?tab=login')
				else:
					flash('Migration service unavailable. Please try again later.', 'error')
					return render_template('migrate_account.html')
					
			except Exception as e:
				flash(f'Migration failed: {str(e)}', 'error')
				return render_template('migrate_account.html')
		
		return render_template('migrate_account.html')
	
	def get_supabase_headers():
		"""Get headers for authenticated Supabase requests"""
		return {
			"apikey": os.getenv('SUPABASE_ANON_KEY', ''),
			"Authorization": f"Bearer {session.get('supabase_access_token', '')}"
		}
	
	# Make the helper function available to all routes
	app.get_supabase_headers = get_supabase_headers
	
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
