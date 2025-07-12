from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_login import current_user, login_required
from app.models import db, User, FriendRequest, Internship

userprofile = Blueprint('profile', __name__)	

@userprofile.route('/', methods=['GET', 'POST'])
@login_required
def profile():
    # Get user's applications with stats
    applications = current_user.internships
    
    # Calculate real stats
    total_applications = len(applications)
    
    # Count by status
    status_counts = {}
    for app in applications:
        status = app.application_status.lower()
        status_counts[status] = status_counts.get(status, 0) + 1
    
    interviews = status_counts.get('interviewing', 0) + status_counts.get('interview scheduled', 0)
    offers = status_counts.get('offered', 0) + status_counts.get('accepted', 0)
    
    # Calculate response rate (interviews + offers + rejections / total)
    responses = interviews + offers + status_counts.get('rejected', 0)
    response_rate = round((responses / total_applications * 100) if total_applications > 0 else 0)
    
    stats = {
        'total_applications': total_applications,
        'interviews': interviews,
        'offers': offers,
        'response_rate': f"{response_rate}%"
    }
    
    return render_template('profile.html', user=current_user, stats=stats)


