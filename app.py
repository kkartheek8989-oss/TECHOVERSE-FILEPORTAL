import os
import uuid
import datetime
import mimetypes
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    session, send_file, abort, jsonify
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from database import get_db, init_db
from auth import get_current_user, login_required, role_required, can_access_file
from audit import log_action

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database and storage folder are ready
init_db()

@app.context_processor
def inject_globals():
    return {
        'current_user': get_current_user(),
        'categories': Config.CATEGORIES,
        'now': datetime.datetime.now()
    }

@app.template_filter('filesize')
def format_filesize(size_in_bytes):
    if size_in_bytes is None:
        return '0 B'
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} PB"

@app.template_filter('datetime_format')
def datetime_format(value):
    if not value:
        return ''
    try:
        # If string like '2026-11-16 08:23:42'
        dt = datetime.datetime.fromisoformat(str(value))
        return dt.strftime('%d %b %Y, %I:%M %p')
    except Exception:
        return str(value)

# ==========================================
# PUBLIC & DASHBOARD ROUTES
# ==========================================

@app.route('/')
def index():
    user = get_current_user()
    classification_filter = request.args.get('classification', 'all')
    category_filter = request.args.get('category', 'all')
    search_query = request.args.get('q', '').strip()

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM files WHERE is_archived = 0"
    params = []

    # Visibility scoping:
    # If not logged in, show only public by default unless filtered, but restrict unauthorized
    if not user:
        # Non-logged in users only see public circulars & files
        query += " AND classification = 'public'"
    elif user['role'] == 'student':
        # General students see public and member overviews
        query += " AND classification IN ('public', 'member')"
    # 'member' sees public and member files
    elif user['role'] == 'member':
        query += " AND classification IN ('public', 'member')"
    # 'core' and 'admin' see everything including confidential

    if classification_filter != 'all':
        query += " AND classification = ?"
        params.append(classification_filter)

    if category_filter != 'all':
        query += " AND category = ?"
        params.append(category_filter)

    if search_query:
        query += " AND (title LIKE ? OR filename LIKE ? OR description LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term])

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    files = cursor.fetchall()

    # Overall statistics
    cursor.execute("SELECT COUNT(*) as total FROM files WHERE is_archived = 0")
    total_files = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as public_count FROM files WHERE is_archived = 0 AND classification = 'public'")
    public_files = cursor.fetchone()['public_count']

    cursor.execute("SELECT COUNT(*) as member_count FROM files WHERE is_archived = 0 AND classification = 'member'")
    member_files = cursor.fetchone()['member_count']

    cursor.execute("SELECT COUNT(*) as confidential_count FROM files WHERE is_archived = 0 AND classification = 'confidential'")
    confidential_files = cursor.fetchone()['confidential_count']

    conn.close()

    return render_template('index.html',
                           files=files,
                           total_files=total_files,
                           public_files=public_files,
                           member_files=member_files,
                           confidential_files=confidential_files,
                           selected_classification=classification_filter,
                           selected_category=category_filter,
                           search_query=search_query)


@app.route('/circulars')
def circulars():
    """Public Notice Board specifically designed for university circulars and notices."""
    search_query = request.args.get('q', '').strip()
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM files WHERE is_archived = 0 AND classification = 'public'"
    params = []

    if search_query:
        query += " AND (title LIKE ? OR filename LIKE ? OR description LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term])

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    circular_files = cursor.fetchall()
    conn.close()

    return render_template('circulars.html', files=circular_files, search_query=search_query)


@app.route('/vault')
@role_required('core', 'admin')
def vault():
    """Exclusive Executive Core Vault for confidential club records, finances, and sensitive data."""
    search_query = request.args.get('q', '').strip()
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM files WHERE is_archived = 0 AND classification = 'confidential'"
    params = []

    if search_query:
        query += " AND (title LIKE ? OR filename LIKE ? OR description LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term])

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    vault_files = cursor.fetchall()
    conn.close()

    return render_template('vault.html', files=vault_files, search_query=search_query)


