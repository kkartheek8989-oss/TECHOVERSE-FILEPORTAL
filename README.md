# 🚀 TechnoVault — File Hosting Portal
### Official Cloud Repository & Circular Archive for **Technoverse Club, Hari University**

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python: 3.12](https://img.shields.io/badge/Python-3.12-cyan.svg)
![Framework: Flask](https://img.shields.io/badge/Framework-Flask_3-emerald.svg)
![Cost: 100% Free](https://img.shields.io/badge/Cost-100%25_FREE-success.svg)

---

## 🌟 Overview

**TechnoVault** is an enterprise-grade, lightweight, and 100% free self-hosted file hosting and document distribution portal built exclusively for **Technoverse Club, Hari University**. 

It handles everything from **official university circulars and notices** for all students, to **club member project assets and workshop code**, up to **strictly confidential executive committee records and financial grant disbursements**.

---

## 🛡️ 3-Tier Security & Classification Model

| Classification | Clearance Required | Typical Documents | Visibility & Access |
| :--- | :--- | :--- | :--- |
| 📢 **Public** | **None** (Any student/faculty) | University Circulars, Hackathon Guidelines, Workshop Fliers, Open Study Notes | Open directly at `/circulars` without login. |
| 👥 **Club Member** | **Member, Core Lead, Admin** | Project Source Code, Design Kits, Hackathon Submissions, Workshop Resources | Requires club member credentials. |
| 🔒 **Confidential** | **Executive Core & Patron Only** | Budget Sheets, Grant Documents, Meeting Minutes, Challenge Keys | Restricted to `/vault`. Supports optional secondary PIN for dual-factor file unlocking. |

---

## ✨ Key Features

1. **📢 Public Notice & Circulars Hub (`/circulars`)**:
   - Hari University students and faculty can browse and download circulars instantly without registration or login.
2. **🔐 Executive Confidential Vault (`/vault`)**:
   - Isolated repository with strict Role-Based Access Control (RBAC).
   - Optional Document PIN protection for high-value files (even core members must provide the PIN).
3. **📁 UUID-Isolated Storage**:
   - Files are stored on disk under non-guessable cryptographic UUIDs outside the public static directory.
   - Prevents directory traversal, file scraping, and unauthenticated hotlinking.
4. **👁️ In-Browser Document Preview**:
   - Directly previews PDFs, images (PNG, JPG, SVG), and code/text (Python, Markdown, JSON, CSV) in the browser.
5. **🔗 Secure Controlled Share Links**:
   - Generate expiring URLs (24 hrs, 3 days, 7 days, 30 days) and set download limits (e.g., burn after 5 downloads) for external guests or judges.
6. **📜 Tamper-Evident Audit Logs (`/logs`)**:
   - Every file download, view, upload, role change, and deletion is timestamped and recorded with IP addresses.
7. **⚡ Zero Recurring Cost**:
   - Pure Python standard library + Flask + SQLite. No expensive external cloud database or paid subscription needed.

---

## 🚀 Quick Start Guide

### 1. Run Locally
Open a terminal in this directory and start the server:

```powershell
python run.py
```

The portal will initialize the SQLite database and start at:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Pre-Seeded Accounts (Or use 1-Click Login buttons on the Sign-In page)

| Role | Username | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Admin / Patron** | `admin` | `technoverse2026` | Full Control, User Roles, All Vault Docs, Audit Logs |
| **Core Lead (President)** | `core_lead` | `core1234` | Confidential Vault, Uploads, File Deletions, Audit Logs |
| **Club Member (Tech Lead)**| `member_tech` | `member123` | Member Repositories, Uploads, Public Circulars |
| **Student** | `student_user`| `student123` | Public Circulars, Member Repositories Overview |

---

## 🌐 100% Free Cloud Deployment Options

You can host this portal online 24/7 for **$0 / month** using any of these free platforms:

### Option A: Render.com (Recommended Free Tier)
1. Push this folder to a GitHub repository.
2. In [Render.com](https://render.com), click **New + > Web Service**.
3. Connect your repository.
4. Settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (or `python run.py`)
5. Click **Deploy**. Your portal will be live at `https://technoverse-hari-univ.onrender.com`.

### Option B: PythonAnywhere (Free Tier)
1. Create a free account on [PythonAnywhere](https://www.pythonanywhere.com).
2. Upload the project files into your directory.
3. In the "Web" tab, configure a manual Flask app pointing to `app.py`.

### Option C: University Intranet / Local Server
To make this accessible across Hari University Wi-Fi / campus LAN:
Run:
```powershell
python run.py
```
Find your machine's local IP (e.g. `192.168.1.50`). Students on campus Wi-Fi can connect via `http://192.168.1.50:5000`!

---

## 📂 Project Directory Structure

```text
technoverse-file-portal/
├── app.py                 # Core Flask routing, RBAC checks, stream downloads
├── database.py            # SQLite schema, migrations & seed data
├── auth.py                # Session authentication & clearance decorators
├── audit.py               # Security audit logging engine
├── config.py              # Configurations & file limits
├── run.py                 # Interactive startup runner with banner
├── requirements.txt       # Python dependencies
├── storage/               # Isolated storage for uploaded documents (UUID-indexed)
├── static/
│   ├── css/style.css      # Styling & glassmorphism touches
│   └── js/main.js         # Client-side copy helpers & interactions
└── templates/
    ├── base.html          # University header, navbar, flash messages
    ├── index.html         # Portal dashboard with filter tabs & metrics
    ├── circulars.html     # Public Notice Board for circulars
    ├── vault.html         # Restricted Executive Vault for core committee
    ├── upload.html        # Drag-and-drop upload with clearance selector
    ├── file_detail.html   # File metadata, inline preview & share links
    ├── login.html         # Sign-in with 1-click test profiles
    ├── register.html      # Student self-registration
    ├── users.html         # Member & role promotion management
    ├── logs.html          # Compliance & audit trail viewer
    ├── share_landing.html # Clean external recipient download page
    └── share_expired.html # Expired share link notification
```

---
**Developed for TECHNOVERSE CLUB • HARI UNIVERSITY (2026)**
