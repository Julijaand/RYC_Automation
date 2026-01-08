#!/usr/bin/env python3
"""
Health Check Script for RYC Automation

Checks:
1. Last run timestamp (alerts if > 24 hours)
2. Recent errors
3. Success rate
4. System components (M: drive, downloads folder, Ollama)
5. Database status

Exit codes:
0 - Healthy
1 - Warning (needs attention)
2 - Critical (immediate action required)
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.tracking_db import get_tracking_db
from src.config.settings import settings

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{BOLD}{'='*50}{RESET}\n")


def print_status(label, status, color):
    """Print formatted status line"""
    print(f"{label:.<40} {color}{status}{RESET}")


def check_last_run(db):
    """Check when automation last ran"""
    health = db.get_system_health()
    last_run = health.get('last_run')
    
    if not last_run:
        print_status("Last Run", "❌ NEVER RUN", RED)
        return 2, "System has never run"
    
    last_run_time = datetime.fromisoformat(last_run['start_time'])
    time_ago = datetime.now() - last_run_time
    hours_ago = time_ago.total_seconds() / 3600
    
    if hours_ago < 1:
        status = f"✅ {int(time_ago.total_seconds() / 60)} minutes ago"
        print_status("Last Run", status, GREEN)
        return 0, None
    elif hours_ago < 24:
        status = f"⚠️  {int(hours_ago)} hours ago"
        print_status("Last Run", status, YELLOW)
        return 1, f"Last run was {int(hours_ago)} hours ago"
    else:
        days_ago = int(hours_ago / 24)
        status = f"❌ {days_ago} days ago"
        print_status("Last Run", status, RED)
        return 2, f"Last run was {days_ago} days ago - system may be down"


def check_success_rate(db):
    """Check success rate"""
    health = db.get_system_health()
    success_rate = health['success_rate']
    total_runs = health['total_runs_7days']
    
    if total_runs == 0:
        print_status("Success Rate (7d)", "⚠️  No runs", YELLOW)
        return 1, "No runs in last 7 days"
    
    if success_rate >= 90:
        status = f"✅ {success_rate:.1f}% ({total_runs} runs)"
        print_status("Success Rate (7d)", status, GREEN)
        return 0, None
    elif success_rate >= 70:
        status = f"⚠️  {success_rate:.1f}% ({total_runs} runs)"
        print_status("Success Rate (7d)", status, YELLOW)
        return 1, f"Success rate is {success_rate:.1f}% (below 90%)"
    else:
        status = f"❌ {success_rate:.1f}% ({total_runs} runs)"
        print_status("Success Rate (7d)", status, RED)
        return 2, f"Success rate is {success_rate:.1f}% (critical)"


def check_recent_errors(db):
    """Check for recent errors"""
    health = db.get_system_health()
    error_count = health['recent_errors']
    
    if error_count == 0:
        print_status("Errors (24h)", "✅ None", GREEN)
        return 0, None
    elif error_count < 5:
        print_status("Errors (24h)", f"⚠️  {error_count} errors", YELLOW)
        return 1, f"{error_count} errors in last 24 hours"
    else:
        print_status("Errors (24h)", f"❌ {error_count} errors", RED)
        return 2, f"{error_count} errors in last 24 hours (critical)"


def check_system_components():
    """Check system components"""
    issues = []
    max_severity = 0
    
    # Check M: drive
    m_drive = Path(settings.M_DRIVE_PATH)
    if m_drive.exists():
        print_status("M: Drive", "✅ Accessible", GREEN)
    else:
        print_status("M: Drive", "❌ Not found", RED)
        issues.append("M: Drive not accessible")
        max_severity = 2
    
    # Check downloads folder
    downloads = Path(settings.LOCAL_DOWNLOAD_PATH)
    if downloads.exists():
        print_status("Downloads Folder", "✅ Ready", GREEN)
    else:
        print_status("Downloads Folder", "⚠️  Missing", YELLOW)
        issues.append("Downloads folder missing (will be created)")
        max_severity = max(max_severity, 1)
    
    # Check database
    db_path = Path(settings.LOG_FILE).parent / "tracking.db"
    if db_path.exists():
        db_size = db_path.stat().st_size / 1024  # KB
        print_status("Database", f"✅ Active ({db_size:.1f} KB)", GREEN)
    else:
        print_status("Database", "⚠️  Not found", YELLOW)
        issues.append("Database not found (will be created on first run)")
        max_severity = max(max_severity, 1)
    
    # Check Ollama (attempt connection)
    try:
        import requests
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            print_status("Ollama Service", "✅ Running", GREEN)
        else:
            print_status("Ollama Service", "⚠️  Not responding", YELLOW)
            issues.append("Ollama service not responding properly")
            max_severity = max(max_severity, 1)
    except Exception as e:
        print_status("Ollama Service", "❌ Not running", RED)
        issues.append("Ollama service is not running")
        max_severity = 2
    
    return max_severity, ", ".join(issues) if issues else None


def check_processing_stats(db):
    """Show processing statistics"""
    today = db.get_stats_today()
    week = db.get_stats_this_week()
    
    print(f"\n{BOLD}Processing Statistics:{RESET}")
    print(f"  Today:     {today['total_files']} files ({today['organized']} organized, {today['errors']} errors)")
    print(f"  This Week: {week['total_files']} files ({week['organized']} organized, {week['errors']} errors)")


def main():
    """Main health check"""
    print_header("RYC Automation - Health Check")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize database
    try:
        db = get_tracking_db()
    except Exception as e:
        print(f"\n{RED}❌ CRITICAL: Cannot connect to database{RESET}")
        print(f"   Error: {e}")
        return 2
    
    print(f"\n{BOLD}System Status:{RESET}\n")
    
    # Run all checks
    checks = []
    
    checks.append(check_last_run(db))
    checks.append(check_success_rate(db))
    checks.append(check_recent_errors(db))
    checks.append(check_system_components())
    
    # Show statistics
    check_processing_stats(db)
    
    # Determine overall status
    severities = [severity for severity, _ in checks]
    max_severity = max(severities)
    
    issues = [msg for severity, msg in checks if msg]
    
    # Print summary
    print(f"\n{BOLD}{'='*50}{RESET}")
    
    if max_severity == 0:
        print(f"\n{GREEN}{BOLD}✅ HEALTHY{RESET} - All systems operational\n")
        return 0
    elif max_severity == 1:
        print(f"\n{YELLOW}{BOLD}⚠️  WARNING{RESET} - System needs attention\n")
        print(f"{BOLD}Issues:{RESET}")
        for issue in issues:
            print(f"  • {issue}")
        print()
        return 1
    else:
        print(f"\n{RED}{BOLD}❌ CRITICAL{RESET} - Immediate action required\n")
        print(f"{BOLD}Issues:{RESET}")
        for issue in issues:
            print(f"  • {issue}")
        print()
        return 2


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Health check interrupted{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Health check failed: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
