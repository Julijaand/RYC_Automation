"""
Date Extraction Service - AI-powered date extraction from document content
Uses Vision LLM to extract dates from PDFs and images directly
"""
import re
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional
from PyPDF2 import PdfReader
from langchain_community.llms import Ollama
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def extract_pdf_text(file_path: Path, max_pages: int = 3) -> str:
    """
    Extract text from PDF file
    
    Args:
        file_path: Path to PDF file
        max_pages: Maximum number of pages to read (default: 3)
    
    Returns:
        Extracted text content
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        
        # Read first few pages (dates usually on first page)
        pages_to_read = min(len(reader.pages), max_pages)
        
        for i in range(pages_to_read):
            page = reader.pages[i]
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        logger.warning(f"Failed to extract PDF text from {file_path.name}: {e}")
        return ""


def extract_date_from_image_with_vision(file_path: Path) -> Optional[str]:
    """
    Extract date from image using Vision LLM (direct image analysis)
    
    Args:
        file_path: Path to image file (JPG, PNG)
    
    Returns:
        Date string in YYYY-MM-DD format, or None if not found
    """
    try:
        # Read image as base64
        with open(file_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Initialize Vision LLM
        llm = Ollama(
            model=settings.OLLAMA_MODEL,  # Should be llama3.2-vision
            base_url="http://localhost:11434",
            temperature=0.1
        )
        
        # Build prompt with image
        prompt = f"""Look at this document image and extract the main date.

Instructions:
1. Find the document date (invoice date, payroll period, contract date)
2. Ignore other dates like due dates or company founding dates
3. If you see "December 2024" or "Décembre 2024" → return "2024-12-01"
4. If you see "15/12/2024" or "2024-12-15" → return "2024-12-15"
5. Return ONLY the date in YYYY-MM-DD format
6. If no clear date found, return "NOT_FOUND"

Date:"""
        
        # Call Vision LLM with image
        response = llm.invoke(
            prompt,
            images=[image_data]  # Pass image as base64
        ).strip()
        
        # Validate response
        date_pattern = r'(\d{4})-(\d{2})-(\d{2})'
        match = re.search(date_pattern, response)
        
        if match:
            logger.info(f"✓ Vision LLM extracted date from image: {file_path.name} → {match.group(0)}")
            return match.group(0)
        else:
            logger.debug(f"Vision LLM could not extract date from {file_path.name}: {response}")
            return None
    
    except Exception as e:
        logger.warning(f"Vision LLM failed for {file_path.name}: {e}")
        return None


def extract_date_with_llm(text: str, filename: str) -> Optional[str]:
    """
    Use LLM to extract date from document text
    
    Args:
        text: Document text content
        filename: Original filename (for context)
    
    Returns:
        Date string in YYYY-MM-DD format, or None if not found
    """
    if not text:
        return None
    
    try:
        # Initialize Ollama
        llm = Ollama(
            model=settings.OLLAMA_MODEL,
            base_url="http://localhost:11434",
            temperature=0.1
        )
        
        # Build prompt
        prompt = f"""Extract the main date from this document.

Filename: {filename}

Document content (first 800 characters):
{text[:800]}

Instructions:
1. Look for dates like: invoice date, payment date, payroll period, contract date, billing date
2. Ignore dates like: due date, company founding date
3. If you see "December 2024" or "Dec 2024" or "2024-12" → return "2024-12-01"
4. If you see "15/12/2024" or "2024-12-15" → return "2024-12-15"
5. Return ONLY the date in YYYY-MM-DD format
6. If no clear date found, return "NOT_FOUND"

