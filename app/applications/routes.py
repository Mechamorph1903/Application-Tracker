from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone, date
from sqlalchemy.orm.attributes import flag_modified
import json
from ..models import db, Internship, User
from . import applications
from app.auth.compatibility import require_supabase_user


applications = Blueprint('applications', __name__)

@applications.route('/applications-list')
@require_supabase_user
def applicationsList(user):
    """Display user's internship applications"""
    # Get all internships for the current user
    internships = Internship.query.filter_by(user_id=user.id).order_by(Internship.applied_date.desc()).all()
    return render_template('applications.html', internships=internships, user=user)

@applications.route('/application-details/<int:internship_id>')
@require_supabase_user
def application_details(user, internship_id):
    """Display detailed view of a specific internship application"""
    # Get the internship for the current user
    internship = Internship.query.filter_by(id=internship_id, user_id=user.id).first()
    
    if not internship:
        flash('Internship not found or you do not have permission to view it.', 'error')
        return redirect(url_for('applications.applicationsList'))
    
    return render_template('application-details.html', internship=internship, user=user)

@applications.route('/friend/<username>/application-details/<int:internship_id>')
@require_supabase_user
def friend_application_details(user, username,internship_id):
    """Display detailed view of a friend's internship application"""
    # Get the internship for the user
    friend_user =  User.query.filter_by(username=username).first()
    internship = Internship.query.filter_by(id=internship_id, user_id=friend_user.id).first()
    
    if not internship:
        flash('Internship not found or you do not have permission to view it.', 'error')
        return redirect(url_for('applications.applicationsList'))
    

    
    if internship.visibility == 'private':
        flash('You do not have permission to view this internship.', 'error')
        return 
    
    return render_template('friend-application-details.html', user=user,friend_user=friend_user, internship=internship)

@applications.route('/copy-application')
@require_supabase_user
def copy_application(user):
    try:
        internship_id = request.args.get('internship_id', type=int)
        if not internship_id:
            flash('Missing user or internship ID.', 'error')
            return redirect(url_for('home'))


        friendInternship = Internship.query.filter_by(id=internship_id).first()
        if not friendInternship:
            flash('Internship Not Found!')
            return redirect(url_for('applications.applicationsList'))

        # Get friend's username for redirect
        friend_user = User.query.get(friendInternship.user_id)
        friend_username = friend_user.username if friend_user else None

        # Check if current user already has this internship (by company and job name)
        existing = Internship.query.filter_by(
            user_id=user.id,
            company_name=friendInternship.company_name,
            job_name=friendInternship.job_name
        ).first()
        if existing:
            flash('You already have this internship in your applications.', 'warning')
            if friend_username:
                return redirect(url_for('friends.friend_profile', username=friend_username))
            return redirect(url_for('applications.applicationsList'))

        internship = Internship(
            job_name=friendInternship.job_name,
            company_name=friendInternship.company_name,
            position=friendInternship.position,
            application_link=friendInternship.application_link,
            application_description=friendInternship.application_description,
            location=friendInternship.location,
            applied_date=date.today(),
            deadline_date=friendInternship.deadline_date,
            user_id=user.id,
            application_status='copied'
        )
        db.session.add(internship)

        for goal in user.goals:
            if goal['goal-type'] == 'count' and goal['goal-status'] == 'active':
                goal['count'] += 1
                if int(goal['count']) >= int(goal['target']):
                    goal['goal-status'] = 'completed'
                    goal['completed_at'] = datetime.now(timezone.utc).isoformat()

        print(user.goals)
        flag_modified(user, "goals")
        db.session.commit()

        flash('Added to your applications successfully', 'success')
        if friend_username:
            return redirect(url_for('friends.friend_profile', username=friend_username))
        return redirect(url_for('applications.applicationsList'))
    except Exception as e:
        flash(f'Error copying internship: {str(e)}', 'error')
        return redirect(url_for('home'))




