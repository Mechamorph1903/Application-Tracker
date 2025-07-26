from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy for  ORM functionality
from datetime import date, datetime, timezone # Import date for timestamping and datetime
from flask_login import UserMixin	# Import UserMixin for user management
from werkzeug.security import generate_password_hash, check_password_hash # Import generate_password_hash for password hashing and check_password_hash for password verification

db = SQLAlchemy()  # Initialize the SQLAlchemy object

class User(db.Model, UserMixin): # User model for managing user data
	__tablename__ = 'users'  # Use plural table name to match existing Supabase data
	id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each user
	firstName = db.Column(db.String(100), nullable=False)  # First name of the user
	lastName = db.Column(db.String(100), nullable=False)  # Last name of the user
	username = db.Column(db.String(150), nullable=False, unique=True)  # Username must be unique
	email = db.Column(db.String(150), nullable=False)  # email for the user
	password_hash = db.Column(db.String(256), nullable=False) # Hashed password for security
	password_changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) # When password was last changed
	is_admin = db.Column(db.Boolean, default=False) # Flag to indicate if the user is an admin
	profile_picture = db.Column(db.String(150), default='default.jpg') # Path to the user's profile picture
	
	# contact fields for friends to see
	phone = db.Column(db.String(20)) # Phone number for contact
	social_media = db.Column(db.JSON, default=lambda: []) # Social media profile URLs
	bio = db.Column(db.Text) # Personal bio/description
	school = db.Column(db.String(100)) # University/school name
	year = db.Column(db.String(100)) # Graduation year
	major = db.Column(db.String(100)) # Field of study
	created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) # When user registered
	
	last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # When user was last active
	
	# Relationships
	settings = db.relationship('UserSettings', backref='user', uselist=False, lazy=True)
	internships = db.relationship('Internship', backref='user', lazy=True) # One-to-many relationship with Internship model

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
		self.password_changed_at = datetime.now(timezone.utc)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	def __repr__(self):
		return f'<User {self.username}>'
		
	@property
	def parsed_social_media(self):
		"""Return social media as a Python list, parsing JSON string if needed"""
		if not self.social_media:
			return []
		
		# If it's already a list, return it
		if isinstance(self.social_media, list):
			return self.social_media
		
		# If it's a string, try to parse it as JSON
		if isinstance(self.social_media, str):
			try:
				import json
				return json.loads(self.social_media)
			except (json.JSONDecodeError, TypeError):
				return []
		
		# Default to empty list
		return []

	def get_social_icon(self, platform):
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




	# User settings management
	
	def create_user_settings(self):
		"""Create default settings for this user if they don't exist"""
		if not self.settings:
			UserSettings.create_default_settings(self.id)
	
	def get_or_create_settings(self):
		"""Get user settings, create if they don't exist"""
		if not self.settings:
			self.create_user_settings()
		return self.settings
	
	# Friend helper methods
	def get_friends(self):
		"""Get all accepted friends"""
		sent_friends = db.session.query(User).join(
			FriendRequest, (FriendRequest.receiver_id == User.id)
		).filter(
			FriendRequest.sender_id == self.id,
			FriendRequest.status == 'accepted'
		).all()
		
		received_friends = db.session.query(User).join(
			FriendRequest, (FriendRequest.sender_id == User.id)
		).filter(
			FriendRequest.receiver_id == self.id,
			FriendRequest.status == 'accepted'
		).all()
		
		return list(set(sent_friends + received_friends))
	
	def is_friend_with(self, user):
		"""Check if this user is friends with another user"""
		return FriendRequest.query.filter(
			((FriendRequest.sender_id == self.id) & (FriendRequest.receiver_id == user.id)) |
			((FriendRequest.sender_id == user.id) & (FriendRequest.receiver_id == self.id)),
			FriendRequest.status == 'accepted'
		).first() is not None
	
	def has_pending_request_with(self, user):
		"""Check if there's a pending request between users"""
		return FriendRequest.query.filter(
			((FriendRequest.sender_id == self.id) & (FriendRequest.receiver_id == user.id)) |
			((FriendRequest.sender_id == user.id) & (FriendRequest.receiver_id == self.id)),
			FriendRequest.status == 'pending'
		).first() is not None
	
	def has_sent_request_to(self, user):
		"""Check if this user has sent a pending request to another user"""
		return FriendRequest.query.filter_by(sender_id=self.id, receiver_id=user.id, status='pending').first() is not None
	
	def has_pending_request_from(self, user):
		"""Check if there is a pending friend request from 'user' to 'self'."""
		return FriendRequest.query.filter_by(sender_id=user.id, receiver_id=self.id, status='pending').first() is not None
	
	def remove_friend(self, user):
		"""Remove friendship between users"""
		friend_request = FriendRequest.query.filter(
			((FriendRequest.sender_id == self.id) & (FriendRequest.receiver_id == user.id)) |
			((FriendRequest.sender_id == user.id) & (FriendRequest.receiver_id == self.id)),
			FriendRequest.status == 'accepted'
		).first()
		
		if friend_request:
			db.session.delete(friend_request)
			db.session.commit()
			return True
		return False
	
	def get_pending_friend_requests(self):
		"""Get all pending friend requests received by this user"""
		return FriendRequest.query.filter(
			FriendRequest.receiver_id == self.id,
			FriendRequest.status == 'pending'
		).all()
	
	def get_sent_friend_requests(self):
		"""Get all pending friend requests sent by this user"""
		return FriendRequest.query.filter(
			FriendRequest.sender_id == self.id,
			FriendRequest.status == 'pending'
		).all()
	
	def send_friend_request(self, user):
		"""Send a friend request to another user"""
		# Check if request already exists
		existing_request = FriendRequest.query.filter(
			((FriendRequest.sender_id == self.id) & (FriendRequest.receiver_id == user.id)) |
			((FriendRequest.sender_id == user.id) & (FriendRequest.receiver_id == self.id))
		).first()
		
		if existing_request:
			return False  # Request already exists
		
		if self.id == user.id:
			return False  # Can't send request to self
		
		friend_request = FriendRequest(sender_id=self.id, receiver_id=user.id)
		db.session.add(friend_request)
		db.session.commit()
		return True

	def cancel_friend_request(self, user):
		# Find the FriendRequest where self is the sender and user is the receiver
		req = FriendRequest.query.filter_by(sender_id=self.id, receiver_id=user.id, status='pending').first()
		if req:
			db.session.delete(req)
			db.session.commit()
			return True
		return False

	def accept_friend_request(self, user):
		"""Accept a pending friend request from 'user' to 'self'."""
		req = FriendRequest.query.filter_by(sender_id=user.id, receiver_id=self.id, status='pending').first()
		if req:
			req.accept()
			# Create notification for the sender that their request was accepted
			Notification.create_friend_accepted_notification(user.id, self.id)
			return True
		return False
	
	def reject_friend_request(self, user):
		"""Reject a pending friend request from 'user' to 'self' - just delete the request."""
		req = FriendRequest.query.filter_by(sender_id=user.id, receiver_id=self.id, status='pending').first()
		if req:
			db.session.delete(req)  # Delete instead of setting to declined
			db.session.commit()
			return True
		return False
	
	def block_user(self, user):
		"""Block a user and remove any existing friend requests"""
		# Check if already blocked
		existing_block = BlockedUser.query.filter_by(blocker_id=self.id, blocked_id=user.id).first()
		if existing_block:
			return False
		
		# Create block record
		block = BlockedUser(blocker_id=self.id, blocked_id=user.id)
		db.session.add(block)
		
		# Remove any existing friend requests between these users
		FriendRequest.query.filter(
			((FriendRequest.sender_id == self.id) & (FriendRequest.receiver_id == user.id)) |
			((FriendRequest.sender_id == user.id) & (FriendRequest.receiver_id == self.id))
		).delete(synchronize_session='fetch')
		
		db.session.commit()
		return True
	
	def is_blocked_by(self, user):
		"""Check if this user is blocked by another user"""
		return BlockedUser.query.filter_by(blocker_id=user.id, blocked_id=self.id).first() is not None
	
	def has_blocked(self, user):
		"""Check if this user has blocked another user"""
		return BlockedUser.query.filter_by(blocker_id=self.id, blocked_id=user.id).first() is not None
	
	def get_unread_notifications(self):
		"""Get all unread notifications for this user"""
		return Notification.query.filter_by(user_id=self.id, is_read=False).order_by(Notification.created_at.desc()).all()
	
	def clear_all_notifications(self):
		"""Delete all notifications for this user"""
		Notification.query.filter_by(user_id=self.id).delete()
		db.session.commit()

