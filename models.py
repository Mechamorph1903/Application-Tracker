from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy for  ORM functionality
from datetime import date # Import date for timestamping
from flask_login import UserMixin	# Import UserMixin for user management
from werkzeug.security import generate_password_hash, check_password_hash # Import generate_password_hash for password hashing and check_password_hash for password verification

db = SQLAlchemy()  # Initialize the SQLAlchemy object

class User(db.Model, UserMixin): # User model for managing user data
	id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each user
	username = db.Column(db.String(150), nullable=False, unique=True)  # Username must be unique
	email = db.Column(db.String(150), nullable=False)  # email for the user
	password_hash = db.Column(db.String(256), nullable=False) # Hashed password for security
	is_admin = db.Column(db.Boolean, default=False) # Flag to indicate if the user is an admin

	internships = db.relationship('Internship', backref='user', lazy=True) # One-to-many relationship with Internship model

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class Internship(db.Model): # Internship model for managing internship applications
	id = db.Column(db.Integer, primary_key=True) # Unique identifier for each internship application
	company_name = db.Column(db.String(100), nullable=False) # Name of the company offering the internship
	position = db.Column(db.String(100), nullable=False) # Position title for the internship
	application_status = db.Column(db.String(50), nullable=False, default='Applied') # Status of the application (e.g., Applied, Interviewing, Offered, Rejected)
	applied_date = db.Column(db.Date, default=date.today) # Date when the application was submitted
	status_change_date = db.Column(db.Date, default=date.today) # Date when the application status was last changed
	notes = db.Column(db.Text) # Additional notes about the internship application
	
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign key linking to the User model

	def to_dict(self):
		return {
			"id": self.id,
			"company_name": self.company_name,
			"position": self.position,
			"application_status": self.application_status,
			"applied_date": self.applied_date.strftime('%Y-%m-%d'),
			"status_change_date": self.status_change_date.strftime('%Y-%m-%d'),
			"notes": self.notes
		}