@applications.route('/add', methods=['GET', 'POST'])
@require_supabase_user
def add_application(user):
    """Add a new internship application"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('app_name')
            company_name = request.form.get('company')
            position = request.form.get('role')
            
            if not name or not company_name:
                flash('Name and Company are required!', 'error')
                return redirect(url_for('applications.add_application'))
            
            application_status = request.form.get('application_status', 'applied')
            application_link = request.form.get('link')
            if application_link and not application_link.startswith(('http://', 'https://')):
                application_link = 'https://' + application_link
            
            application_description = request.form.get('description')
            location = request.form.get('location')
            notes = request.form.get('notes')
            visibility = request.form.get('visibility', 'friends')
            job_type = request.form.get('job_type', 'on-site')
            contacts_json = request.form.get('contacts', '[]')
            
            # Parse contacts JSON
            try:
                contacts = json.loads(contacts_json) if contacts_json else []
            except json.JSONDecodeError:
                contacts = []
            
            # Parse date fields (handle empty strings)
            def parse_date(date_str):
                if date_str:
                    return datetime.fromisoformat(date_str).date()
                return None
            
            def parse_datetime(date_str):
                if date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return None
            
            applied_date = parse_date(request.form.get('applied'))
            deadline_date = parse_datetime(request.form.get('deadline_date'))
            
            # Parse next action data
            next_action = request.form.get('next_action')
            next_action_date = parse_datetime(request.form.get('next_action_date'))
            
            # Create new internship
            internship = Internship(
                job_name=name,
                company_name=company_name,
                position=position,
                application_status=application_status,
                application_link=application_link,
                application_description=application_description,
                location=location,
                notes=notes,
                visibility=visibility,
                job_type=job_type,
                applied_date=applied_date,
                deadline_date=deadline_date,
                contacts=contacts,
                user_id=user.id
            )
            
            # Set next action if provided
            if next_action and next_action_date:
                internship.set_next_action(next_action, next_action_date)
            
            db.session.add(internship)
            for goal in user.goals:
                if goal['goal-type'] == 'count' and goal['goal-status'] == 'active':
                    goal['count'] += 1
                    if int(goal['count']) >= int(goal['target']):
                        goal['goal-status'] = 'completed'
                        goal['completed_at'] = datetime.now(timezone.utc).isoformat()

            
            flag_modified(user, "goals")
            db.session.commit()
            
            flash(f'Successfully added internship application for {company_name}!', 'success')
            return redirect('/applications/applications-list')
            
        except Exception as e:
            flash(f'Error adding internship: {str(e)}', 'error')
            return redirect(url_for('applications.add_application'))
    
    # GET request - show the form
    today = date.today().strftime('%Y-%m-%d')
    return render_template('add.html', today=today, user=user)

@applications.route('/edit/<int:internship_id>', methods=['GET', 'POST'])
@require_supabase_user
def edit_application(user, internship_id):
    """Edit an existing internship application"""
    internship = Internship.query.filter_by(id=internship_id, user_id=user.id).first()
    
    if not internship:
        flash('Internship not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('applications'))
    
    print(f"DEBUG: Loading internship {internship_id}")
    print(f"DEBUG: internship.contacts type: {type(internship.contacts)}")
    print(f"DEBUG: internship.contacts value: {internship.contacts}")
    
    if request.method == 'POST':
        try:
            # Update fields
            name = request.form.get('app_name')
            company_name = request.form.get('company')
            position = request.form.get('role')
            
            if not name or not company_name:
                flash('Name and Company are required!', 'error')
                return redirect(url_for('applications.edit_application', internship_id=internship_id))
            
            # Parse date fields (handle empty strings)
            def parse_date(date_str):
                if date_str:
                    return datetime.fromisoformat(date_str).date()
                return None
            
            def parse_datetime(date_str):
                if date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return None
            
            # Handle next action logic
            next_action = request.form.get('next_action')
            next_action_date_str = request.form.get('next_action_date')
            next_action_date = parse_datetime(next_action_date_str) if next_action_date_str else None
            
            # Reset all action dates first
            interview_date = None
            follow_up_date = None
            assessment_date = None  # If you have this field in your model
            
            # Set the appropriate date based on selected action
            if next_action and next_action_date:
                if next_action == 'interview':
                    interview_date = next_action_date
                elif next_action == 'follow_up':
                    follow_up_date = next_action_date
                elif next_action == 'assessment':
                    assessment_date = next_action_date
            
            # Parse other date fields
            applied_date = parse_date(request.form.get('applied'))
            deadline_date = parse_datetime(request.form.get('deadline'))
            
            # Parse contacts JSON
            contacts_json = request.form.get('contacts', '[]')
            # print(f"DEBUG: Received contacts JSON: {contacts_json}")
            try:
                contacts = json.loads(contacts_json) if contacts_json else []
                print(f"DEBUG: Parsed contacts: {contacts}")
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON decode error: {e}")
                contacts = []
            
            # Parse next action data
            next_action = request.form.get('next_action')
            next_action_date = parse_datetime(request.form.get('next_action_date'))
            
            # Update all internship fields
            old_status = internship.application_status
            
            internship.job_name = name
            internship.company_name = company_name
            internship.position = position
            internship.application_status = request.form.get('application_status', 'applied')
            internship.application_link = request.form.get('link')
            internship.application_description = request.form.get('description')
            internship.location = request.form.get('location')
            internship.notes = request.form.get('notes')
            internship.visibility = request.form.get('visibility', 'friends')
            internship.job_type = request.form.get('job_type', 'on-site')
            internship.applied_date = applied_date
            internship.deadline_date = deadline_date
            internship.contacts = contacts
            print(f"DEBUG: Set internship.contacts to: {internship.contacts}")
            
            # Handle next action - only one can be active at a time
            if next_action and next_action_date:
                internship.set_next_action(next_action, next_action_date)
            else:
                internship.clear_next_action()
            
            # Update status change date if status changed
            if old_status != internship.application_status:
                internship.status_change_date = datetime.now(timezone.utc).date()
            
            db.session.commit()
            
            flash(f'Successfully updated {internship.company_name} application!', 'success')
            return redirect(url_for('applications.applicationsList'))
            
        except Exception as e:
            flash(f'Error updating internship: {str(e)}', 'error')
    
    return render_template('edit.html', internship=internship, user=user)

@applications.route('/delete/<int:internship_id>', methods=['POST'])
@require_supabase_user
def delete_internship(user, internship_id):
    """Delete an internship application"""
    internship = Internship.query.filter_by(id=internship_id, user_id=user.id).first()
    
    if not internship:
        flash('Internship not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('applications.applicationsList'))
    
    job_name = internship.job_name
    db.session.delete(internship)
    db.session.commit()
    
    flash(f'Successfully deleted {job_name} application.', 'info')
    return redirect(url_for('applications.applicationsList'))


@applications.route('/application-details/<int:internship_id>', methods=['POST'])
@require_supabase_user
def editNotes(user,internship_id):
    """Edit Notes"""
    internship = Internship.query.filter_by(id=internship_id, user_id=user.id).first()

    if not internship:
         return {'error': 'Internship not found'}, 404
    try:
        notes = request.form.get('notes', '')
        internship.notes = notes
        db.session.commit()
        print('Notes successfully updated!')
        flash('Notes successfully updated!', 'success')
        
        return {'success': True, 'notes': notes}, 200
        
    except Exception as e:
        flash(f'Error updating notes: {str(e)}', 'error')
        db.session.rollback()
        return {'error': str(e)}, 500



