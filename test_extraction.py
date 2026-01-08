"""
Test script to run CrewAI data extraction on existing organized files
"""
from pathlib import Path
from src.services.data_extraction_service import DataExtractionService
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    """Test data extraction on existing files in test_drive"""
    
    test_drive = Path("test_drive")
    extractor = DataExtractionService()
    
    # Find test files to extract from
    test_files = {
        "invoice": list((test_drive / "invoice").rglob("*.pdf"))[:2],  # First 2 invoices
        "payroll": list((test_drive / "payroll").rglob("*.jpg"))[:1] + \
                   list((test_drive / "payroll").rglob("*.png"))[:1],  # 2 payroll
        "contract": list((test_drive / "contract").rglob("*.pdf"))[:1]  # 1 contract
    }
    
    logger.info("="*60)
    logger.info("TESTING CREWAI DATA EXTRACTION")
    logger.info("="*60)
    
    total = sum(len(files) for files in test_files.values())
    logger.info(f"Testing on {total} files:")
    for doc_type, files in test_files.items():
        logger.info(f"  - {doc_type}: {len(files)} files")
    
    logger.info("")
    
    # Extract from each file
    for doc_type, files in test_files.items():
        for file_path in files:
            logger.info("-"*60)
            logger.info(f"Processing: {file_path.name}")
            logger.info("-"*60)
            
            try:
                data = extractor.extract_from_file(file_path, doc_type)
                
                # Show extracted data
                logger.info(f"✓ Extracted data:")
                for key, value in data.items():
                    if key not in ['file_path', 'file_name', 'extracted_at', 'raw_output']:
                        logger.info(f"    {key}: {value}")
                
            except Exception as e:
                logger.error(f"❌ Failed: {e}")
            
            logger.info("")
    
    logger.info("="*60)
    logger.info("EXTRACTION COMPLETE")
    logger.info("="*60)
    logger.info(f"📊 Results saved to: extracted_data.json")
    logger.info("")
    
    # Show summary
    import json
    with open("extracted_data.json") as f:
        data = json.load(f)
    
    logger.info("Summary:")
    logger.info(f"  Invoices: {len(data.get('invoices', []))}")
    logger.info(f"  Payroll: {len(data.get('payroll', []))}")
    logger.info(f"  Contracts: {len(data.get('contracts', []))}")


if __name__ == "__main__":
    main()
