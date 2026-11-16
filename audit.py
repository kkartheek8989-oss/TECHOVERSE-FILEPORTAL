from database import get_db
from flask import request

def log_action(user_id, user_identifier, action, target_type, target_id, details=''):
    """
    Inserts a tamper-evident audit record into audit_logs table.
    """
    ip_addr = request.remote_addr if request else '127.0.0.1'
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO audit_logs (user_id, user_identifier, action, target_type, target_id, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_identifier, action, target_type, str(target_id), details, ip_addr))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging audit trail: {e}")
