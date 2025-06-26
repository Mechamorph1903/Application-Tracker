from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes
# This imports the routes module to register the routes defined in it with the auth blueprint.