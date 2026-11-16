# 🚀 Deployment Guide (100% Free • Zero Supabase Required)

**TechnoVault** is designed from the ground up to be **completely independent of Supabase**, AWS, or paid third-party database services. It uses Python's built-in **SQLite** database and an **isolated local filesystem storage engine** (`storage/`).

Below are the 3 best ways to deploy it online for free.

---

## 🌟 Method 1: Render.com (Recommended Free Cloud Hosting)

Render provides a **free web service tier** with automated SSL (HTTPS) and continuous deployment from GitHub.

### Step-by-Step:
1. **Push your code to GitHub**:
   - Create a new free repository on [GitHub](https://github.com/new) (e.g. `technoverse-file-portal`).
   - In your project folder:
     ```bash
     git init
     git add .
     git commit -m "Initial commit for Technoverse portal"
     git branch -M main
     git remote add origin https://github.com/<YOUR_USERNAME>/technoverse-file-portal.git
     git push -u origin main
     ```

2. **Deploy on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com) and sign in with GitHub (No credit card required).
   - Click **New +** > **Web Service**.
   - Select your repository `technoverse-file-portal`.
   - Fill in the basic settings:
     - **Name**: `technoverse-hari-univ`
     - **Language**: `Python 3`
     - **Region**: Closest to you (e.g., Singapore or Frankfurt)
     - **Branch**: `main`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 app:app`
     - **Instance Type**: **Free**
   - Click **Deploy Web Service**.

3. **Done!**  
   In 2 minutes, your portal will be live at `https://technoverse-hari-univ.onrender.com`.

---

## 🐍 Method 2: PythonAnywhere (100% Free Forever • Built for Python & SQLite)

PythonAnywhere is specifically built for Python + SQLite web applications. You get free permanent persistent storage and your own custom subdomain (`<yourusername>.pythonanywhere.com`).

### Step-by-Step:
1. Sign up for a free account at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Go to the **Files** tab and upload your `technoverse-file-portal` folder (or open the **Bash console** and clone your GitHub repo):
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/technoverse-file-portal.git
   ```
3. In the Bash console, install dependencies:
   ```bash
   pip3 install -r technoverse-file-portal/requirements.txt
   ```
4. Go to the **Web** tab:
   - Click **Add a new web app**.
   - Choose **Manual configuration** > **Python 3.12**.
5. In the **WSGI configuration file** link, edit the file to point to your app:
   ```python
   import sys
   path = '/home/<yourusername>/technoverse-file-portal'
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```
6. Click the green **Reload <yourusername>.pythonanywhere.com** button.
7. Your portal is live with persistent storage!

---

## 🐳 Method 3: Self-Hosted / Campus Linux Server / Free Oracle Cloud VPS (Docker)

If you have a campus computer, lab server, or free cloud VM (e.g., Oracle Cloud Always-Free ARM VM), you can deploy with a single Docker command.

### Step-by-Step:
1. Ensure Docker is installed on your server.
2. In the project folder, run:
   ```bash
   docker compose up -d
   ```
3. Docker will build the container, mount persistent storage volumes for `./storage` and `./technoverse.db`, and run the portal in the background.
4. Access it at `http://<server-ip>:5000`.

---

## 🔒 Verification That Supabase is NOT Used:
- Database: Built-in `sqlite3` (file: `technoverse.db`)
- File Storage: Local filesystem (directory: `/storage`)
- Authentication: Built-in `werkzeug.security` SHA-256 salted hashes
- Zero external dependencies, zero credit card requirements, zero API keys required.
