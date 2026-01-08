"""
Gmail API setup helper script
Run this script to authenticate with Gmail API and generate token.json
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.gmail_service import get_gmail_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Test Gmail API authentication"""
    
    print("="*60)
    print("Gmail API Setup")
    print("="*60)
    print()
    print("Prerequisites:")
    print("1. credentials.json file must be in the project root")
    print("2. Gmail API must be enabled in Google Cloud Console")
    print()
    print("This script will:")
    print("- Open a browser for authentication")
    print("- Generate token.json for future use")
    print()
    input("Press Enter to continue...")
    
    try:
        service = get_gmail_service()
        
        # Test with a simple query
        results = service.users().messages().list(
            userId='me',
            maxResults=1
        ).execute()
        
        print()
        print("✅ SUCCESS! Gmail API is working")
        print(f"✅ token.json has been created")
        print()
        print("You can now run the main automation:")
        print("  python -m src.main")
        
    except FileNotFoundError as e:
        print()
        print("❌ ERROR: credentials.json not found")
        print()
        print("Please follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json")
        print("6. Place credentials.json in project root")
        sys.exit(1)
        
    except Exception as e:
        print()
        print(f"❌ ERROR: {e}")
        print()
        print("Please check:")
        print("- Gmail API is enabled in Google Cloud Console")
        print("- credentials.json is valid")
        print("- You have internet connection")
        sys.exit(1)


if __name__ == "__main__":
    main()
