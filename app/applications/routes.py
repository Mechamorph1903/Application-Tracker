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
    
    return render_template('application_details.html', internship=internship)

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
            
            # Update status change date if status changed
            old_status = request.form.get('old_status')
            if old_status and old_status != internship.application_status:
                internship.status_change_date = datetime.now(timezone.utc).date()
            
            db.session.commit()
            
            flash(f'Successfully updated {internship.company_name} application!', 'success')
            return redirect(url_for('applications.applicationsList'))
            
        except Exception as e:
            flash(f'Error updating internship: {str(e)}', 'error')
    
    return render_template('internships/edit.html', internship=internship)

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


