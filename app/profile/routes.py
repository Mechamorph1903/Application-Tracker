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
    
    # Count by status (case-insensitive and robust)
    status_counts = {}
    for app in applications:
        status = app.application_status.lower() if app.application_status else ''
        status_counts[status] = status_counts.get(status, 0) + 1

    interviews = 0
    for key in status_counts:
        if key in ['interview', 'interviewing', 'interview scheduled']:
            interviews += status_counts[key]
    offers = 0
    for key in status_counts:
        if key in ['offer', 'offered', 'accepted']:
            offers += status_counts[key]

    # Calculate response rate (interviews + offers + rejections + assessments / total)
    assessments = sum(
        count for key, count in status_counts.items() if 'assessment' in key
    )
    responses = interviews + offers + status_counts.get('rejected', 0) + assessments
    response_rate = round((responses / total_applications * 100) if total_applications > 0 else 0)

    stats = {
        'total_applications': total_applications,
        'interviews': interviews,
        'offers': offers,
        'response_rate': f"{response_rate}%"
    }
    
    return render_template('profile.html', user=current_user, stats=stats)


