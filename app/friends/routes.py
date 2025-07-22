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

	interview_counts = {}
	offer_counts = {}
	for friend in friends_list:
		interview_counts[friend.id] = sum(
			1 for internship in friend.internships
			if (internship.application_status and internship.application_status.lower() == 'interview' 
				and internship.visibility != 'private')
		)
		offer_counts[friend.id] = sum(
			1 for internship in friend.internships
			if (internship.application_status and internship.application_status.lower() == 'offer'
				and internship.visibility != 'private')
		)
	return render_template('friends.html', 
		friends=friends_list,
		pending_received=pending_received,
		pending_sent=pending_sent,
		interview_counts=interview_counts,
		offer_counts=offer_counts)

# not friends
@friends.route('/users/<username>')
@login_required
def limited_profile(username):
	user = User.query.filter_by(username=username).first()
	current_user_friends = set(current_user.get_friends())
	acquaintance_friends = set(user.get_friends())
	mutual_friends = current_user_friends & acquaintance_friends



	if not user:
		flash('User not found.', 'error')
		return redirect(url_for('friends.friendsList'))
	if username == current_user.username:
		flash("Thats's you silly, 😂", 'info')
		return redirect(url_for('profile.profile'))
	isFriends = user.is_friend_with(current_user)
	if isFriends:
		return redirect(url_for('friends.friend_profile', username=username))
	return render_template('prospective.html', user=user, isFriends=isFriends, mutual_friends=mutual_friends)

#user pool
@friends.route('/friends-portal', methods=['GET', 'POST'])
@login_required
def search_users():
	import json
	majors_path = 'app/static/js/majors.json'
	with open(majors_path, encoding='utf-8') as f:
		majors_data = json.load(f)
	majors = sorted([m['major'] for m in majors_data['Majors']])

	users_query = User.query.filter(User.username != current_user.username)
	name = request.form.get('name', '').strip()
	school = request.form.get('school', '').strip()
	major = request.form.get('major', '').strip()

	if request.method == 'POST':
		if name:
			users_query = users_query.filter(
				(User.firstName.ilike(f'%{name}%')) | (User.lastName.ilike(f'%{name}%')) | (User.username.ilike(f'%{name}%'))
			)
		if school:
			users_query = users_query.filter(User.school.ilike(f'%{school}%'))
		if major:
			users_query = users_query.filter(User.major == major)
	users = users_query.all()
	return render_template("friends-portal.html", users=users, majors=majors)

#friend request logic
@friends.route('/add-friend', methods=['POST'])
@login_required
def addFriend():
	user_id = request.form.get('user_id')
	if not user_id:
		flash('User ID is required', 'error')
		return redirect(url_for('friends.friendsList'))
	try:
		user_id = int(user_id)
		user = User.query.get(user_id)
		if not user:
			flash('User not found', 'error')
			return redirect(url_for('friends.friendsList'))
		print(f"user_id: {user_id}, user: {user}")
		friend_request = current_user.send_friend_request(user)
		if friend_request:
			flash(f'Friend request sent to {user.firstName}!', 'success')
		else:
			flash(f'You already sent a request to {user.firstName}!', 'info')
		return redirect(url_for('friends.limited_profile', username=user.username))
	except ValueError:
		flash('Invalid user ID', 'error')
		return redirect(url_for('friends.friendsList'))
	except Exception as e:
		flash('An error occurred', 'error')
		return redirect(url_for('friends.friendsList'))



#cancel friend request
@friends.route('/cancel-friend-request', methods=['POST'])
@login_required
def cancelRequest():
	
	user_id = request.form.get('user_id')
	if not user_id:
		flash('User ID is required', 'error')
		return redirect(url_for('friends.friendsList'))
	try:
		user_id = int(user_id)
		user = User.query.get(user_id)
		if not user:
			flash('User not found', 'error')
			return redirect(url_for('friends.friendsList'))
		cancelled = current_user.cancel_friend_request(user)
		if cancelled:
			flash('Friend request cancelled', 'success')
		else:
			flash('No pending request to cancel', 'info')
		return redirect(url_for('friends.limited_profile', username=user.username))
	except Exception as e:
		flash('An error occurred', 'error')
		return redirect(url_for('friends.friendsList'))