# ==========================================
# FILE UPLOAD & MANAGEMENT
# ==========================================

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    user = get_current_user()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'General')
        classification = request.form.get('classification', 'public')
        description = request.form.get('description', '').strip()
        access_pin = request.form.get('access_pin', '').strip() or None

        if 'file' not in request.files or not request.files['file'].filename:
            flash('Please choose a file to upload.', 'danger')
            return redirect(request.url)

        uploaded_file = request.files['file']
        orig_filename = secure_filename(uploaded_file.filename)
        if not orig_filename:
            orig_filename = f"file_{int(datetime.datetime.now().timestamp())}.dat"

        # Permission verification for classification
        if classification == 'confidential' and user['role'] not in ['core', 'admin']:
            flash('Only Executive Core Committee or Admin can upload Confidential documents.', 'danger')
            return redirect(request.url)

        if not title:
            title = orig_filename

        # Detect extension & mime type
        ext = ''
        if '.' in orig_filename:
            ext = orig_filename.rsplit('.', 1)[1].lower()

        mime_type = uploaded_file.mimetype or mimetypes.guess_type(orig_filename)[0] or 'application/octet-stream'

        # Generate isolated UUID for disk storage
        file_uuid = str(uuid.uuid4())
        disk_path = os.path.join(Config.STORAGE_FOLDER, file_uuid)

        # Save to disk
        uploaded_file.save(disk_path)
        file_size = os.path.getsize(disk_path)

        # Insert database record
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO files (
            file_uuid, filename, file_size, mime_type, extension,
            classification, category, title, description,
            uploader_id, uploader_name, access_pin
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_uuid, orig_filename, file_size, mime_type, ext,
            classification, category, title, description,
            user['id'], user['full_name'], access_pin
        ))
        new_file_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Audit log
        log_action(user['id'], user['username'], 'UPLOAD', 'FILE', new_file_id,
                   f"Uploaded '{orig_filename}' [{classification.upper()}] under category '{category}'")

        flash(f"File '{title}' uploaded successfully into the {classification.title()} repository!", 'success')
        return redirect(url_for('file_detail', file_id=new_file_id))

    return render_template('upload.html')


