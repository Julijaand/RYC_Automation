"""
Tracking Database - SQLite database for monitoring document processing

Schema:
- processing_runs: Overall pipeline execution records
- file_records: Individual file processing details
- errors: Error tracking and categorization
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from contextlib import contextmanager

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TrackingDatabase:
    """SQLite database for tracking document processing"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize tracking database
        
        Args:
            db_path: Path to SQLite database file (default: logs/tracking.db)
        """
        if db_path is None:
            db_path = Path(settings.LOG_FILE).parent / "tracking.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Processing runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT NOT NULL,  -- running, success, error
                    total_files INTEGER DEFAULT 0,
                    downloaded_files INTEGER DEFAULT 0,
                    classified_files INTEGER DEFAULT 0,
                    organized_files INTEGER DEFAULT 0,
                    duplicate_files INTEGER DEFAULT 0,
                    error_files INTEGER DEFAULT 0,
                    error_message TEXT,
                    metadata TEXT  -- JSON string for additional data
                )
            """)
            
            # File records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    filename TEXT NOT NULL,
                    file_path TEXT,
                    document_type TEXT,  -- invoice, payroll, contract, other
                    status TEXT NOT NULL,  -- downloaded, classified, organized, duplicate, error
                    error_message TEXT,
                    file_size INTEGER,  -- bytes
                    email_id TEXT,  -- Gmail message ID
                    classification_confidence REAL,  -- 0.0 to 1.0
                    metadata TEXT,  -- JSON string for additional data
                    FOREIGN KEY (run_id) REFERENCES processing_runs(id)
                )
            """)
            
            # Errors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    timestamp TIMESTAMP NOT NULL,
                    error_type TEXT NOT NULL,  -- gmail, classification, organization, system
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    file_path TEXT,
                    metadata TEXT,  -- JSON string for additional data
                    FOREIGN KEY (run_id) REFERENCES processing_runs(id)
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_start_time 
                ON processing_runs(start_time)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_run_id 
                ON file_records(run_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_timestamp 
                ON file_records(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_document_type 
                ON file_records(document_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_errors_run_id 
                ON errors(run_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_errors_timestamp 
                ON errors(timestamp)
            """)
            
            conn.commit()
            logger.debug(f"Tracking database initialized at: {self.db_path}")
    
    # ========== Processing Runs ==========
    
    def start_run(self) -> int:
        """
        Start a new processing run
        
        Returns:
            Run ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processing_runs (start_time, status)
                VALUES (?, 'running')
            """, (datetime.now(),))
            run_id = cursor.lastrowid
            logger.debug(f"Started processing run: {run_id}")
            return run_id
    
    def end_run(
        self, 
        run_id: int, 
        status: str,
        stats: Dict[str, Any],
        error_message: Optional[str] = None
    ):
        """
        End a processing run with statistics
        
        Args:
            run_id: Run ID
            status: Final status (success, error)
            stats: Statistics dictionary with counts
            error_message: Error message if status is error
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE processing_runs
                SET end_time = ?,
                    status = ?,
                    total_files = ?,
                    downloaded_files = ?,
                    classified_files = ?,
                    organized_files = ?,
                    duplicate_files = ?,
                    error_files = ?,
                    error_message = ?
                WHERE id = ?
            """, (
                datetime.now(),
                status,
                stats.get('total', 0),
                stats.get('downloaded', 0),
                stats.get('classified', 0),
                stats.get('organized', 0),
                stats.get('duplicates', 0),
                stats.get('errors', 0),
                error_message,
                run_id
            ))
            logger.debug(f"Ended processing run: {run_id} (status: {status})")
    
    def get_recent_runs(self, limit: int = 10) -> List[Dict]:
        """Get recent processing runs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM processing_runs
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_run_by_id(self, run_id: int) -> Optional[Dict]:
        """Get processing run by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM processing_runs WHERE id = ?
            """, (run_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ========== File Records ==========
    
    def add_file_record(
        self,
        run_id: int,
        filename: str,
        status: str,
        document_type: Optional[str] = None,
        file_path: Optional[str] = None,
        error_message: Optional[str] = None,
        file_size: Optional[int] = None,
        email_id: Optional[str] = None,
        confidence: Optional[float] = None
    ):
        """
        Add a file processing record
        
        Args:
            run_id: Processing run ID
            filename: File name
            status: Processing status (downloaded, classified, organized, duplicate, error)
            document_type: Classified document type
            file_path: Final file path
            error_message: Error message if status is error
            file_size: File size in bytes
            email_id: Gmail message ID
            confidence: Classification confidence (0.0 to 1.0)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO file_records (
                    run_id, timestamp, filename, file_path, document_type,
                    status, error_message, file_size, email_id, classification_confidence
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                datetime.now(),
                filename,
                file_path,
                document_type,
                status,
                error_message,
                file_size,
                email_id,
                confidence
            ))
            logger.debug(f"Added file record: {filename} (status: {status})")
    
    def get_files_by_run(self, run_id: int) -> List[Dict]:
        """Get all file records for a processing run"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM file_records
                WHERE run_id = ?
                ORDER BY timestamp
            """, (run_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_files(self, limit: int = 50) -> List[Dict]:
        """Get recent file records"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM file_records
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== Errors ==========
    
    def add_error(
        self,
        error_type: str,
        error_message: str,
        run_id: Optional[int] = None,
        stack_trace: Optional[str] = None,
        file_path: Optional[str] = None
    ):
        """
        Log an error
        
        Args:
            error_type: Error type (gmail, classification, organization, system)
            error_message: Error message
            run_id: Associated processing run ID (optional)
            stack_trace: Full stack trace (optional)
            file_path: Associated file path (optional)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO errors (
                    run_id, timestamp, error_type, error_message, stack_trace, file_path
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                datetime.now(),
                error_type,
                error_message,
                stack_trace,
                file_path
            ))
            logger.debug(f"Logged error: {error_type} - {error_message}")
    
    def get_recent_errors(self, limit: int = 20) -> List[Dict]:
        """Get recent errors"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM errors
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== Statistics ==========
    
    def get_stats_today(self) -> Dict:
        """Get statistics for today"""
        return self._get_stats_for_period("date('now')")
    
    def get_stats_this_week(self) -> Dict:
        """Get statistics for this week"""
        return self._get_stats_for_period("date('now', '-7 days')")
    
    def get_stats_this_month(self) -> Dict:
        """Get statistics for this month"""
        return self._get_stats_for_period("date('now', 'start of month')")
    
    def _get_stats_for_period(self, date_clause: str) -> Dict:
        """Get statistics for a specific period"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Overall stats
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_files,
                    SUM(CASE WHEN status = 'organized' THEN 1 ELSE 0 END) as organized,
                    SUM(CASE WHEN status = 'duplicate' THEN 1 ELSE 0 END) as duplicates,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors
                FROM file_records
                WHERE date(timestamp) >= {date_clause}
            """)
            overall = dict(cursor.fetchone())
            
            # By document type
            cursor.execute(f"""
                SELECT document_type, COUNT(*) as count
                FROM file_records
                WHERE date(timestamp) >= {date_clause}
                    AND status = 'organized'
                GROUP BY document_type
            """)
            by_type = {row['document_type']: row['count'] for row in cursor.fetchall()}
            
            # Processing runs
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_runs,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as failed_runs
                FROM processing_runs
                WHERE date(start_time) >= {date_clause}
            """)
            runs = dict(cursor.fetchone())
            
            return {
                'total_files': overall['total_files'] or 0,
                'organized': overall['organized'] or 0,
                'duplicates': overall['duplicates'] or 0,
                'errors': overall['errors'] or 0,
                'by_type': by_type,
                'runs': runs
            }
    
    def get_classification_breakdown(self, days: int = 30) -> Dict[str, int]:
        """
        Get document type breakdown for last N days
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary of document_type: count
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT document_type, COUNT(*) as count
                FROM file_records
                WHERE date(timestamp) >= date('now', ? || ' days')
                    AND status = 'organized'
                GROUP BY document_type
                ORDER BY count DESC
            """, (f'-{days}',))
            return {row['document_type']: row['count'] for row in cursor.fetchall()}
    
    def get_daily_stats(self, days: int = 30) -> List[Dict]:
        """
        Get daily statistics for last N days
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of daily statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    date(timestamp) as date,
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'organized' THEN 1 ELSE 0 END) as organized,
                    SUM(CASE WHEN status = 'duplicate' THEN 1 ELSE 0 END) as duplicates,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors
                FROM file_records
                WHERE date(timestamp) >= date('now', ? || ' days')
                GROUP BY date(timestamp)
                ORDER BY date DESC
            """, (f'-{days}',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_system_health(self) -> Dict:
        """
        Get system health indicators
        
        Returns:
            Dictionary with health metrics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Last run
            cursor.execute("""
                SELECT * FROM processing_runs
                ORDER BY start_time DESC
                LIMIT 1
            """)
            last_run = cursor.fetchone()
            last_run_dict = dict(last_run) if last_run else None
            
            # Recent errors (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM errors
                WHERE datetime(timestamp) >= datetime('now', '-24 hours')
            """)
            recent_errors = cursor.fetchone()['count']
            
            # Success rate (last 7 days)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful
                FROM processing_runs
                WHERE datetime(start_time) >= datetime('now', '-7 days')
            """)
            success_data = dict(cursor.fetchone())
            success_rate = (
                success_data['successful'] / success_data['total'] * 100
                if success_data['total'] > 0 else 0
            )
            
            return {
                'last_run': last_run_dict,
                'recent_errors': recent_errors,
                'success_rate': success_rate,
                'total_runs_7days': success_data['total']
            }


# Global instance
_db = None

def get_tracking_db() -> TrackingDatabase:
    """Get or create global tracking database instance"""
    global _db
    if _db is None:
        _db = TrackingDatabase()
    return _db