# Accept friend request endpoint
@friends.route('/accept-friend-request/<int:user_id>', methods=['GET'])
@login_required
def acceptFriendRequest(user_id):
	try:
		user = User.query.get(user_id)
		if not user:
			flash('User not found', 'error')
			return redirect(url_for('friends.friendsList'))

		req = current_user.accept_friend_request(user)
		if req:
			flash('Friend request accepted!', 'success')
			return redirect(url_for('friends.friend_profile', username=user.username))
		else:
			flash('No pending request to accept', 'error')
			return redirect(url_for('friends.friendsList'))
	except Exception as e:
		flash('An error occurred', 'error')
		return redirect(url_for('friends.friendsList'))

#Reject friend_request
@friends.route('/decline-friend-request/<int:user_id>')
@login_required
def declineFriendRequest(user_id):
	try:
		user = User.query.get(user_id)
		if not user:
			flash('User not found', 'error')
			return redirect(url_for('profile.profile'))

		req = current_user.reject_friend_request(user)
		if req:
			flash('Friend request declined', 'info')
			return redirect(url_for('profile.profile'))
		else:
			flash('No pending request to decline', 'error')
			return redirect(url_for('profile.profile'))
	except Exception as e:
		flash('An error occurred', 'error')
		return redirect(url_for('profile.profile'))

# Block user route
@friends.route('/block-user/<int:user_id>')
@login_required
def blockUser(user_id):
	try:
		user = User.query.get(user_id)
		if not user:
			flash('User not found', 'error')
			return redirect(url_for('profile.profile'))

		blocked = current_user.block_user(user)
		if blocked:
			flash(f'{user.firstName} has been blocked', 'info')
		else:
			flash(f'{user.firstName} is already blocked', 'warning')
		return redirect(url_for('profile.profile'))
	except Exception as e:
		flash('An error occurred', 'error')
		return redirect(url_for('profile.profile'))




# if friends

@friends.route('/friends/<username>')
@login_required
def friend_profile(username):
	user = User.query.filter_by(username=username).first()
	if not user:
		# For testing purposes, if 'mikechen' doesn't exist, use current user as example
			flash('User not found.', 'error')
			return redirect(url_for('friends.friendsList'))
	
	# Get the user's internship applications (exclude private ones for friends)
	internships = Internship.query.filter(
		Internship.user_id == user.id,
		Internship.visibility != 'private'
	).order_by(Internship.applied_date.desc()).all()
	
	return render_template('friend_profile.html', user=user, internships=internships)

# Notification management routes
@friends.route('/mark-notification-read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
	from app.models import Notification
	try:
		notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
		if notification:
			notification.mark_as_read()
			flash('Notification marked as read', 'success')
		else:
			flash('Notification not found', 'error')
	except Exception as e:
		flash('An error occurred', 'error')
	return redirect(url_for('profile.profile'))

@friends.route('/delete-notification/<int:notification_id>')
@login_required
def delete_notification(notification_id):
	from app.models import Notification
	try:
		notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
		if notification:
			notification.delete()
			flash('Notification deleted', 'success')
		else:
			flash('Notification not found', 'error')
	except Exception as e:
		flash('An error occurred', 'error')
	return redirect(url_for('profile.profile'))

@friends.route('/clear-all-notifications')
@login_required
def clear_all_notifications():
	try:
		current_user.clear_all_notifications()
		flash('All notifications cleared', 'success')
	except Exception as e:
		flash('An error occurred', 'error')
	return redirect(url_for('profile.profile'))