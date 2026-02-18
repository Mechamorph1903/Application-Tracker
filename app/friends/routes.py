from flask import render_template, request, redirect, url_for, flash, jsonify
from app.models import db, User, FriendRequest, Internship
from . import friends
from app.auth.compatibility import require_supabase_user

@friends.route('/')
@require_supabase_user
def friendsList(user):
	friends_list = user.get_friends()
	pending_received = user.get_pending_friend_requests()
	pending_sent = user.get_sent_friend_requests()

	interview_statuses = {'interview', 'interviewing', 'interview scheduled'}
	offer_statuses = {'offer', 'offered', 'accepted'}
	interview_counts = {}
	offer_counts = {}
	for friend in friends_list:
		interview_counts[friend.id] = sum(
			1 for internship in friend.internships
			if internship.application_status and internship.visibility != 'private'
			and internship.application_status.strip().lower() in interview_statuses
		)
		offer_counts[friend.id] = sum(
			1 for internship in friend.internships
			if internship.application_status and internship.visibility != 'private'
			and internship.application_status.strip().lower() in offer_statuses
		)
	return render_template('friends.html', 
		friends=friends_list,
		pending_received=pending_received,
		pending_sent=pending_sent,
		interview_counts=interview_counts,
		offer_counts=offer_counts,
		user=user)

# not friends
@friends.route('/users/<username>')
@require_supabase_user
def limited_profile(user, username):
	prospective_user = User.query.filter_by(username=username).first()
	user_friends = set(user.get_friends())
	acquaintance_friends = set(prospective_user.get_friends())
	mutual_friends = user_friends & acquaintance_friends



	if not prospective_user:
		flash('User not found.', 'error')
		return redirect(url_for('friends.friendsList'))
	if username == user.username:
		flash("Thats's you silly, 😂. (Please, report this to us)", 'info')
		return redirect(url_for('profile.profile'))
	isFriends = prospective_user.is_friend_with(user)
	if isFriends:
		return redirect(url_for('friends.friend_profile', username=username))
	return render_template('prospective.html', user=user, isFriends=isFriends, mutual_friends=mutual_friends, prospective_user=prospective_user)

#user pool
@friends.route('/friends-portal', methods=['GET', 'POST'])
@require_supabase_user
def search_users(user):
	import json
	majors_path = 'app/static/js/majors.json'
	with open(majors_path, encoding='utf-8') as f:
		majors_data = json.load(f)
	majors = sorted([m['major'] for m in majors_data['Majors']])

	users_query = User.query.filter(User.username != user.username)
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
	
	try:
		users = users_query.all()
	except Exception as e:
		# Handle social_media field type errors gracefully
		print(f"⚠️  Database error in user search: {e}")
		flash('There was an issue loading user profiles. Please try again.', 'error')
		users = []
	
	return render_template("friends-portal.html", users=users, majors=majors, user=user)

#friend request logic
@friends.route('/add-friend', methods=['POST'])
@require_supabase_user
def addFriend(user):
	user_id = request.form.get('user_id')
	if not user_id:
		flash('User ID is required', 'error')
		return redirect(url_for('friends.friendsList'))
	try:
		user_id = int(user_id)
		target_user = User.query.get(user_id)
		if not target_user:
			flash('User not found', 'error')
			return redirect(url_for('friends.friendsList'))
		print(f"user_id: {user_id}, user: {target_user}")
		friend_request = user.send_friend_request(target_user)
		if friend_request:
			flash(f'Friend request sent to {target_user.firstName}!', 'success')
		else:
			flash(f'You already sent a request to {target_user.firstName}!', 'info')
		return redirect(url_for('friends.limited_profile', username=target_user.username))
	except ValueError:
		flash('Invalid user ID', 'error')
		return redirect(url_for('friends.friendsList'))
	except Exception as e:
		flash('An error occurred', 'error')
		return redirect(url_for('friends.friendsList'))



