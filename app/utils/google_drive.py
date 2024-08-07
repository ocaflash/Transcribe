from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import os
import logging
from config import settings

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_google_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def upload_file_to_drive(file_path, file_name):
    service = get_google_drive_service()
    file_metadata = {
        'name': file_name,
        'parents': [settings.GOOGLE_DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    return file.get('id'), file.get('webViewLink')

def delete_file_from_drive(file_id):
    service = get_google_drive_service()
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error deleting file from Google Drive: {str(e)}")
        return False