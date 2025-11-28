import io
import json
import os
from typing import Optional, Tuple

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
]

# Use a default folder ID from environment if caller doesn't supply one
DEFAULT_FOLDER_ENV = "GOOGLE_DRIVE_FOLDER_ID"


def _get_service():
    """
    Build a Google Drive service using a Service Account.
    Environment variables:
      - GOOGLE_SERVICE_ACCOUNT_JSON: path to the service account JSON file (prefer this)
      - or inline JSON content (fallback)
    """
    sa_file_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    
    # Try to load from file path first
    if sa_file_path and os.path.exists(sa_file_path):
        print(f"📁 Loading Google credentials from file: {sa_file_path}")
        with open(sa_file_path, 'r') as f:
            sa_json_str = f.read()
        creds = Credentials.from_service_account_info(json.loads(sa_json_str), scopes=SCOPES)
    # Try to load from inline JSON string
    elif sa_file_path:
        try:
            print(f"📄 Loading Google credentials from inline JSON")
            creds = Credentials.from_service_account_info(json.loads(sa_file_path), scopes=SCOPES)
        except (json.JSONDecodeError, TypeError):
            raise RuntimeError(
                f"Invalid GOOGLE_SERVICE_ACCOUNT_JSON value. Could not parse as JSON or find file at: {sa_file_path}"
            )
    else:
        raise RuntimeError(
            "Missing Google Service Account credentials. Set GOOGLE_SERVICE_ACCOUNT_JSON to either a file path or JSON string."
        )

    print(f"✅ Google Drive service initialized successfully")
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _resolve_folder_id(folder_id: Optional[str]) -> Optional[str]:
    """Prefer explicit folder_id; otherwise use env GOOGLE_DRIVE_FOLDER_ID if set."""
    return folder_id or os.getenv(DEFAULT_FOLDER_ENV) or None


def upload_file_to_drive(
    file_stream: io.BytesIO,
    filename: str,
    mime_type: str,
    folder_id: Optional[str] = None,
) -> Tuple[str, str, str]:
    """
    Upload a file to Google Drive using a Service Account and set it public.

    Returns: (file_id, web_view_link, public_download_url)
    """
    service = _get_service()

    resolved_folder_id = _resolve_folder_id(folder_id)

    file_metadata = {"name": filename}
    if resolved_folder_id:
        file_metadata["parents"] = [resolved_folder_id]

    media = MediaIoBaseUpload(file_stream, mimetype=mime_type, resumable=True)

    created = (
        service.files()  # type: ignore
        .create(body=file_metadata, media_body=media, fields="id, name, webViewLink, webContentLink")
        .execute()
    )

    file_id = created.get("id")

    # Make the file public (anyone with link can view)
    service.permissions().create(  # type: ignore
        fileId=file_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()

    # Build a stable, embeddable URL
    web_view_link = created.get("webViewLink")
    public_download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
    return file_id, web_view_link, public_download_url