#cancel friend request
@friends.route('/cancel-friend-request', methods=['POST'])
@require_supabase_user
def cancelRequest(user):
	
	user_id = request.form.get('user_id')
	if not user_id:
		flash('User ID is required', 'error')
		return redirect(url_for('friends.friendsList'))
	try:
		user_id = int(user_id)
		target_user = User.query.get(user_id)
		if not target_user:
			flash('User not found', 'error')
			return redirect(url_for('friends.friendsList'))
		cancelled = user.cancel_friend_request(target_user)
		if cancelled:
			flash('Friend request cancelled', 'success')
		else:
			flash('No pending request to cancel', 'info')
		return redirect(url_for('friends.limited_profile', username=target_user.username))
	except Exception as e:
		flash('An error occurred', 'error')
		return redirect(url_for('friends.friendsList'))


# Accept friend request endpoint
@friends.route('/accept-friend-request/<int:user_id>', methods=['GET'])
@require_supabase_user
def acceptFriendRequest(user,user_id):
	try:
		target_user = User.query.get(user_id)
		if not target_user:
			flash('User not found', 'error')
			return redirect(url_for('friends.friendsList'))

		req = user.accept_friend_request(target_user)
		if req:
			flash('Friend request accepted!', 'success')
			return redirect(url_for('friends.friend_profile', username=target_user.username))
		else:
			flash('No pending request to accept', 'error')
			return redirect(url_for('friends.friendsList'))
	except Exception as e:
		flash('An error occurred', 'error')
		return redirect(url_for('friends.friendsList'))

#Reject friend_request
@friends.route('/decline-friend-request/<int:user_id>')
@require_supabase_user
def declineFriendRequest(user,user_id):
	try:
		target_user = User.query.get(user_id)
		if not target_user:
			flash('User not found', 'error')
			return redirect(url_for('profile.profile'))

		req = user.reject_friend_request(target_user)
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
@require_supabase_user
def blockUser(user, user_id):
	try:
		target_user = User.query.get(user_id)
		if not target_user:
			flash('User not found', 'error')
			return redirect(url_for('profile.profile'))

		blocked = user.block_user(target_user)
		if blocked:
			flash(f'{target_user.firstName} has been blocked', 'info')
		else:
			flash(f'{target_user.firstName} is already blocked', 'warning')
		return redirect(url_for('profile.profile'))
	except Exception as e:
		flash('An error occurred', 'error')
		return redirect(url_for('profile.profile'))




# if friends

@friends.route('/friends/<username>')
@require_supabase_user
def friend_profile(user,username):
	friend_user = User.query.filter_by(username=username).first()
	if not friend_user:
		# For testing purposes, if 'mikechen' doesn't exist, use current user as example
			flash('User not found.', 'error')
			return redirect(url_for('friends.friendsList'))
	
	# Get the user's internship applications (exclude private ones for friends)
	internships = Internship.query.filter(
		Internship.user_id == friend_user.id,
		Internship.visibility != 'private'
	).order_by(Internship.applied_date.desc()).all()
	
	return render_template('friend_profile.html', user=user, internships=internships, friend_user=friend_user)

# Notification management routes
@friends.route('/mark-notification-read/<int:notification_id>')
@require_supabase_user
def mark_notification_read(user, notification_id):
	from app.models import Notification
	try:
		notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
		if notification:
			notification.mark_as_read()
			flash('Notification marked as read', 'success')
		else:
			flash('Notification not found', 'error')
	except Exception as e:
		flash('An error occurred', 'error')
	return redirect(url_for('profile.profile'))

@friends.route('/delete-notification/<int:notification_id>')
@require_supabase_user
def delete_notification(user, notification_id):
	from app.models import Notification
	try:
		notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
		if notification:
			notification.delete()
			flash('Notification deleted', 'success')
		else:
			flash('Notification not found', 'error')
	except Exception as e:
		flash('An error occurred', 'error')
	return redirect(url_for('profile.profile'))

@friends.route('/clear-all-notifications')
@require_supabase_user
def clear_all_notifications(user):
	try:
		user.clear_all_notifications()
		flash('All notifications cleared', 'success')
	except Exception as e:
		flash('An error occurred', 'error')
	return redirect(url_for('profile.profile'))