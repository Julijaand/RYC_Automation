"""
Main Entry Point - RYC Document Automation System

RAG CLASSIFICATION PIPELINE:
- Fast RAG-based document classification (1-2 seconds per file)
- Automatic organization by document type and date
- Daily email processing workflow

For data extraction, use: python scripts/extract_data.py

Usage:
    python -m src.main                    # Run RAG classification pipeline
"""
import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


def run_rag_pipeline():
    """
    Run the RAG classification pipeline
    
    Fast RAG-only classification and organization
    """
    from src.workflows.document_pipeline import run_pipeline
    
    logger.info("="*60)
    logger.info("RYC DOCUMENT AUTOMATION - RAG PIPELINE")
    logger.info("="*60)
    logger.info(f"M: Drive Path: {settings.M_DRIVE_PATH}")
    logger.info(f"Downloads Path: {settings.LOCAL_DOWNLOAD_PATH}")
    logger.info(f"Ollama Model: {settings.OLLAMA_MODEL}")
    logger.info("="*60)
    
    result = run_pipeline()
    
    logger.info("="*60)
    logger.info("WORKFLOW COMPLETED")
    logger.info("="*60)
    
    return result


def main():
    """Main entry point for RAG classification pipeline"""
    parser = argparse.ArgumentParser(
        description="RYC Document Automation - RAG Classification Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main                    # Fast RAG classification and organization

RAG Classification Pipeline:
  ✓ Fast: 1-2 seconds per file
  ✓ Accurate: Uses vector similarity matching
  ✓ Recognizes: invoice, payroll, contract, other
  
  Example: 10 files = 20 seconds total

For Data Extraction:
  Use separate script: python scripts/extract_data.py
  - Extracts structured data (customer, amounts, dates)
  - Saves to extracted_data.json
  - Run monthly or on-demand
        """
    )
    
    args = parser.parse_args()
    
    return run_rag_pipeline()


if __name__ == "__main__":
    main()
