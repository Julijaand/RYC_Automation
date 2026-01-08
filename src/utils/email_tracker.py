"""
Email tracker to avoid downloading the same emails multiple times
"""
from pathlib import Path
import json
from datetime import datetime
from src.config.settings import settings


class EmailTracker:
    """Track processed email IDs to avoid duplicate downloads"""
    
    def __init__(self, tracker_file: str = None):
        if tracker_file is None:
            tracker_file = Path(settings.LOCAL_DOWNLOAD_PATH).parent / "processed_emails.json"
        self.tracker_file = Path(tracker_file)
        self.processed_emails = self._load()
    
    def _load(self) -> dict:
        """Load processed email IDs from file"""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save(self):
        """Save processed email IDs to file"""
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracker_file, 'w') as f:
            json.dump(self.processed_emails, f, indent=2)
    
    def is_processed(self, email_id: str) -> bool:
        """Check if email has been processed"""
        return email_id in self.processed_emails
    
    def mark_processed(self, email_id: str, subject: str = None):
        """Mark email as processed"""
        self.processed_emails[email_id] = {
            'processed_at': datetime.now().isoformat(),
            'subject': subject
        }
        self._save()
    
    def get_unprocessed(self, email_ids: list) -> list:
        """Filter out already processed emails"""
        return [eid for eid in email_ids if not self.is_processed(eid)]
    
    def clear(self):
        """Clear all tracked emails (use with caution!)"""
        self.processed_emails = {}
        self._save()


# Global tracker instance
_tracker = None

def get_email_tracker() -> EmailTracker:
    """Get global email tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = EmailTracker()
    return _tracker
