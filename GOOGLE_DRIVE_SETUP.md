# 📂 Setting Up Google Drive as the Backend Storage (100% Free • 15 GB)

TechnoVault supports **Google Drive** as its primary cloud storage engine! 
Files uploaded through the portal are automatically sent to your designated Google Drive folder, and downloads/previews are securely streamed through the portal while maintaining all Role-Based Access Controls and Confidentiality PINs.

---

## ⚡ 3-Step Setup Guide

### Step 1: Create a Free Google Service Account (2 Minutes)
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., `TechnoVault-Drive`) or select an existing one.
3. In the search bar at the top, search for **"Google Drive API"** and click **Enable**.
4. Go to **APIs & Services** > **Credentials** > **Create Credentials** > **Service Account**.
   - Name it `technovault-uploader` and click **Create and Continue**.
   - Role: Select **Basic > Editor** (or leave default) and click **Done**.
5. Click on the created service account email (e.g., `technovault-uploader@<project-id>.iam.gserviceaccount.com`).
6. Go to the **Keys** tab > **Add Key** > **Create new key** > Select **JSON** > Click **Create**.
7. A `.json` credentials file will download to your computer.

---

### Step 2: Create a Google Drive Folder & Share with Service Account
1. Open [Google Drive](https://drive.google.com/).
2. Create a new folder (e.g., `TechnoVault Files`).
3. Right-click the folder > **Share**.
4. Paste the Service Account Email (from Step 1) into the invite box, set permission to **Editor**, and click **Share**.
5. Look at your browser address bar when inside the folder:
   ```
   https://drive.google.com/drive/folders/1aBcDeFgHiJkLmNoPqRsTuVwXyZ12345
   ```
   The string after `/folders/` (e.g., `1aBcDeFgHiJkLmNoPqRsTuVwXyZ12345`) is your **`GDRIVE_FOLDER_ID`**.

---

### Step 3: Configure Environment Variables

#### Option A: On Render.com (Cloud Deployment)
In your Render Dashboard for `TECHOVERSE-FILEPORTAL`:
1. Go to **Environment** tab on the left sidebar.
2. Click **Add Environment Variable**:
   - **Key**: `GDRIVE_FOLDER_ID`
   - **Value**: *(Paste your folder ID from Step 2)*
3. Click **Add Environment Variable**:
   - **Key**: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - **Value**: *(Open the downloaded `.json` file in Notepad, copy the ENTIRE JSON text, and paste it here)*
4. Click **Save Changes**. Render will automatically redeploy, and Google Drive will be active!

#### Option B: For Local Development
1. Rename your downloaded credentials file to `service_account.json` and place it in this project directory.
2. Create or edit a `.env` file with:
   ```env
   GDRIVE_FOLDER_ID=your_drive_folder_id_here
   ```
3. Restart the server with `python run.py`. You will see `Google Drive Backend Active` on the top bar!
