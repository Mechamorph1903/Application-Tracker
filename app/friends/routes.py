from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app.models import db, User, FriendRequest, Internship
from . import friends

@friends.route('/')
@login_required
def friendsList():
	friends_list = current_user.get_friends()
	pending_received = current_user.get_pending_friend_requests()
	pending_sent = current_user.get_sent_friend_requests()
	
	return render_template('friends.html', 
	                     friends=friends_list,
	                     pending_received=pending_received,
	                     pending_sent=pending_sent)

@friends.route('/users/<username>')
@login_required
def limited_profile(username):
	user =  User.query.filter_by(username=username).first()
	if not user:
		flash('User not found.', 'error')
		return redirect(url_for('friends.friendsList'))

	return render_template('acquaintance.html', user=user)
	
@friends.route('/friends-portal', methods=['GET', 'POST'])
@login_required
def search_friends():
	all_users =  User.query.all()

	return render_template("friends-portal.html", users=all_users)


@friends.route('/friends/<username>')
@login_required
def friend_profile(username):
	user = User.query.filter_by(username=username).first()
	if not user:
		# For testing purposes, if 'mikechen' doesn't exist, use current user as example
			flash('User not found.', 'error')
			return redirect(url_for('friends.friendsList'))
	
	# Check if the current user is friends with this user
	# Temporarily commented out for testing - uncomment when you have real friends
	# if not current_user.is_friend_with(user):
	# 	flash('You are not friends with this user.', 'error')
	# 	return redirect(url_for('friends.friendsList'))
	
	# Get the user's internship applications
	internships = Internship.query.filter_by(user_id=user.id).order_by(Internship.applied_date.desc()).all()
	
	return render_template('friend_profile.html', user=user, internships=internships)