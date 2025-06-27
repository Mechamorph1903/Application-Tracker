from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_login import current_user, login_required
from app.models import db, User, FriendRequest, Internship

userprofile = Blueprint('profile', __name__)	

@userprofile.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
	return render_template('profile.html', user=current_user)


