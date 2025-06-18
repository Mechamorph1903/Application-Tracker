# “This folder is a package — and you can import from it.”
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import db, User

def create_app():
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///internships.db'  # local DB
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable track modifications to save resources
	app.config['SECRET_KEY'] = 'Tinubu'  # Change this to a secure key

	# Initialize extensions
	db.init_app(app)

	login_manager = LoginManager()
	login_manager.login_view = 'login'  # Redirect to login page if not authenticated
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))  # Load user by ID for session management
	
	  # Create database tables
	with app.app_context():
		db.create_all()

	return app
# This function creates and configures the Flask application
