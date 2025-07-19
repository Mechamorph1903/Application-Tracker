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

# not friends
@friends.route('/users/<username>')
@login_required
def limited_profile(username):
	user = User.query.filter_by(username=username).first()
	if not user:
		flash('User not found.', 'error')
		return redirect(url_for('friends.friendsList'))
	if username == current_user.username:
		flash("Thats's you silly, 😂", 'info')
		return redirect(url_for('profile.profile'))
	isFriends = user.is_friend_with(current_user)
	if isFriends:
		return redirect(url_for('friends.friend_profile', username=username))
	return render_template('prospective.html', user=user, isFriends=isFriends)

#user pool
@friends.route('/friends-portal', methods=['GET', 'POST'])
@login_required
def search_users():
	all_users =  User.query.filter(User.username!=current_user.username).all()
	return render_template("friends-portal.html", users=all_users)

#friend request logic
@friends.route('/add-friend', methods=['POST'])
@login_required
def addFriend():
	user_id = request.form.get('user_id')
	if not user_id:
		return jsonify({'success': False, 'message': 'User ID is required'}), 400
	
	try:
		user_id = int(user_id)
		user = User.query.get(user_id)
		if not user:
			return jsonify({'success': False, 'message': 'User not found'}), 404
		
		friend_request = current_user.send_friend_request(user_id)
		
		if friend_request:
			return jsonify({'success': True, 'message': f'Friend request sent to {user.firstName}!'})
		else:
			return jsonify({'success': False, 'message': f'You are already friends with {user.firstName}!'})
	except ValueError:
		return jsonify({'success': False, 'message': 'Invalid user ID'}), 400
	except Exception as e:
		return jsonify({'success': False, 'message': 'An error occurred'}), 500











# if friends

@friends.route('/friends/<username>')
@login_required
def friend_profile(username):
	user = User.query.filter_by(username=username).first()
	if not user:
		# For testing purposes, if 'mikechen' doesn't exist, use current user as example
			flash('User not found.', 'error')
			return redirect(url_for('friends.friendsList'))
	
	# Get the user's internship applications
	internships = Internship.query.filter_by(user_id=user.id).order_by(Internship.applied_date.desc()).all()
	
	return render_template('friend_profile.html', user=user, internships=internships)