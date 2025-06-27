from flask import Blueprint
from . import routes

profile = Blueprint('profile', __name__)	
# This creates a blueprint named 'profile' for the profile module, allowing you to organize routes and views related to user profiles.