import sqlite3
import os
import uuid
from werkzeug.security import generate_password_hash
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(Config.STORAGE_FOLDER, exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        student_id TEXT,
        department TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_approved INTEGER DEFAULT 1
    )
    ''')

    # Files Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_uuid TEXT UNIQUE NOT NULL,
        filename TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        mime_type TEXT,
        extension TEXT,
        classification TEXT NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        uploader_id INTEGER NOT NULL,
        uploader_name TEXT NOT NULL,
        access_pin TEXT,
        download_count INTEGER DEFAULT 0,
        view_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_archived INTEGER DEFAULT 0,
        FOREIGN KEY (uploader_id) REFERENCES users (id)
    )
    ''')

    # Share Links Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS share_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        created_by INTEGER NOT NULL,
        expires_at TIMESTAMP,
        max_downloads INTEGER,
        download_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (file_id) REFERENCES files (id),
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    ''')

    # Audit Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_identifier TEXT NOT NULL,
        action TEXT NOT NULL,
        target_type TEXT NOT NULL,
        target_id TEXT,
        details TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()

    # Seed Default Users if none exist
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()['count'] == 0:
        seed_users = [
            (
                'admin',
                'Prof. Hari Krishna (Club Patron & Admin)',
                'admin@hariuniv.edu.in',
                generate_password_hash('technoverse2026'),
                'admin',
                'FACULTY-HU-01',
                'Faculty of Computing & Technology'
            ),
            (
                'core_lead',
                'Kartheek (President - Technoverse Club)',
                'kartheek@technoverse.hariuniv.edu.in',
                generate_password_hash('core1234'),
                'core',
                'HU-2023-CSE-001',
                'Computer Science & Engineering'
            ),
            (
                'member_tech',
                'Aarav Sharma (Technical Lead)',
                'aarav@technoverse.hariuniv.edu.in',
                generate_password_hash('member123'),
                'member',
                'HU-2024-AI-042',
                'Artificial Intelligence & Data Science'
            ),
            (
                'student_user',
                'Ananya Patel (Student Member)',
                'ananya@student.hariuniv.edu.in',
                generate_password_hash('student123'),
                'student',
                'HU-2025-ECE-088',
                'Electronics & Communication'
            )
        ]
        cursor.executemany('''
        INSERT INTO users (username, full_name, email, password_hash, role, student_id, department)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', seed_users)
        conn.commit()

    # Seed Default Files (Sample circulars and documents) if none exist
    cursor.execute("SELECT COUNT(*) as count FROM files")
    if cursor.fetchone()['count'] == 0:
        # Sample 1: Public Circular
        c1_uuid = str(uuid.uuid4())
        c1_path = os.path.join(Config.STORAGE_FOLDER, c1_uuid)
        c1_content = """========================================================================
             HARI UNIVERSITY - OFFICE OF THE REGISTRAR
                 TECHNOVERSE INNOVATION & TECH CLUB
========================================================================
Ref: HU/CIRCULAR/TECH/2026/089                               Date: Nov 16, 2026

CIRCULAR: ANNUAL HACKATHON & INNOVATION CONCLAVE 2026-27

1. Technoverse Club, Hari University is thrilled to announce the upcoming
   48-hour National Level Hackathon: "INNOVERSE 2026".
2. Eligibility: All undergraduate and postgraduate students of Hari University
   and affiliated institutions.
3. Tracks:
   - Artificial Intelligence & Agentic Workflows
   - Cyber Security & Zero-Trust Cloud Architectures
   - Sustainable Tech & Smart Campus IoT
4. Important Dates:
   - Problem Statement Release: 1st Dec 2026
   - Prototype Submission: 15th Dec 2026
   - Grand Finale Demo Day: 22nd Dec 2026

All department HODs are requested to circulate this notice to student groups.

Sd/-
Dr. V. Ramanathan
Dean of Student Affairs & Patron, Technoverse Club
Hari University
========================================================================
"""
        with open(c1_path, 'w', encoding='utf-8') as f:
            f.write(c1_content)

        # Sample 2: Public Workshop Schedule
        c2_uuid = str(uuid.uuid4())
        c2_path = os.path.join(Config.STORAGE_FOLDER, c2_uuid)
        c2_content = """TECHNOVERSE CLUB - WORKSHOP SCHEDULE (SEMESTER EVEN 2026)
------------------------------------------------------------------------
Topic: Building Cloud Native & Microservice Applications with Python
Venue: Tech Auditorium - Block C, Hari University
Fee: 100% FREE for all Hari University Students

Syllabus:
Week 1: Modern Python 3.12, Asynchronous APIs & REST Principles
Week 2: Secure File Handling, Cryptography, and Role-Based Access Control
Week 3: Containerization with Docker & Multi-Node Cluster Deployment
Week 4: Real-time Data Streaming & Webhook Pipelines

Bring your laptops with Python and VS Code installed.
Registration link: https://portal.technoverse.hariuniv.edu.in/register
------------------------------------------------------------------------
Organized by: Technoverse Core Committee, Hari University
"""
        with open(c2_path, 'w', encoding='utf-8') as f:
            f.write(c2_content)

        # Sample 3: Member-Only Doc
        c3_uuid = str(uuid.uuid4())
        c3_path = os.path.join(Config.STORAGE_FOLDER, c3_uuid)
        c3_content = """[TECHNOVERSE CLUB INTERNAL - MEMBERS REPOSITORY]
Document: Club Infrastructure Architecture & GitHub Org Standards
Classification: CLUB MEMBER ACCESS ONLY

1. Code Style Guide: PEP 8 with Black & Flake8 formatting.
2. Branch Protection: Main branch requires 2 approvals from Core Committee.
3. Server Access: Staging environment runs on Hari University Local Cloud cluster.
4. Member Guidelines: Do not share club internal credentials or draft hackathon problem statements publicly.
"""
        with open(c3_path, 'w', encoding='utf-8') as f:
            f.write(c3_content)

        # Sample 4: Confidential Executive Board Document
        c4_uuid = str(uuid.uuid4())
        c4_path = os.path.join(Config.STORAGE_FOLDER, c4_uuid)
        c4_content = """[CONFIDENTIAL - HARI UNIVERSITY TECHNOVERSE CORE COMMITTEE ONLY]
Classification Level: STRICTLY CONFIDENTIAL - EXECUTIVE BOARD
Subject: Annual Budget Allocation, Faculty Grants & Sponsor Agreements (FY 2026-27)

1. Total University Sanctioned Grant: INR 2,50,000/-
2. Industry Sponsorships Confirmed:
   - TechCorp India: INR 1,50,000/- (Lead Conclave Sponsor)
   - CloudSolutions Global: Cloud Credits ($5,000 USD)
3. Budget Breakdown:
   - Hackathon Prizes & Swag: INR 1,80,000
   - Cloud Servers & Infrastructure: INR 45,000
   - Refreshments & Logistics: INR 75,000
4. Core Member Access Pass:
   Access to raw bank statements and vendor invoices requires written concurrence
   from Faculty Advisor Prof. Hari Krishna.
"""
        with open(c4_path, 'w', encoding='utf-8') as f:
            f.write(c4_content)

        sample_files = [
            (
                c1_uuid,
                'HU_Circular_Hackathon_2026.txt',
                len(c1_content.encode('utf-8')),
                'text/plain',
                'txt',
                'public',
                'Circulars & Notices',
                'HU Circular #089: Annual Hackathon & Innovation Conclave 2026',
                'Official circular from Registrar & Dean of Student Affairs regarding the Technoverse Annual Conclave.',
                1,
                'Prof. Hari Krishna (Club Patron)',
                None,
                14,
                38
            ),
            (
                c2_uuid,
                'Workshop_Python_Cloud_Schedule.txt',
                len(c2_content.encode('utf-8')),
                'text/plain',
                'txt',
                'public',
                'Workshops & Code',
                'Python & Cloud Native Workshop 4-Week Schedule',
                'Free hands-on workshop curriculum for all enrolled students at Hari University.',
                2,
                'Kartheek (President)',
                None,
                29,
                82
            ),
            (
                c3_uuid,
                'Technoverse_Internal_Dev_Standards.txt',
                len(c3_content.encode('utf-8')),
                'text/plain',
                'txt',
                'member',
                'Study Resources',
                'Club Internal Dev Standards & Repository Guidelines',
                'Guidelines for active club project contributors and development teams.',
                3,
                'Aarav Sharma (Technical Lead)',
                None,
                8,
                19
            ),
            (
                c4_uuid,
                'Confidential_Budget_Allocation_2026_27.txt',
                len(c4_content.encode('utf-8')),
                'text/plain',
                'txt',
                'confidential',
                'Finances & Budgets',
                'Executive Committee FY 2026-27 Budget & Grants Allocation',
                'Confidential financial breakdown and sponsorship distribution. Core committee only.',
                1,
                'Prof. Hari Krishna (Club Patron)',
                '7788',  # Optional secondary PIN
                2,
                7
            )
        ]

        cursor.executemany('''
        INSERT INTO files (
            file_uuid, filename, file_size, mime_type, extension,
            classification, category, title, description,
            uploader_id, uploader_name, access_pin, download_count, view_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_files)

        # Log initial seeds
        cursor.execute('''
        INSERT INTO audit_logs (user_id, user_identifier, action, target_type, target_id, details, ip_address)
        VALUES (1, 'SYSTEM', 'INITIALIZATION', 'SYSTEM', 'PORTAL', 'Initialized TechnoVault with security roles and seed files', '127.0.0.1')
        ''')
        conn.commit()

    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