class Internship(db.Model): # Internship model for managing internship applications
	__tablename__ = 'internships'  # Use plural table name to match existing Supabase data
	id = db.Column(db.Integer, primary_key=True) # Unique identifier for each internship application
	job_name = db.Column(db.String(250), nullable=False)
	company_name = db.Column(db.String(100), nullable=False) # Name of the company offering the internship
	position = db.Column(db.String(100), nullable=False) # Position title for the internship
	application_status = db.Column(db.String(50), nullable=False, default='Applied') # Status of the application (e.g., Applied, Interviewing, Offered, Rejected)
	application_link = db.Column(db.String(200)) # Link to the internship application (if applicable)
	application_description = db.Column(db.Text) # Description of the internship position
	applied_date = db.Column(db.Date, default=date.today) # Date when the application was submitted
	status_change_date = db.Column(db.Date, default=date.today) # Date when the application status was last changed
	notes = db.Column(db.Text) # Additional notes about the internship application
	visibility = db.Column(db.String(20), default='friends') # Visibility: 'public', 'friends', 'private'
	location = db.Column(db.String(200))  # City, State or Remote # Location of the internship (if applicable)
	contacts = db.Column(db.JSON, default=list)  # List of contacts: [{"name": "Recruiter Name", "details": "recruiter@email.com, 555-1234, LinkedIn"}]
	
	# Work arrangement and job details
	job_type = db.Column(db.String(20), default='on-site')  # 'remote', 'on-site', 'hybrid'
	
	# Calendar integration fields
	calendar_event_id = db.Column(db.String(100))  # Google Calendar event ID for interviews
	reminder_date = db.Column(db.DateTime)  # Custom reminder date
	
	# Application tracking enhancements
	application_method = db.Column(db.String(20), default='website')  # 'website', 'email', 'linkedin', 'referral'
	priority_level = db.Column(db.String(10), default='medium')  # 'high', 'medium', 'low'
	
	# Interview and follow-up tracking
	interview_date = db.Column(db.DateTime)  # Scheduled interview date/time
	follow_up_date = db.Column(db.DateTime)  # When to follow up
	deadline_date = db.Column(db.DateTime)   # Application deadline
	
	# Next Action tracking - only one action can be active at a time
	next_action = db.Column(db.String(50))  # 'follow_up', 'interview', 'assessment', or None
	next_action_date = db.Column(db.DateTime)  # Date/time for the next action
	next_action_notes = db.Column(db.Text)  # Optional notes about the next action
	
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Foreign key linking to the User model

	@property
	def parsed_contacts(self):
		"""Return contacts as a Python list, parsing JSON string if needed"""
		if not self.contacts:
			return []
		
		# If it's already a list, return it
		if isinstance(self.contacts, list):
			return self.contacts
		
		# If it's a string, try to parse it as JSON
		if isinstance(self.contacts, str):
			try:
				import json
				return json.loads(self.contacts)
			except (json.JSONDecodeError, TypeError):
				return []
		
		# Default to empty list
		return []

	def to_dict(self):
		return {
			"id": self.id,
			"job_name": self.job_name,
			"company_name": self.company_name,
			"position": self.position,
			"description": self.application_description,
			"application_status": self.application_status,
			"applied_date": self.applied_date.strftime('%Y-%m-%d'),
			"status_change_date": self.status_change_date.strftime('%Y-%m-%d'),
			"notes": self.notes,
			"next_action": self.next_action,
			"next_action_date": self.next_action_date.strftime('%Y-%m-%d %H:%M') if self.next_action_date else None,
			"contacts": self.parsed_contacts
		}
	
	def set_next_action(self, action_type, action_date=None, notes=None):
		"""Set the next action, clearing old follow_up/interview dates"""
		# Clear previous action dates
		self.follow_up_date = None
		self.interview_date = None
		
		# Set new action
		self.next_action = action_type
		self.next_action_date = action_date
		self.next_action_notes = notes
		
		# Also set the specific date fields for backward compatibility
		if action_type == 'follow_up':
			self.follow_up_date = action_date
		elif action_type == 'interview':
			self.interview_date = action_date
	
	def clear_next_action(self):
		"""Clear all next action fields"""
		self.next_action = None
		self.next_action_date = None
		self.next_action_notes = None
		self.follow_up_date = None
		self.interview_date = None
	
	def get_next_action_display(self):
		"""Get human-readable next action text"""
		if not self.next_action:
			return "No action scheduled"
		
		action_map = {
			'follow_up': 'Follow Up',
			'interview': 'Interview',
			'assessment': 'Assessment'
		}
		
		action_text = action_map.get(self.next_action, self.next_action.title())
		
		if self.next_action_date:
			date_str = self.next_action_date.strftime('%b %d, %Y at %I:%M %p')
			return f"{action_text} on {date_str}"
		else:
			return action_text
	
	def is_next_action_overdue(self):
		"""Check if the next action is overdue"""
		if not self.next_action_date:
			return False
		return datetime.now(timezone.utc) > self.next_action_date.replace(tzinfo=timezone.utc)
	
	def get_status_color(self):
		"""Get color code for application status (useful for UI)"""
		status_colors = {
			'applied': '#007bff',      # Blue
			'interviewing': '#ffc107', # Yellow
			'offered': '#28a745',      # Green
			'rejected': '#dc3545',     # Red
			'accepted': '#28a745',     # Green
			'withdrawn': '#6c757d',    # Gray
			'waitlist': '#fd7e14'      # Orange
		}
		return status_colors.get(self.application_status.lower(), '#6c757d')

