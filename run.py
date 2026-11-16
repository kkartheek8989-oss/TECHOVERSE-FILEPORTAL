import os
import sys
from app import app
from database import init_db

def print_banner():
    banner = r"""
  ╔════════════════════════════════════════════════════════════════════════════╗
  ║    TECHNOVAULT v2.4 - SECURE FILE & CIRCULAR HOSTING CLOUD PORTAL         ║
  ║              TECHNOVERSE CLUB • HARI UNIVERSITY                            ║
  ╚════════════════════════════════════════════════════════════════════════════╝
  [+] Platform: Python 3.12 + Flask + SQLite (100% Free & Self-Hosted)
  [+] Storage: Isolated UUID-Hashed Object Directory
  [+] Access Controls: Role-Based (Student, Member, Core Lead, Admin)
  [+] Public Hub: /circulars (University Circulars & Open Notices)
  [+] Vault: /vault (Strictly Confidential Documents & Financial Records)
  ─────────────────────────────────────────────────────────────────────────────
  Default Demo Accounts (Or use 1-click login buttons on the sign-in page):
  • Admin / Patron:    admin       | Password: technoverse2026
  • Core President:    core_lead   | Password: core1234
  • Technical Member:  member_tech | Password: member123
  • Student:           student_user| Password: student123
  ─────────────────────────────────────────────────────────────────────────────
  Server running at: http://127.0.0.1:5000
    """
    print(banner)

if __name__ == '__main__':
    init_db()
    print_banner()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
