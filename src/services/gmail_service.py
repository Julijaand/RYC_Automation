"""
Gmail Service - Direct Gmail API access without agents
Simple, reliable email retrieval and attachment download
"""
import base64
from pathlib import Path
from typing import List, Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.email_tracker import get_email_tracker

logger = get_logger(__name__)

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_gmail_service():
    """
    Authenticate and return Gmail API service
    
    Returns:
        Gmail API service instance
    """
    creds = None
    token_path = settings.GMAIL_TOKEN_PATH
    creds_path = settings.GMAIL_CREDENTIALS_PATH
    
    # Load existing token
    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


class GmailDownloadService:
    """
    Direct Gmail API service - no agents, just clean functions
    
    Downloads email attachments with duplicate prevention via email tracking
    """
    
    def __init__(self):
        self.service = get_gmail_service()
        self.tracker = get_email_tracker()
        self.download_dir = Path(settings.LOCAL_DOWNLOAD_PATH)
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_new_attachments(
        self,
        query: str = "has:attachment (invoice OR payroll OR contract OR notification OR facture OR paie OR contrat)",
        max_results: int = 100
    ) -> List[str]:
        """
        Search Gmail and download NEW attachments only
        
        Args:
            query: Gmail search query
            max_results: Maximum number of emails to process
        
        Returns:
            List of downloaded filenames (not full paths, just names)
        """
        logger.info(f"Searching Gmail with query: {query}")
        
        # Search for messages
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
        except Exception as e:
            logger.error(f"Failed to search Gmail: {e}")
            return []
        
        messages = results.get('messages', [])
        
        if not messages:
            logger.info("No messages found")
            return []
        
        # Filter out already processed emails
        message_ids = [msg['id'] for msg in messages]
        unprocessed_ids = self.tracker.get_unprocessed(message_ids)
        
        if not unprocessed_ids:
            logger.info(f"Found {len(messages)} messages, but all already processed")
            return []
        
        skipped_count = len(messages) - len(unprocessed_ids)
        logger.info(f"Found {len(messages)} messages: {len(unprocessed_ids)} new, {skipped_count} already processed")
        
        # Download attachments from unprocessed messages
        all_filenames = []
        
        for message_id in unprocessed_ids:
            filenames = self._download_message_attachments(message_id)
            all_filenames.extend(filenames)
        
        logger.info(f"Downloaded {len(all_filenames)} files total")
        return all_filenames
    
    def _download_message_attachments(self, message_id: str) -> List[str]:
        """
        Download all attachments from a single message
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            List of downloaded filenames
        """
        try:
            # Get full message
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract subject for logging
            headers_list = message.get('payload', {}).get('headers', [])
            headers = {h['name']: h['value'] for h in headers_list} if isinstance(headers_list, list) else {}
            subject = headers.get('Subject', 'No subject')
            
            # Recursively find and download attachments
            payload = message.get('payload', {})
            parts = payload.get('parts', []) if isinstance(payload, dict) else []
            filenames = self._process_parts(parts, message_id)
            
            # Mark as processed if we downloaded files
            if filenames:
                self.tracker.mark_processed(message_id, subject)
                logger.info(f"Downloaded {len(filenames)} files from: {subject}")
            
            return filenames
            
        except Exception as e:
            logger.error(f"Failed to download from message {message_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _process_parts(self, parts: List[Dict], message_id: str) -> List[str]:
        """
        Recursively process message parts to find and download attachments
        
        Args:
            parts: Message parts from Gmail API
            message_id: Gmail message ID
        
        Returns:
            List of downloaded filenames
        """
        filenames = []
        
        if not parts:
            return filenames
        
        for part in parts:
            filename = part.get('filename', '')
            
            # Check if this part is an attachment
            if filename:
                attachment_id = part.get('body', {}).get('attachmentId')
                if attachment_id:
                    # Download attachment
                    try:
                        attachment = self.service.users().messages().attachments().get(
                            userId='me',
                            messageId=message_id,
                            id=attachment_id
                        ).execute()
                        
                        # Decode and save
                        file_data = base64.urlsafe_b64decode(attachment['data'])
                        file_path = self.download_dir / filename
                        
                        # Write file
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
                        
                        filenames.append(filename)
                        logger.debug(f"Saved: {filename}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to download attachment {filename}: {e}")
            
            # Recursively check nested parts
            if 'parts' in part:
                filenames.extend(self._process_parts(part['parts'], message_id))
        
        return filenames
