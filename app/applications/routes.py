from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone, date
import json
from ..models import db, Internship, User
from . import applications

applications = Blueprint('applications', __name__)

@applications.route('/applications-list')
@login_required
def applicationsList():
    """Display user's internship applications"""
    # Get all internships for the current user
    internships = Internship.query.filter_by(user_id=current_user.id).all()
    return render_template('applications.html', internships=internships)

@applications.route('/application-details/<int:internship_id>')
@login_required
def application_details(internship_id):
    """Display detailed view of a specific internship application"""
    # Get the internship for the current user
    internship = Internship.query.filter_by(id=internship_id, user_id=current_user.id).first()
    
    if not internship:
        flash('Internship not found or you do not have permission to view it.', 'error')
        return redirect(url_for('applications.applicationsList'))
    
    return render_template('application-details.html', internship=internship)

@applications.route('/add', methods=['GET', 'POST'])
@login_required
def add_application():
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
            application_description = request.form.get('description')
            location = request.form.get('location')
            notes = request.form.get('notes')
            visibility = request.form.get('visibility', 'friends')
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
            interview_date = parse_datetime(request.form.get('interview_date'))
            follow_up_date = parse_datetime(request.form.get('follow_up_date'))
            deadline_date = parse_datetime(request.form.get('deadline_date'))
            
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
                applied_date=applied_date,
                interview_date=interview_date,
                follow_up_date=follow_up_date,
                deadline_date=deadline_date,
                contacts=contacts,
                user_id=current_user.id
            )
            
            db.session.add(internship)
            db.session.commit()
            
            flash(f'Successfully added internship application for {company_name}!', 'success')
            return redirect('/applications/applications-list')
            
        except Exception as e:
            flash(f'Error adding internship: {str(e)}', 'error')
            return redirect(url_for('applications.add_application'))
    
    # GET request - show the form
    today = date.today().strftime('%Y-%m-%d')
    return render_template('add.html', today=today)

@applications.route('/edit/<int:internship_id>', methods=['GET', 'POST'])
@login_required
def edit_application(internship_id):
    """Edit an existing internship application"""
    internship = Internship.query.filter_by(id=internship_id, user_id=current_user.id).first()
    
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
            print(f"DEBUG: Received contacts JSON: {contacts_json}")
            try:
                contacts = json.loads(contacts_json) if contacts_json else []
                print(f"DEBUG: Parsed contacts: {contacts}")
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON decode error: {e}")
                contacts = []
            
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
            internship.applied_date = applied_date
            internship.interview_date = interview_date
            internship.follow_up_date = follow_up_date
            internship.deadline_date = deadline_date
            internship.contacts = contacts
            print(f"DEBUG: Set internship.contacts to: {internship.contacts}")
            
            # Update status change date if status changed
            if old_status != internship.application_status:
                internship.status_change_date = datetime.now(timezone.utc).date()
            
            db.session.commit()
            
            flash(f'Successfully updated {internship.company_name} application!', 'success')
            return redirect(url_for('applications.applicationsList'))
            
        except Exception as e:
            flash(f'Error updating internship: {str(e)}', 'error')
    
    return render_template('edit.html', internship=internship)

@applications.route('/delete/<int:internship_id>', methods=['POST'])
@login_required
def delete_internship(internship_id):
    """Delete an internship application"""
    internship = Internship.query.filter_by(id=internship_id, user_id=current_user.id).first()
    
    if not internship:
        flash('Internship not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('applications.applicationsList'))
    
    company_name = internship.company_name
    db.session.delete(internship)
    db.session.commit()
    
    flash(f'Successfully deleted {company_name} application.', 'info')
    return redirect(url_for('applications.applicationsList'))


