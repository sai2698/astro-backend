import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import google.auth.transport.requests
import logging

logger = logging.getLogger(__name__)

# Note: In production, the path to the service account JSON should be in an environment variable (e.g. GOOGLE_APPLICATION_CREDENTIALS)
# For this implementation, we will expect a file named "google-credentials.json" in the root of the backend folder.
CREDENTIALS_FILE = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "google-credentials.json"))
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
_cached_creds = None

def get_access_token() -> str:
    """Returns a valid access token for the service account."""
    global _cached_creds
    if not os.path.exists(CREDENTIALS_FILE):
        return None
    try:
        if not _cached_creds:
            _cached_creds = service_account.Credentials.from_service_account_file(
                CREDENTIALS_FILE, scopes=SCOPES)
        if not _cached_creds.valid:
            request = google.auth.transport.requests.Request()
            _cached_creds.refresh(request)
        return _cached_creds.token
    except Exception as e:
        logger.error(f"Error getting Google Drive access token: {e}")
        return None

def get_drive_service():
    """Initializes and returns the Google Drive API service."""
    if not os.path.exists(CREDENTIALS_FILE):
        logger.warning(f"Google Drive credentials file not found at {CREDENTIALS_FILE}. Drive sharing will not work.")
        return None
        
    try:
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Error initializing Google Drive service: {e}")
        return None

def grant_reader_access(folder_id: str, email: str) -> str:
    """
    Grants reader access to the specified folder for the given email.
    Returns the permission ID if successful, or None.
    """
    service = get_drive_service()
    if not service or not folder_id:
        return None
        
    try:
        permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': email
        }
        # sendNotificationEmail defaults to True, which is good so the user knows they have access
        created_permission = service.permissions().create(
            fileId=folder_id,
            body=permission,
            fields='id'
        ).execute()
        
        logger.info(f"Successfully granted access to {email} for folder {folder_id}")
        return created_permission.get('id')
    except Exception as e:
        logger.error(f"Error granting drive access to {email} for folder {folder_id}: {e}")
        return None

def revoke_access(folder_id: str, permission_id: str) -> bool:
    """
    Revokes access for a specific permission ID on a folder.
    Returns True if successful, False otherwise.
    """
    service = get_drive_service()
    if not service or not folder_id or not permission_id:
        return False
        
    try:
        service.permissions().delete(
            fileId=folder_id,
            permissionId=permission_id
        ).execute()
        
        logger.info(f"Successfully revoked permission {permission_id} for folder {folder_id}")
        return True
    except Exception as e:
        logger.error(f"Error revoking permission {permission_id} for folder {folder_id}: {e}")
        return False
