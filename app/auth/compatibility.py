"""
Compatibility layer for gradual Supabase migration.
Provides helpers to work with both Flask-Login and Supabase auth.
"""

from flask import current_app, session, g
from requests import request
from app.models import User
from app.auth.supabase_auth import get_user_id_from_token
from datetime import timezone, datetime

def get_db_user():
    """
    Get the authenticated database user from Supabase token.
    This replaces current_user.id usage in routes.
    
    Returns:
        User object if authenticated via Supabase, None otherwise
    """
    supabase_user_id = get_user_id_from_token()
    
    if not supabase_user_id:
        return None
    
    db_user = User.query.filter_by(supabase_user_id=supabase_user_id).first()
    return db_user


def get_authenticated_user():
    """
    Get the authenticated user - checks both Supabase and Flask-Login.
    Use this as a failsafe during transition period.
    
    Priority:
    1. Supabase token (new method)
    2. Flask-Login session (old method, for backward compat)
    
    Returns:
        User object if authenticated, None otherwise
    """
    # Try Supabase first (new method)
    db_user = get_db_user()
    if db_user:
        return db_user
    
    # Fallback to Flask-Login (old method)
    from flask_login import current_user
    if current_user.is_authenticated:
        return current_user
    
    return None


def require_supabase_user(f):
    """
    Decorator replacement for @supabase_login_required.
    Gets database user and passes it to the route.
    
    Usage:
        @app.route('/dashboard')
        @require_supabase_user
        def dashboard(user):
            return render_template('dashboard.html', user=user)
    """
    from functools import wraps
    from flask import redirect, url_for, flash
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_db_user()
        
        if not user:
            flash('Please log in to access this page.', 'warning')
            session['next'] = request.url
            return redirect(url_for('auth.register') + '?tab=login')

        try:
            user.last_seen = datetime.now(timezone.utc)
            from app.models import db
            db.session.commit()
        except Exception as e:
            print(f"⚠️ Error updating last_seen: {e}")
            # Don't fail the request if last_seen update fails
        
        # Pass user as first argument to the route
        return f(user, *args, **kwargs)
    
    return decorated_function