from functools import wraps
from flask import session, redirect, url_for, request, g, current_app, jsonify
import jwt
from datetime import datetime, timedelta

class SupabaseUser:
    """Wrapper for Supabase user data to mimic Flask-Login's current_user"""
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.user_metadata = user_data.get('user_metadata', {})
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<SupabaseUser {self.email}>'


def get_supabase_user():
    """
    Get the current authenticated Supabase user from session tokens.
    Returns SupabaseUser object or None if not authenticated.
    """
    access_token = session.get('supabase_access_token')
    refresh_token = session.get('supabase_refresh_token')
    
    if not access_token:
        return None
    
    try:
        response = current_app.supabase.auth.get_user(access_token)
        if response and response.user:
            return SupabaseUser(response.user.model_dump())
    except Exception as e:
        current_app.logger.error(f"Error getting user: {e}")
        
        # Token might be expired, try to refresh
        if refresh_token:
            try:
                refresh_response = current_app.supabase.auth.refresh_session(refresh_token)
                if refresh_response and refresh_response.session:
                    # Update session with new tokens
                    session['supabase_access_token'] = refresh_response.session.access_token
                    session['supabase_refresh_token'] = refresh_response.session.refresh_token
                    return SupabaseUser(refresh_response.user.model_dump())
            except Exception as refresh_error:
                current_app.logger.error(f"Error refreshing token: {refresh_error}")
                # Clear invalid tokens
                session.pop('supabase_access_token', None)
                session.pop('supabase_refresh_token', None)
    
    return None


def supabase_login_required(f):
    """
    Decorator to protect routes with Supabase authentication.
    Use this instead of @login_required for Supabase-authenticated routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_supabase_user()
        
        if user is None:
            # Store the original URL for redirect after login
            session['next'] = request.url
            return redirect(url_for('auth.login'))
        
        # Make user available in g context (like flask-login's current_user)
        g.supabase_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function


def api_supabase_login_required(f):
    """
    Decorator for API routes that return JSON instead of redirecting.
    this is for AJAX/API endpoints.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_supabase_user()
        
        if user is None:
            return jsonify({'error': 'Unauthorized'}), 401
        
        g.supabase_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def store_supabase_tokens(session_data):
    """
    Helper function to store Supabase auth tokens in Flask session.
    
    Args:
        session_data: Supabase session object containing access_token and refresh_token
    """
    if session_data and hasattr(session_data, 'access_token'):
        session['supabase_access_token'] = session_data.access_token
        session['supabase_refresh_token'] = session_data.refresh_token
        session.permanent = True  # Make session persistent
    

def clear_supabase_tokens():
    """
    Helper function to clear Supabase tokens from session.
    """
    session.pop('supabase_access_token', None)
    session.pop('supabase_refresh_token', None)
    session.pop('next', None)


def get_user_id_from_token():
    """
    Extract user ID directly from the JWT token without API call.
    """
    access_token = session.get('supabase_access_token')
    
    if not access_token:
        return None
    
    try:
        # Decode JWT without verification (Supabase has already verified it)
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        return decoded.get('sub')  # 'sub' contains the user ID
    except Exception as e:
        current_app.logger.error(f"Error decoding token: {e}")
        return None