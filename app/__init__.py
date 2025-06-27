# “This folder is a package — and you can import from it.”
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import db, User
from .auth.routes import auth
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
	login_manager.login_view = 'auth.register'  # Redirect to login page if not authenticated
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))  # Load user by ID for session management
	
	# Create database tables
	with app.app_context():
		db.create_all()

	# ⬇️ Import and register the blueprint
	
	app.register_blueprint(auth, url_prefix='/auth')  # Register the auth blueprint with a URL prefix

	# Add a simple route to test the layout
	@app.route('/')
	def home():
		return render_template('layout.html')

	return app
# This function creates and configures the Flask application
