#!/usr/bin/env python3
"""
Fast Ollama Data Extraction Script

Extracts structured data from organized documents in test_drive/
Uses direct Ollama LLM calls (5-10 seconds per file)

Usage:
    python scripts/extract_data.py                    # Extract from all files
    python scripts/extract_data.py --sample 3         # Test with 3 files
    python scripts/extract_data.py --type invoice     # Extract invoices only
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.data_extraction_service import DataExtractionService
from src.utils.logger import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


def extract_all(test_drive_path: Path, doc_type: str = None, sample: int = None):
    """
    Extract data from all organized documents
    
    Args:
        test_drive_path: Path to test_drive folder
        doc_type: Extract only this document type (invoice, payroll, contract)
        sample: Limit extraction to N files for testing
    """
    extractor = DataExtractionService()
    
    # Find files to extract from
    doc_types = [doc_type] if doc_type else ['invoice', 'payroll', 'contract']
    
    all_files = {}
    for dtype in doc_types:
        folder = test_drive_path / dtype
        if folder.exists():
            # Get all PDFs, JPGs, and PNGs
            files = []
            files.extend(list(folder.rglob("*.pdf")))
            files.extend(list(folder.rglob("*.jpg")))
            files.extend(list(folder.rglob("*.png")))
            all_files[dtype] = files[:sample] if sample else files
    
    total_files = sum(len(files) for files in all_files.values())
    
    logger.info("="*60)
    logger.info("FAST OLLAMA DATA EXTRACTION")
    logger.info("="*60)
    logger.info(f"Source: {test_drive_path}")
    logger.info(f"Files to process: {total_files}")
    for dtype, files in all_files.items():
        if files:
            logger.info(f"  - {dtype}: {len(files)} files")
    logger.info("")
    
    if total_files == 0:
        logger.warning("No files found to extract from")
        return
    
    # Estimate time (8 seconds per file - fast Ollama)
    estimated_seconds = total_files * 8
    if estimated_seconds < 60:
        logger.info(f"⏱️  Estimated time: {estimated_seconds} seconds")
    else:
        estimated_minutes = estimated_seconds / 60
        logger.info(f"⏱️  Estimated time: {estimated_minutes:.1f} minutes")
    logger.info("")
    
    # Extract from each file
    success_count = 0
    error_count = 0
    
    for dtype, files in all_files.items():
        for i, file_path in enumerate(files, 1):
            logger.info("-"*60)
            logger.info(f"[{success_count + error_count + 1}/{total_files}] Processing: {file_path.name}")
            logger.info("-"*60)
            
            try:
                data = extractor.extract_from_file(file_path, dtype)
                
                # Check if extraction succeeded
                if 'error' not in data:
                    success_count += 1
                    # Show key extracted fields
                    if dtype == 'invoice':
                        logger.info(f"  ✓ Customer: {data.get('customer_name')}")
                        logger.info(f"  ✓ Amount: {data.get('currency')} {data.get('total_amount')}")
                    elif dtype == 'payroll':
                        logger.info(f"  ✓ Employee: {data.get('employee_name')}")
                        logger.info(f"  ✓ Net Pay: {data.get('currency')} {data.get('net_pay')}")
                    elif dtype == 'contract':
                        logger.info(f"  ✓ Type: {data.get('contract_type')}")
                        logger.info(f"  ✓ Parties: {data.get('parties')}")
                else:
                    error_count += 1
                    logger.error(f"  ❌ Error: {data.get('error')}")
                
            except Exception as e:
                error_count += 1
                logger.error(f"  ❌ Failed: {e}")
            
            logger.info("")
    
    logger.info("="*60)
    logger.info("EXTRACTION COMPLETE")
    logger.info("="*60)
    logger.info(f"✓ Successfully extracted: {success_count} files")
    if error_count > 0:
        logger.info(f"❌ Errors: {error_count} files")
    logger.info(f"💾 Data saved to: extracted_data.json")
    logger.info("")
    
    # Show summary from JSON
    import json
    try:
        with open("extracted_data.json") as f:
            data = json.load(f)
        
        logger.info("📊 Summary:")
        logger.info(f"  Total Invoices: {len(data.get('invoices', []))}")
        logger.info(f"  Total Payroll: {len(data.get('payroll', []))}")
        logger.info(f"  Total Contracts: {len(data.get('contracts', []))}")
        
        # Calculate totals
        if data.get('invoices'):
            total_invoiced = sum(inv.get('total_amount', 0) for inv in data['invoices'])
            logger.info(f"  Total Invoiced: €{total_invoiced:,.2f}")
        
        if data.get('payroll'):
            total_payroll = sum(p.get('net_pay', 0) for p in data['payroll'])
            logger.info(f"  Total Net Payroll: €{total_payroll:,.2f}")
            
    except Exception as e:
        logger.error(f"Could not load summary: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Extract structured data from organized documents using CrewAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/extract_data.py                    # Extract from all files
  python scripts/extract_data.py --sample 5         # Test with 5 files
  python scripts/extract_data.py --type invoice     # Extract invoices only
  python scripts/extract_data.py --type payroll --sample 2  # Test with 2 payroll files

Performance:
  - Average: 50 seconds per file
  - 10 files ≈ 8-10 minutes
  - Recommended: Run monthly or on-demand
        """
    )
    
    parser.add_argument(
        '--type',
        type=str,
        choices=['invoice', 'payroll', 'contract'],
        help='Extract only this document type'
    )
    
    parser.add_argument(
        '--sample',
        type=int,
        metavar='N',
        help='Extract from N files only (for testing)'
    )
    
    args = parser.parse_args()
    
    # Get test_drive path from settings
    test_drive = settings.M_DRIVE_PATH
    
    if not test_drive.exists():
        logger.error(f"Test drive not found: {test_drive}")
        logger.error("Make sure documents are organized first: python -m src.main")
        sys.exit(1)
    
    extract_all(test_drive, doc_type=args.type, sample=args.sample)


if __name__ == "__main__":
    main()