class FriendRequest(db.Model):
	"""Model for storing friend requests between users"""
	id = db.Column(db.Integer, primary_key=True)
	sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	status = db.Column(db.String(20), default='pending')  # pending, accepted, declined
	created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
	updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
	
	# Relationships
	sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
	receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')
	
	# Prevent users from sending requests to themselves
	__table_args__ = (db.CheckConstraint('sender_id != receiver_id'),)
	
	def accept(self):
		"""Accept this friend request"""
		self.status = 'accepted'
		self.updated_at = datetime.now(timezone.utc)
		db.session.commit()
	
	def decline(self):
		"""Decline this friend request"""
		self.status = 'declined'
		self.updated_at = datetime.now(timezone.utc)
		db.session.commit()

	def __repr__(self):
		return f'<FriendRequest {self.sender.username} -> {self.receiver.username} ({self.status})>'

class UserSettings(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
	
	# Display & Theme Settings
	theme = db.Column(db.String(20), default='light')  # light, dark, auto
	dashboard_layout = db.Column(db.String(20), default='grid')  # grid, list, compact (for a later time)
	items_per_page = db.Column(db.Integer, default=10)
	
	# Privacy Settings
	profile_visibility = db.Column(db.String(20), default='friends')  # public, friends, private
	show_application_stats = db.Column(db.Boolean, default=True)
	
	# Notification Settings
	email_notifications = db.Column(db.Boolean, default=True)
	friend_request_notifications = db.Column(db.Boolean, default=True)
	application_reminders = db.Column(db.Boolean, default=True)
	interview_reminders = db.Column(db.Boolean, default=True)
	
	# Application Tracking Settings
	auto_archive_rejected = db.Column(db.Boolean, default=False)  # Auto-archive rejected applications after 30 days
	reminder_days_before_followup = db.Column(db.Integer, default=14)  # Days before follow-up reminder
	default_application_status = db.Column(db.String(20), default='applied')
	
	# Calendar & Time Settings
	timezone = db.Column(db.String(50), default='America/New_York')
	date_format = db.Column(db.String(20), default='MM/DD/YYYY')
	time_format = db.Column(db.String(10), default='12h')  # 12h, 24h
	
	# Data & Export Settings
	auto_backup = db.Column(db.Boolean, default=False)
	export_format = db.Column(db.String(10), default='csv')  # csv, excel, pdf
	
	# Security Settings
	two_factor_enabled = db.Column(db.Boolean, default=False)
	login_notifications = db.Column(db.Boolean, default=False)
	
	# Created/Updated timestamps
	created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
	updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
	
	def __repr__(self):
		return f'<UserSettings for {self.user.username}>'
	
	@staticmethod
	def create_default_settings(user_id):
		"""Create default settings for a new user"""
		settings = UserSettings(user_id=user_id)
		db.session.add(settings)
		db.session.commit()
		return settings
	
	def update_setting(self, setting_name, value):
		"""Update a single setting"""
		if hasattr(self, setting_name):
			setattr(self, setting_name, value)
			self.updated_at = datetime.now(timezone.utc)
			db.session.commit()
			return True
		return False
	
	def get_display_settings(self):
		"""Get all display-related settings as dict"""
		return {
			'theme': self.theme,
			'dashboard_layout': self.dashboard_layout,
			'items_per_page': self.items_per_page,
			'date_format': self.date_format,
			'time_format': self.time_format
		}
	
	def get_notification_settings(self):
		"""Get all notification settings as dict"""
		return {
			'email_notifications': self.email_notifications,
			'friend_request_notifications': self.friend_request_notifications,
			'application_reminders': self.application_reminders,
			'interview_reminders': self.interview_reminders,
			'login_notifications': self.login_notifications
		}
	
	def get_privacy_settings(self):
		"""Get all privacy settings as dict"""
		return {
			'default_internship_visibility': self.default_internship_visibility,
			'profile_visibility': self.profile_visibility,
			'show_application_stats': self.show_application_stats,
			'two_factor_enabled': self.two_factor_enabled
		}

class Notification(db.Model):
	"""Model for storing user notifications"""
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	title = db.Column(db.String(200), nullable=False)
	message = db.Column(db.Text, nullable=False)
	type = db.Column(db.String(50), default='info')  # info, success, warning, error, friend_request
	is_read = db.Column(db.Boolean, default=False)
	created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
	
	# Optional: Link to related objects
	related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # For friend request notifications
	
	# Relationships
	user = db.relationship('User', foreign_keys=[user_id], backref='notifications')
	related_user = db.relationship('User', foreign_keys=[related_user_id])
	
	def mark_as_read(self):
		"""Mark notification as read"""
		self.is_read = True
		db.session.commit()
	
	def delete(self):
		"""Delete this notification"""
		db.session.delete(self)
		db.session.commit()
	
	@staticmethod
	def create_friend_request_notification(receiver_id, sender_id):
		"""Create a friend request notification"""
		from app.models import User
		sender = User.query.get(sender_id)
		notification = Notification(
			user_id=receiver_id,
			title="New Friend Request",
			message=f"{sender.firstName} {sender.lastName} sent you a friend request!",
			type="friend_request",
			related_user_id=sender_id
		)
		db.session.add(notification)
		db.session.commit()
		return notification
	
	@staticmethod
	def create_friend_accepted_notification(user_id, friend_id):
		"""Create a friend request accepted notification"""
		from app.models import User
		friend = User.query.get(friend_id)
		notification = Notification(
			user_id=user_id,
			title="Friend Request Accepted",
			message=f"{friend.firstName} {friend.lastName} accepted your friend request!",
			type="success",
			related_user_id=friend_id
		)
		db.session.add(notification)
		db.session.commit()
		return notification

class BlockedUser(db.Model):
	"""Model for storing blocked users"""
	id = db.Column(db.Integer, primary_key=True)
	blocker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	blocked_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
	
	# Relationships
	blocker = db.relationship('User', foreign_keys=[blocker_id], backref='blocked_users')
	blocked = db.relationship('User', foreign_keys=[blocked_id], backref='blocked_by')
	
	# Prevent users from blocking themselves and duplicate blocks
	__table_args__ = (
		db.CheckConstraint('blocker_id != blocked_id'),
		db.UniqueConstraint('blocker_id', 'blocked_id')
	)