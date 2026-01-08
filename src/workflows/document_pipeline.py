"""
Document Processing Pipeline - RAG Classification

Main workflow:
1. Download files from Gmail
2. Classify each file using RAG (vector similarity)
3. Organize files on M: drive by type and date

For data extraction, use: python scripts/extract_data.py
"""
from typing import Dict, Optional
import traceback
from pathlib import Path

from src.services.gmail_service import GmailDownloadService
from src.services.classification_service import RAGClassificationService
from src.services.file_organizer_service import FileOrganizerService
from src.database.tracking_db import get_tracking_db
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentPipeline:
    """
    RAG-based document processing pipeline
    
    Classification: Fast RAG with vector similarity matching
    Organization: Automatic folder structure by type and date
    
    Features:
    - Fast: 1-2 seconds per file
    - Accurate: Trained on invoice, payroll, contract examples
    - Simple: No complex agent logic
    """
    
    def __init__(self):
        """Initialize pipeline with RAG-based classification"""
        self.gmail_service = GmailDownloadService()
        self.classifier = RAGClassificationService()
        self.organizer = FileOrganizerService()
        self.tracking_db = get_tracking_db()
    
    def run(
        self,
        query: str = "has:attachment (invoice OR payroll OR contract OR notification OR facture OR paie OR contrat)",
        max_results: int = 100
    ) -> Dict:
        """
        Execute complete document processing pipeline
        
        Args:
            query: Gmail search query
            max_results: Maximum number of emails to process
        
        Returns:
            Statistics and results dictionary
        """
        logger.info("="*60)
        logger.info("RAG CLASSIFICATION PIPELINE STARTING")
        logger.info("="*60)
        
        # Start tracking run
        run_id = self.tracking_db.start_run()
        
        try:
            # Step 1: Download from Gmail
            logger.info("Step 1/3: Downloading attachments from Gmail...")
            downloaded_files = self.gmail_service.fetch_new_attachments(
                query=query,
                max_results=max_results
            )
            
            if not downloaded_files:
                logger.info("No new files to process")
                stats = {
                    "status": "success",
                    "message": "No new files found",
                    "downloaded": 0,
                    "classified": 0,
                    "organized": 0,
                    "duplicates": 0,
                    "errors": 0
                }
                self.tracking_db.end_run(run_id, "success", stats)
                return stats
            
            logger.info(f"✓ Downloaded {len(downloaded_files)} files")
            
            # Track downloaded files
            for file_path in downloaded_files:
                file_size = Path(file_path).stat().st_size if Path(file_path).exists() else None
                self.tracking_db.add_file_record(
                    run_id=run_id,
                    filename=Path(file_path).name,
                    status='downloaded',
                    file_path=str(file_path),
                    file_size=file_size
                )
            
            # Step 2: Classify documents
            logger.info(f"Step 2/3: Classifying {len(downloaded_files)} documents...")
            classified_files = self.classifier.classify_batch(downloaded_files)
            logger.info(f"✓ Classified {len(classified_files)} files")
            
            # Log classification breakdown
            type_counts = {}
            for file_path, doc_type in classified_files.items():
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
                # Update file record with classification
                self.tracking_db.add_file_record(
                    run_id=run_id,
                    filename=Path(file_path).name,
                    status='classified',
                    document_type=doc_type,
                    file_path=str(file_path)
                )
            
            logger.info(f"  Breakdown: {dict(type_counts)}")
            
            # Step 3: Organize files
            logger.info(f"Step 3/3: Organizing {len(classified_files)} files...")
            org_stats = self.organizer.organize_batch(classified_files)
            logger.info(f"✓ Organization complete")
            logger.info(f"  Organized: {org_stats.get('success', 0)}")
            logger.info(f"  Duplicates skipped: {org_stats.get('duplicates', 0)}")
            logger.info(f"  Errors: {org_stats.get('errors', 0)}")
            
            # Track organized files
            for file_path, doc_type in classified_files.items():
                if file_path in org_stats.get('organized_files', []):
                    self.tracking_db.add_file_record(
                        run_id=run_id,
                        filename=Path(file_path).name,
                        status='organized',
                        document_type=doc_type,
                        file_path=str(file_path)
                    )
                elif file_path in org_stats.get('duplicate_files', []):
                    self.tracking_db.add_file_record(
                        run_id=run_id,
                        filename=Path(file_path).name,
                        status='duplicate',
                        document_type=doc_type,
                        file_path=str(file_path)
                    )
            
            # Track any errors
            for error in org_stats.get('error_list', []):
                self.tracking_db.add_error(
                    run_id=run_id,
                    error_type='organization',
                    error_message=error.get('message', ''),
                    file_path=error.get('file_path', '')
                )
            
            # Compile results
            result = {
                "status": "success",
                "message": "Pipeline completed successfully",
                "downloaded": len(downloaded_files),
                "classified": len(classified_files),
                "organized": org_stats.get('success', 0),
                "duplicates": org_stats.get('duplicates', 0),
                "errors": org_stats.get('errors', 0),
                "classification_breakdown": type_counts
            }
            
            # End tracking run
            self.tracking_db.end_run(run_id, "success", result)
            
            logger.info("="*60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*60)
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            logger.error(f"Pipeline failed: {error_msg}", exc_info=True)
            
            # Track error
            self.tracking_db.add_error(
                run_id=run_id,
                error_type='system',
                error_message=error_msg,
                stack_trace=error_trace
            )
            
            result = {
                "status": "error",
                "message": error_msg,
                "downloaded": 0,
                "classified": 0,
                "organized": 0,
                "duplicates": 0,
                "errors": 1
            }
            
            # End tracking run with error
            self.tracking_db.end_run(run_id, "error", result, error_msg)
            
            return result


def run_pipeline(
    query: Optional[str] = None,
    max_results: int = 100
) -> Dict:
    """
    Convenience function to run the RAG classification pipeline
    
    Args:
        query: Optional Gmail search query (uses default if not provided)
        max_results: Maximum number of emails to process
    
    Returns:
        Pipeline results dictionary
    """
    pipeline = DocumentPipeline()
    
    if query:
        return pipeline.run(query=query, max_results=max_results)
    else:
        return pipeline.run(max_results=max_results)


def main():
    """
    Main entry point for hybrid pipeline execution
    """
    from src.config.settings import settings
    
    logger.info("RYC Document Automation - Hybrid Pipeline")
    logger.info(f"M: Drive: {settings.M_DRIVE_PATH}")
    logger.info(f"Downloads: {settings.LOCAL_DOWNLOAD_PATH}")
    logger.info(f"Model: {settings.OLLAMA_MODEL}")
    
    result = run_pipeline()
    
    print("\n" + "="*60)
    print("PIPELINE RESULTS")
    print("="*60)
    print(f"Status: {result['status']}")
    print(f"Files downloaded: {result['downloaded']}")
    print(f"Files classified: {result['classified']}")
    print(f"Files organized: {result['organized']}")
    print(f"Duplicates skipped: {result['duplicates']}")
    print(f"Errors: {result['errors']}")
    
    if result.get('classification_breakdown'):
        print("\nClassification Breakdown:")
        for doc_type, count in result['classification_breakdown'].items():
            print(f"  {doc_type}: {count}")
    
    print("="*60)
    
    return result


if __name__ == "__main__":
    main()
