import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'technoverse-hari-univ-super-secret-key-2026')
    STORAGE_FOLDER = os.path.join(BASE_DIR, 'storage')
    DATABASE_PATH = os.path.join(BASE_DIR, 'technoverse.db')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB max file upload
    
    # Classification Levels
    CLASSIFICATION_PUBLIC = 'public'             # Anyone / Circulars / Open
    CLASSIFICATION_MEMBER = 'member'             # Registered Club Members
    CLASSIFICATION_CONFIDENTIAL = 'confidential' # Executive Core & Faculty Admin Only
    
    # Categories
    CATEGORIES = [
        'Circulars & Notices',
        'Workshops & Code',
        'Hackathons & Projects',
        'Study Resources',
        'Meeting Minutes',
        'Finances & Budgets',
        'Event Assets',
        'General'
    ]
    
    # Allowed Extensions previewable inline
    PREVIEWABLE_EXTS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'txt', 'md', 'py', 'json', 'csv', 'js', 'html', 'css'}
