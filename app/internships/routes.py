from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from ..models import db, Internship, User
from . import internships

@internships.route('/add', methods=['GET', 'POST'])
@login_required
def add_internship():
    """Add a new internship application"""
    if request.method == 'POST':
        try:
            # Get form data
            company_name = request.form.get('company_name')
            position = request.form.get('position')
            application_status = request.form.get('application_status', 'applied')
            application_link = request.form.get('application_link')
            application_description = request.form.get('application_description')
            location = request.form.get('location')
            notes = request.form.get('notes')
            visibility = request.form.get('visibility', 'friends')
            
            # Parse date fields (handle empty strings)
            def parse_datetime(date_str):
                if date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return None
            
            interview_date = parse_datetime(request.form.get('interview_date'))
            follow_up_date = parse_datetime(request.form.get('follow_up_date'))
            deadline_date = parse_datetime(request.form.get('deadline_date'))
            next_action_date = parse_datetime(request.form.get('next_action_date'))
            next_action_type = request.form.get('next_action_type')
            
            # Create new internship
            internship = Internship(
                company_name=company_name,
                position=position,
                application_status=application_status,
                application_link=application_link,
                application_description=application_description,
                location=location,
                notes=notes,
                visibility=visibility,
                interview_date=interview_date,
                follow_up_date=follow_up_date,
                deadline_date=deadline_date,
                next_action_date=next_action_date,
                next_action_type=next_action_type,
                user_id=current_user.id
            )
            
            db.session.add(internship)
            db.session.commit()
            
            flash(f'Successfully added internship application for {company_name}!', 'success')
            return redirect(url_for('applications'))
            
        except Exception as e:
            flash(f'Error adding internship: {str(e)}', 'error')
            return redirect(url_for('internships.add_internship'))
    
    # GET request - show the form
    return render_template('internships/add.html')

@internships.route('/edit/<int:internship_id>', methods=['GET', 'POST'])
@login_required
def edit_internship(internship_id):
    """Edit an existing internship application"""
    internship = Internship.query.filter_by(id=internship_id, user_id=current_user.id).first()
    
    if not internship:
        flash('Internship not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('applications'))
    
    if request.method == 'POST':
        try:
            # Update fields
            internship.company_name = request.form.get('company_name')
            internship.position = request.form.get('position')
            internship.application_status = request.form.get('application_status')
            internship.application_link = request.form.get('application_link')
            internship.application_description = request.form.get('application_description')
            internship.location = request.form.get('location')
            internship.notes = request.form.get('notes')
            internship.visibility = request.form.get('visibility')
            
            # Parse date fields
            def parse_datetime(date_str):
                if date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return None
            
            internship.interview_date = parse_datetime(request.form.get('interview_date'))
            internship.follow_up_date = parse_datetime(request.form.get('follow_up_date'))
            internship.deadline_date = parse_datetime(request.form.get('deadline_date'))
            internship.next_action_date = parse_datetime(request.form.get('next_action_date'))
            internship.next_action_type = request.form.get('next_action_type')
            
            # Update status change date if status changed
            old_status = request.form.get('old_status')
            if old_status and old_status != internship.application_status:
                internship.status_change_date = datetime.now(timezone.utc).date()
            
            db.session.commit()
            
            flash(f'Successfully updated {internship.company_name} application!', 'success')
            return redirect(url_for('applications'))
            
        except Exception as e:
            flash(f'Error updating internship: {str(e)}', 'error')
    
    return render_template('internships/edit.html', internship=internship)

@internships.route('/delete/<int:internship_id>', methods=['POST'])
@login_required
def delete_internship(internship_id):
    """Delete an internship application"""
    internship = Internship.query.filter_by(id=internship_id, user_id=current_user.id).first()
    
    if not internship:
        flash('Internship not found or you do not have permission to delete it.', 'error')
        return redirect(url_for('applications'))
    
    company_name = internship.company_name
    db.session.delete(internship)
    db.session.commit()
    
    flash(f'Successfully deleted {company_name} application.', 'info')
    return redirect(url_for('applications'))

@internships.route('/action/<int:internship_id>')
@login_required
def get_next_action(internship_id):
    """API endpoint to get next action for an internship"""
    internship = Internship.query.filter_by(id=internship_id, user_id=current_user.id).first()
    
    if not internship:
        return jsonify({'error': 'Internship not found'}), 404
    
    next_action = internship.get_next_action()
    return jsonify({
        'next_action': next_action,
        'is_overdue': internship.is_overdue(),
        'days_until_next_action': internship.days_until_next_action(),
        'status_color': internship.get_status_color()
    })

@internships.route('/dashboard-data')
@login_required
def dashboard_data():
    """API endpoint for dashboard statistics"""
    user_internships = current_user.internships
    
    # Use the helper methods for dashboard stats
    urgent_internships = [i for i in user_internships if i.get_next_action()]
    overdue_count = sum(1 for i in user_internships if i.is_overdue())
    today_actions = [i for i in user_internships if i.days_until_next_action() == 0]
    week_actions = [i for i in user_internships if i.days_until_next_action() and 0 <= i.days_until_next_action() <= 7]
    
    # Status breakdown
    status_counts = {}
    for internship in user_internships:
        status = internship.application_status.lower()
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return jsonify({
        'total_applications': len(user_internships),
        'urgent_count': len(urgent_internships),
        'overdue_count': overdue_count,
        'today_actions_count': len(today_actions),
        'week_actions_count': len(week_actions),
        'status_counts': status_counts,
        'urgent_internships': [
            {
                'id': i.id,
                'company_name': i.company_name,
                'position': i.position,
                'next_action': i.get_next_action(),
                'days_until': i.days_until_next_action(),
                'status_color': i.get_status_color()
            } for i in urgent_internships[:5]  # Top 5 urgent
        ]
    })
