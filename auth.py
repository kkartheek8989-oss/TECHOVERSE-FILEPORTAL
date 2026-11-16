from functools import wraps
from flask import session, redirect, url_for, flash, request, abort

def get_current_user():
    if 'user_id' not in session:
        return None
    return {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role', 'student'),
        'full_name': session.get('full_name', 'Student'),
        'email': session.get('email', '')
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please sign in to access this section.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in with appropriate privileges.', 'warning')
                return redirect(url_for('login', next=request.url))
            user_role = session.get('role', 'student')
            if user_role not in allowed_roles and user_role != 'admin':
                flash('Access Denied: You do not possess the clearance level required for this resource.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def can_access_file(file_row, user, provided_pin=None):
    """
    Evaluates whether the given user (or anonymous visitor) has authorization
    to access/download a file based on its classification level and security PIN.
    """
    classification = file_row['classification']
    required_pin = file_row['access_pin']

    # 1. Public files: Accessible to everyone
    if classification == 'public':
        return True, "Authorized"

    # For member and confidential files, login is mandatory
    if not user:
        return False, "Authentication Required: Please sign in."

    user_role = user.get('role', 'student')

    # 2. Member files: Allowed for member, core, admin
    if classification == 'member':
        if user_role in ['member', 'core', 'admin']:
            return True, "Authorized"
        return False, "Clearance Insufficient: Requires active Technoverse Club Membership."

    # 3. Confidential files: Allowed for core and admin only
    if classification == 'confidential':
        if user_role not in ['core', 'admin']:
            return False, "Clearance Denied: Strictly restricted to Executive Core Committee & Club Administration."
        
        # If an additional security PIN is set, verify PIN
        if required_pin:
            if provided_pin and str(provided_pin).strip() == str(required_pin).strip():
                return True, "Authorized with Security PIN"
            return False, "PIN Required: This high-security file requires the document authorization PIN."

        return True, "Authorized"

    return False, "Unauthorized access attempt"
