import os
import io
import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_credentials():
    """
    Attempts to load Google Service Account credentials from:
    1. GOOGLE_SERVICE_ACCOUNT_JSON environment variable (raw JSON string or base64)
    2. GOOGLE_SERVICE_ACCOUNT_FILE environment variable path
    3. Local service_account.json in the project root
    """
    # 1. Check environment variable for JSON string or base64
    sa_json_str = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if sa_json_str:
        sa_json_str = sa_json_str.strip()
        try:
            # Check if base64 encoded
            if not sa_json_str.startswith('{'):
                sa_json_str = base64.b64decode(sa_json_str).decode('utf-8')
            info = json.loads(sa_json_str)
            return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        except Exception as e:
            print(f"[GDrive] Failed to parse GOOGLE_SERVICE_ACCOUNT_JSON env var: {e}")

    # 2. Check path from env or local file
    sa_file = os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE', 'service_account.json')
    if os.path.exists(sa_file):
        try:
            return service_account.Credentials.from_service_account_file(sa_file, scopes=SCOPES)
        except Exception as e:
            print(f"[GDrive] Failed to load credentials from file {sa_file}: {e}")

    return None

def is_gdrive_enabled():
    """Returns True if Google Drive service account is configured."""
    return get_credentials() is not None

def get_drive_folder_id():
    """Target Google Drive folder ID to store uploaded files."""
    return os.environ.get('GDRIVE_FOLDER_ID', '').strip() or None

def get_drive_service():
    creds = get_credentials()
    if not creds:
        return None
    return build('drive', 'v3', credentials=creds, cache_discovery=False)

def upload_to_drive(file_obj, filename, mime_type=None):
    """
    Uploads a file stream or file-like object directly into the designated Google Drive folder.
    Returns (drive_file_id, web_view_link) or (None, None) on failure.
    """
    service = get_drive_service()
    if not service:
        return None, None

    folder_id = get_drive_folder_id()
    file_metadata = {
        'name': filename
    }
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaIoBaseUpload(
        file_obj,
        mimetype=mime_type or 'application/octet-stream',
        resumable=True
    )

    try:
        file_res = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        return file_res.get('id'), file_res.get('webViewLink')
    except Exception as e:
        print(f"[GDrive] Error uploading '{filename}' to Google Drive: {e}")
        return None, None

def download_from_drive(drive_file_id):
    """
    Downloads media bytes from Google Drive.
    Returns io.BytesIO containing file data.
    """
    service = get_drive_service()
    if not service:
        return None

    try:
        request = service.files().get_media(fileId=drive_file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh
    except Exception as e:
        print(f"[GDrive] Error downloading file {drive_file_id} from Google Drive: {e}")
        return None

def delete_from_drive(drive_file_id):
    """Deletes a file permanently from Google Drive."""
    service = get_drive_service()
    if not service or not drive_file_id:
        return False
    try:
        service.files().delete(fileId=drive_file_id).execute()
        return True
    except Exception as e:
        print(f"[GDrive] Error deleting file {drive_file_id} from Google Drive: {e}")
        return False