@app.route('/file/<int:file_id>')
def file_detail(file_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE id = ? AND is_archived = 0", (file_id,))
    file_row = cursor.fetchone()

    if not file_row:
        conn.close()
        flash('File not found or has been archived.', 'danger')
        return redirect(url_for('index'))

    user = get_current_user()
    provided_pin = request.args.get('pin')
    authorized, reason = can_access_file(file_row, user, provided_pin)

    # Increment view count
    cursor.execute("UPDATE files SET view_count = view_count + 1 WHERE id = ?", (file_id,))
    conn.commit()

    # Get recent audit logs for this file (visible to core/admin)
    logs = []
    if user and user['role'] in ['core', 'admin']:
        cursor.execute("SELECT * FROM audit_logs WHERE target_type = 'FILE' AND target_id = ? ORDER BY created_at DESC LIMIT 10", (str(file_id),))
        logs = cursor.fetchall()

    # Read inline preview content if permitted and previewable
    preview_content = None
    preview_error = None
    is_previewable = file_row['extension'] in Config.PREVIEWABLE_EXTS

    if authorized and is_previewable:
        disk_path = os.path.join(Config.STORAGE_FOLDER, file_row['file_uuid'])
        if os.path.exists(disk_path):
            if file_row['extension'] in {'txt', 'md', 'py', 'json', 'csv', 'js', 'html', 'css'}:
                try:
                    with open(disk_path, 'r', encoding='utf-8', errors='replace') as f:
                        preview_content = f.read(15000) # Read up to 15KB for preview
                except Exception as e:
                    preview_error = str(e)

    conn.close()

    return render_template('file_detail.html',
                           file=file_row,
                           authorized=authorized,
                           reason=reason,
                           is_previewable=is_previewable,
                           preview_content=preview_content,
                           preview_error=preview_error,
                           logs=logs,
                           provided_pin=provided_pin)


@app.route('/file/<int:file_id>/download')
def download_file(file_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE id = ? AND is_archived = 0", (file_id,))
    file_row = cursor.fetchone()

    if not file_row:
        conn.close()
        abort(404, description="File not found")

    user = get_current_user()
    provided_pin = request.args.get('pin') or request.form.get('pin')
    authorized, reason = can_access_file(file_row, user, provided_pin)

    if not authorized:
        conn.close()
        log_action(user['id'] if user else None,
                   user['username'] if user else 'Anonymous',
                   'DOWNLOAD_BLOCKED', 'FILE', file_id,
                   f"Unauthorized download attempt for '{file_row['filename']}' ({file_row['classification']})")
        flash(reason, 'danger')
        return redirect(url_for('file_detail', file_id=file_id))

    disk_path = os.path.join(Config.STORAGE_FOLDER, file_row['file_uuid'])
    if not os.path.exists(disk_path):
        conn.close()
        abort(404, description="Physical storage file missing on disk")

    # Increment download count
    cursor.execute("UPDATE files SET download_count = download_count + 1 WHERE id = ?", (file_id,))
    conn.commit()
    conn.close()

    # Audit log download
    log_action(user['id'] if user else None,
               user['username'] if user else 'Anonymous',
               'DOWNLOAD', 'FILE', file_id,
               f"Downloaded file '{file_row['filename']}' [{file_row['classification'].upper()}]")

    return send_file(
        disk_path,
        as_attachment=True,
        download_name=file_row['filename'],
        mimetype=file_row['mime_type'] or 'application/octet-stream'
    )


@app.route('/file/<int:file_id>/view_raw')
def view_raw_file(file_id):
    """Serve file for inline browser viewing (PDFs, images)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE id = ? AND is_archived = 0", (file_id,))
    file_row = cursor.fetchone()

    if not file_row:
        conn.close()
        abort(404)

    user = get_current_user()
    provided_pin = request.args.get('pin')
    authorized, reason = can_access_file(file_row, user, provided_pin)

    if not authorized:
        conn.close()
        abort(403, description=reason)

    disk_path = os.path.join(Config.STORAGE_FOLDER, file_row['file_uuid'])
    conn.close()

    return send_file(
        disk_path,
        as_attachment=False,
        download_name=file_row['filename'],
        mimetype=file_row['mime_type'] or 'application/octet-stream'
    )


@app.route('/file/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_file(file_id):
    user = get_current_user()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
    file_row = cursor.fetchone()

    if not file_row:
        conn.close()
        flash('File not found.', 'danger')
        return redirect(url_for('index'))

    # Only uploader or admin/core can delete
    if user['role'] not in ['admin', 'core'] and file_row['uploader_id'] != user['id']:
        conn.close()
        flash('You are not authorized to delete this file.', 'danger')
        return redirect(url_for('file_detail', file_id=file_id))

    # Mark as archived or remove
    cursor.execute("UPDATE files SET is_archived = 1 WHERE id = ?", (file_id,))
    conn.commit()
    conn.close()

    log_action(user['id'], user['username'], 'DELETE', 'FILE', file_id,
               f"Archived file '{file_row['filename']}' ({file_row['classification']})")

    flash(f"File '{file_row['title']}' removed from portal.", 'success')
    return redirect(url_for('index'))


# ==========================================
# SECURE SHAREABLE LINKS
# ==========================================

@app.route('/file/<int:file_id>/share', methods=['POST'])
@login_required
def create_share_link(file_id):
    user = get_current_user()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE id = ? AND is_archived = 0", (file_id,))
    file_row = cursor.fetchone()

    if not file_row:
        conn.close()
        flash('File not found.', 'danger')
        return redirect(url_for('index'))

    # Check permission to share
    authorized, reason = can_access_file(file_row, user)
    if not authorized:
        conn.close()
        flash(f"Cannot generate share link: {reason}", 'danger')
        return redirect(url_for('file_detail', file_id=file_id))

    expiry_days = int(request.form.get('expiry_days', 7))
    max_downloads = request.form.get('max_downloads', '').strip()
    max_downloads = int(max_downloads) if max_downloads.isdigit() else None

    token = uuid.uuid4().hex[:16]
    expires_at = datetime.datetime.now() + datetime.timedelta(days=expiry_days)

    cursor.execute('''
    INSERT INTO share_links (file_id, token, created_by, expires_at, max_downloads)
    VALUES (?, ?, ?, ?, ?)
    ''', (file_id, token, user['id'], expires_at, max_downloads))
    conn.commit()
    conn.close()

    log_action(user['id'], user['username'], 'SHARE_GENERATE', 'FILE', file_id,
               f"Created share token '{token}' expiring in {expiry_days} days")

    share_url = url_for('access_share_link', token=token, _external=True)
    flash(f"Share link created! Direct link: {share_url}", 'info')
    return redirect(url_for('file_detail', file_id=file_id))


@app.route('/share/<token>')
def access_share_link(token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT sl.*, f.filename, f.file_uuid, f.file_size, f.mime_type, f.title, f.classification, f.description
    FROM share_links sl
    JOIN files f ON sl.file_id = f.id
    WHERE sl.token = ? AND f.is_archived = 0
    ''', (token,))
    share = cursor.fetchone()

    if not share:
        conn.close()
        abort(404, description="Invalid or expired share link")

    # Expiry verification
    if share['expires_at']:
        exp = datetime.datetime.fromisoformat(str(share['expires_at']))
        if datetime.datetime.now() > exp:
            conn.close()
            return render_template('share_expired.html', message="This secure share link has expired.")

    # Download limit check
    if share['max_downloads'] and share['download_count'] >= share['max_downloads']:
        conn.close()
        return render_template('share_expired.html', message="This share link has reached its maximum allowed downloads.")

    # Handle download action
    if request.args.get('download') == '1':
        disk_path = os.path.join(Config.STORAGE_FOLDER, share['file_uuid'])
        cursor.execute("UPDATE share_links SET download_count = download_count + 1 WHERE id = ?", (share['id'],))
        cursor.execute("UPDATE files SET download_count = download_count + 1 WHERE id = ?", (share['file_id'],))
        conn.commit()
        conn.close()

        log_action(None, 'Token Holder', 'SHARE_DOWNLOAD', 'FILE', share['file_id'],
                   f"Downloaded via token '{token}'")

        return send_file(disk_path, as_attachment=True, download_name=share['filename'], mimetype=share['mime_type'])

    conn.close()
    return render_template('share_landing.html', share=share)


# ==========================================
# AUTHENTICATION & USER MANAGEMENT
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if quick demo login was clicked
        demo_user = request.form.get('demo_user')
        if demo_user:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (demo_user,))
            user = cursor.fetchone()
            conn.close()
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['full_name'] = user['full_name']
                session['email'] = user['email']
                log_action(user['id'], user['username'], 'LOGIN_DEMO', 'USER', user['id'], f"Logged in with {user['role']} role")
                flash(f"Welcome back, {user['full_name']}! Signed in as [{user['role'].upper()}].", 'success')
                return redirect(url_for('index'))

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            session['email'] = user['email']

            log_action(user['id'], user['username'], 'LOGIN', 'USER', user['id'], "User signed in successfully")
            flash(f"Welcome to Technoverse Portal, {user['full_name']}!", 'success')
            next_url = request.args.get('next') or url_for('index')
            return redirect(next_url)
        else:
            flash('Invalid username or password. Check credentials or try one-click demo login.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        student_id = request.form.get('student_id', '').strip()
        department = request.form.get('department', '').strip()
        password = request.form.get('password', '').strip()

        if not (username and full_name and email and password):
            flash('All core fields are required.', 'danger')
            return redirect(request.url)

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO users (username, full_name, email, password_hash, role, student_id, department)
            VALUES (?, ?, ?, ?, 'student', ?, ?)
            ''', (username, full_name, email, generate_password_hash(password), student_id, department))
            user_id = cursor.lastrowid
            conn.commit()

            log_action(user_id, username, 'REGISTER', 'USER', user_id, f"Registered student from {department}")
            flash('Registration successful! You may now sign in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Registration failed: Username or Email may already exist.", 'danger')
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/logout')
def logout():
    user = get_current_user()
    if user:
        log_action(user['id'], user['username'], 'LOGOUT', 'USER', user['id'], "User signed out")
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))


@app.route('/users')
@role_required('admin', 'core')
def users_list():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, email, role, student_id, department, created_at FROM users ORDER BY id ASC")
    users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>/role', methods=['POST'])
@role_required('admin')
def update_user_role(user_id):
    new_role = request.form.get('role')
    if new_role not in ['student', 'member', 'core', 'admin']:
        flash('Invalid role specified.', 'danger')
        return redirect(url_for('users_list'))

    admin_user = get_current_user()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()

    log_action(admin_user['id'], admin_user['username'], 'PERMISSION_CHANGE', 'USER', user_id,
               f"Promoted/changed user {user_id} role to '{new_role.upper()}'")

    flash(f"User role updated to '{new_role.upper()}'.", 'success')
    return redirect(url_for('users_list'))


# ==========================================
# AUDIT & ACTIVITY LOGS (ADMIN / CORE)
# ==========================================

@app.route('/logs')
@role_required('admin', 'core')
def logs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 100")
    audit_records = cursor.fetchall()
    conn.close()
    return render_template('logs.html', logs=audit_records)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