Date:"""
        
        # Call LLM
        response = llm.invoke(prompt).strip()
        
        # Validate response
        date_pattern = r'(\d{4})-(\d{2})-(\d{2})'
        match = re.search(date_pattern, response)
        
        if match:
            return match.group(0)  # Return YYYY-MM-DD
        else:
            logger.debug(f"LLM could not extract date from {filename}: {response}")
            return None
    
    except Exception as e:
        logger.warning(f"LLM date extraction failed for {filename}: {e}")
        return None


def extract_date_from_document(file_path: Path) -> Optional[str]:
    """
    Extract date from document content using AI (Vision for images, text extraction for PDFs)
    
    Args:
        file_path: Path to document file
    
    Returns:
        Date string in YYYYMMDD format, or None if not found
    """
    filename = file_path.name
    file_ext = file_path.suffix.lower()
    
    # For images: Use Vision LLM directly (no OCR needed!)
    if file_ext in ['.jpg', '.jpeg', '.png']:
        logger.debug(f"Using Vision LLM for image: {filename}")
        date_str = extract_date_from_image_with_vision(file_path)
        
        if date_str:
            # Convert YYYY-MM-DD to YYYYMMDD
            date_yyyymmdd = date_str.replace('-', '')
            return date_yyyymmdd
        return None
    
    # For PDFs: Extract text then use LLM
    elif file_ext == '.pdf':
        logger.debug(f"Extracting text from PDF: {filename}")
        text = extract_pdf_text(file_path)
        
        if not text:
            logger.debug(f"No text extracted from {filename}")
            return None
        
        # Use LLM to extract date from text
        date_str = extract_date_with_llm(text, filename)
        
        if date_str:
            # Convert YYYY-MM-DD to YYYYMMDD
            date_yyyymmdd = date_str.replace('-', '')
            logger.info(f"✓ Extracted date from PDF content: {filename} → {date_str}")
            return date_yyyymmdd
        
        return None
    
    else:
        logger.warning(f"Unsupported file type for date extraction: {file_ext}")
        return None


def extract_date_smart(file_path: Path) -> str:
    """
    Smart date extraction: Try AI first, fallback to filename patterns
    
    Args:
        file_path: Path to document file
    
    Returns:
        Date string in YYYYMMDD format (always returns something)
    """
    filename = file_path.name
    
    # Strategy 1: Extract from document CONTENT using AI
    date_from_content = extract_date_from_document(file_path)
    if date_from_content:
        return date_from_content
    
    # Strategy 2: Extract from FILENAME using regex patterns
    logger.debug(f"Falling back to filename pattern extraction: {filename}")
    
    # Pattern 1: YYYYMMDD (8 consecutive digits)
    pattern1 = r'(20\d{2})(0[1-9]|1[0-2])([0-2]\d|3[01])'
    match = re.search(pattern1, filename)
    if match:
        return match.group(0)
    
    # Pattern 2: YYYY-MM-DD or YYYY_MM_DD
    pattern2 = r'(20\d{2})[-_](0[1-9]|1[0-2])[-_]([0-2]\d|3[01])'
    match = re.search(pattern2, filename)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    
    # Pattern 3: Month names (Dec2024, December2024, Décembre2024)
    month_patterns = {
        r'jan(?:uary|vier)?[\s_-]?(20\d{2})': '01',
        r'f[eé]v(?:rier)?[\s_-]?(20\d{2})': '02',
        r'mar(?:ch|s)?[\s_-]?(20\d{2})': '03',
        r'avr(?:il)?[\s_-]?(20\d{2})': '04',
        r'ma[iy][\s_-]?(20\d{2})': '05',
        r'jun[e]?[\s_-]?(20\d{2})': '06',
        r'jul(?:y|illet)?[\s_-]?(20\d{2})': '07',
        r'ao[uû]t?[\s_-]?(20\d{2})': '08',
        r'sep(?:tember|tembre)?[\s_-]?(20\d{2})': '09',
        r'oct(?:ober|obre)?[\s_-]?(20\d{2})': '10',
        r'nov(?:ember|embre)?[\s_-]?(20\d{2})': '11',
        r'd[eé]c(?:ember|embre)?[\s_-]?(20\d{2})': '12',
    }
    
    filename_lower = filename.lower()
    for pattern, month in month_patterns.items():
        match = re.search(pattern, filename_lower)
        if match:
            year = match.group(1)
            return f"{year}{month}01"
    
    # Pattern 4: Just year (Invoice_2024_001)
    year_pattern = r'_(20\d{2})_'
    match = re.search(year_pattern, filename)
    if match:
        year = match.group(1)
        return f"{year}0101"
    
    # Strategy 3: Last resort - use current date
    logger.warning(f"Could not extract date from {filename}, using current date")
    return datetime.now().strftime("%Y%m%d")
