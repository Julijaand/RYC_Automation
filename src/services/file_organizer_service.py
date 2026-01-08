"""
File Organizer Service - Direct file organization without agents
Handles file movement, duplicate detection, and folder structure
"""
import shutil
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from src.config.settings import settings
from src.utils.logger import get_logger
from src.services.date_extraction_service import extract_date_smart

logger = get_logger(__name__)


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA256 hash of file content for duplicate detection
    
    Args:
        file_path: Path to file
    
    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def find_duplicate_by_hash(file_path: Path, target_dir: Path) -> Optional[Path]:
    """
    Search for duplicate file in target directory using hash comparison
    
    Args:
        file_path: Source file to check
        target_dir: Directory to search for duplicates
    
    Returns:
        Path to duplicate file if found, None otherwise
    """
    if not target_dir.exists():
        return None
    
    source_hash = calculate_file_hash(file_path)
    
    # Search all files in target directory and subdirectories
    for existing_file in target_dir.rglob("*"):
        if existing_file.is_file():
            try:
                if calculate_file_hash(existing_file) == source_hash:
                    return existing_file
            except Exception as e:
                logger.warning(f"Could not hash file {existing_file}: {e}")
                continue
    
    return None


def extract_customer_from_filename(filename: str) -> str:
    """
    Extract customer name from filename
    
    Patterns:
    - CustomerName_DocumentType_Date.pdf
    - Separated by underscores or spaces
    
    Args:
        filename: Name of the file
    
    Returns:
        Customer name or 'Unknown' if not found
    """
    # Remove extension
    name_without_ext = Path(filename).stem
    
    parts = re.split(r'[_\-\s]+', name_without_ext)
    
    # Skip common document type keywords
    skip_keywords = [
        'invoice', 'facture', 'payroll', 'paie', 'fiche', 'contract', 
        'contrat', 'receipt', 'recu', 'statement', 'releve', 'bill',
        'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
        'sep', 'oct', 'nov', 'december', 'january', 'february', '2024', '2025'
    ]
    
    # Find first part that's not a keyword and not just numbers
    for part in parts:
        part_lower = part.lower()
        if (part and 
            len(part) > 2 and 
            not part.isdigit() and 
            part_lower not in skip_keywords and
            not re.match(r'^\d+$', part)):
            return part
    
    # Fallback: use first part or 'Unknown'
    return parts[0] if parts and len(parts[0]) > 0 else 'Unknown'


class FileOrganizerService:
    """
    File organization service with duplicate detection
    
    Organizes files into structured folders on M: drive:
    Customer/DocType/YYYY-MM/doctype_YYYYMMDD_originalname.ext
    """
    
    def __init__(self):
        self.download_dir = Path(settings.LOCAL_DOWNLOAD_PATH)
        self.m_drive = Path(settings.M_DRIVE_PATH)
        self.m_drive.mkdir(parents=True, exist_ok=True)
    
    def organize_single(
        self,
        filename: str,
        doc_type: str,
        customer_name: Optional[str] = None
    ) -> str:
        """
        Organize a single file
        
        Args:
            filename: Name of file in downloads/ folder
            doc_type: Document type (invoice, payroll, contract, etc.)
            customer_name: Optional customer name (extracted if not provided)
        
        Returns:
            Status: 'success', 'duplicate', or 'error'
        """
        try:
            source_path = self.download_dir / filename
            
            if not source_path.exists():
                logger.error(f"File not found: {filename}")
                return 'error'
            
            # Validate document type
            valid_types = ['invoice', 'payroll', 'contract', 'receipt', 'statement', 'other']
            if doc_type not in valid_types:
                doc_type = 'other'
            
            # Extract or use provided customer name
            if not customer_name:
                customer_name = extract_customer_from_filename(filename)
            
            # Clean customer name for folder
            customer_clean = re.sub(r'[^a-zA-Z0-9_\-]', '', customer_name)
            if not customer_clean:
                customer_clean = 'Unknown'
            
            # Extract date from document content using AI (then fallback to filename)
            date_str = extract_date_smart(source_path)
            year = date_str[:4]
            month = date_str[4:6]
            year_month = f"{year}-{month}"
            
            # Build destination path: doc_type/year-month/
            doc_type_clean = doc_type.lower().replace(' ', '_')
            dest_dir = self.m_drive / doc_type_clean / year_month
            
            # Check for duplicates using hash
            duplicate = find_duplicate_by_hash(source_path, self.m_drive)
            
            if duplicate:
                logger.info(f"Duplicate: {filename} already exists as {duplicate}")
                source_path.unlink()  # Delete source
                return 'duplicate'
            
            # Create destination directory
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Keep original filename (no date prefix)
            dest_path = dest_dir / filename
            
            # Handle filename collision (edge case)
            if dest_path.exists():
                original_name = source_path.stem
                extension = source_path.suffix
                counter = 1
                while dest_path.exists():
                    new_filename = f"{original_name}_{counter}{extension}"
                    dest_path = dest_dir / new_filename
                    counter += 1
            
            # Move file
            shutil.move(str(source_path), str(dest_path))
            
            logger.info(f"Organized: {filename} → {dest_path}")
            return 'success'
            
        except Exception as e:
            logger.error(f"Error organizing {filename}: {e}")
            return 'error'
    
    def organize_batch(
        self,
        classified_files: Dict[str, str]
    ) -> Dict[str, int]:
        """
        Organize multiple files
        
        Args:
            classified_files: Dictionary mapping file_path to document type
        
        Returns:
            Statistics: {
                success: X, 
                duplicates: Y, 
                errors: Z,
                organized_files: [list of paths],
                duplicate_files: [list of paths],
                error_list: [list of error dicts]
            }
        """
        if not classified_files:
            logger.info("No files to organize")
            return {
                "success": 0, 
                "duplicates": 0, 
                "errors": 0,
                "organized_files": [],
                "duplicate_files": [],
                "error_list": []
            }
        
        logger.info(f"Organizing {len(classified_files)} files...")
        
        stats = {
            "success": 0, 
            "duplicates": 0, 
            "errors": 0,
            "organized_files": [],
            "duplicate_files": [],
            "error_list": []
        }
        
        for file_path, doc_type in classified_files.items():
            # Extract filename from path
            filename = Path(file_path).name
            
            # Organize
            result = self.organize_single(filename, doc_type)
            
            # Track results
            if result == 'success':
                stats['success'] += 1
                stats['organized_files'].append(file_path)
            elif result == 'duplicate':
                stats['duplicates'] += 1
                stats['duplicate_files'].append(file_path)
            else:  # error
                stats['errors'] += 1
                stats['error_list'].append({
                    'file_path': file_path,
                    'message': f'Failed to organize {filename}'
                })
        
        logger.info(f"Organization complete: success={stats['success']}, duplicates={stats['duplicates']}, errors={stats['errors']}")
        return stats
