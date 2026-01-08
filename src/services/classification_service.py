"""
Classification Service - RAG-based document classification with AI agent fallback
Uses existing RAG engine for intelligent document type detection
Falls back to AI agent for unclear cases
"""
from pathlib import Path
from typing import Dict, List, Optional
from src.rag.query_engine import classify_document_with_rag
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RAGClassificationService:
    """
    Document classification using RAG (Retrieval-Augmented Generation)
    with optional AI agent for edge cases
    
    Primary method: RAG (fast, reliable)
    Fallback method: AI agent (for unclear cases)
    
    Uses vector search + LLM to identify document types based on:
    - Content similarity to known documents
    - Filename patterns
    - Keyword matching as fallback
    - AI agent analysis (only when needed)
    """
    
    def __init__(self):
        """
        Initialize classification service
        
        Uses RAG with similarity thresholds for fast, reliable classification
        """
        self.download_dir = Path(settings.LOCAL_DOWNLOAD_PATH)
    
    def classify(
        self, 
        filename: str,
        email_subject: Optional[str] = None,
        email_body: Optional[str] = None
    ) -> str:
        """
        Classify a single document with optional AI agent fallback
        
        Args:
            filename: Name of file in downloads/ folder
            email_subject: Optional email subject (for agent analysis)
            email_body: Optional email body (for agent analysis)
        
        Returns:
            Document type: 'invoice', 'payroll', 'contract', 'receipt', 'statement', or 'other'
        """
        file_path = self.download_dir / filename
        
        if not file_path.exists():
            logger.warning(f"File not found: {filename}")
            return "other"
        
        try:
            # Use RAG classification with similarity thresholds
            doc_type = classify_document_with_rag(str(file_path), filename)
            logger.debug(f"RAG classified {filename} as: {doc_type}")
            return doc_type
            
        except Exception as e:
            logger.error(f"Classification failed for {filename}: {e}")
            return "other"
    
    def classify_batch(
        self,
        filenames: List[str],
        email_context: Optional[Dict[str, Dict[str, str]]] = None
    ) -> Dict[str, str]:
        """
        Classify multiple documents using RAG
        
        Args:
            filenames: List of filenames to classify
            email_context: Optional dict mapping filename to {subject, body} (unused, for future)
        
        Returns:
            Dictionary mapping filename to document type
        """
        if not filenames:
            logger.info("No files to classify")
            return {}
        
        logger.info(f"Classifying {len(filenames)} documents using RAG...")
        
        results = {}
        for filename in filenames:
            # Get email context if available
            subject = None
            body = None
            if email_context and filename in email_context:
                subject = email_context[filename].get('subject')
                body = email_context[filename].get('body')
            
            results[filename] = self.classify(filename, subject, body)
        
        # Log summary
        type_counts = {}
        for doc_type in results.values():
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        logger.info(f"Classification complete: {dict(type_counts)}")
        return results
