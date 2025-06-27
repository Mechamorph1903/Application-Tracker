from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_login import current_user, login_required
from app.models import db, User, FriendRequest, Internship

settings = Blueprint('settings', __name__)
@settings.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
	return render_template('settings.html', user=current_user)