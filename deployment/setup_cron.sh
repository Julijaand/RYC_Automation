#!/bin/bash
# RYC Automation - Cron Job Setup Script
# This script helps you set up automated scheduling for the document automation

set -e  # Exit on error

echo "=========================================="
echo "RYC Automation - Cron Job Setup"
echo "=========================================="
echo ""

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Error: Virtual environment not found at $VENV_PYTHON"
    echo "   Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

echo "✅ Found Python virtual environment"
echo "   Project directory: $PROJECT_DIR"
echo "   Python: $VENV_PYTHON"
echo ""

# Test if automation runs
echo "🧪 Testing automation script..."
if ! "$VENV_PYTHON" -m src.main --help &> /dev/null; then
    echo "❌ Error: Automation script test failed"
    echo "   Please ensure the automation runs manually first: python -m src.main"
    exit 1
fi
echo "✅ Automation script is working"
echo ""

# Show scheduling options
echo "📅 Scheduling Options:"
echo ""
echo "1. Every 30 minutes (business hours: 9 AM - 6 PM, Monday-Friday)"
echo "   */30 9-18 * * 1-5"
echo ""
echo "2. Every hour (business hours: 9 AM - 6 PM, Monday-Friday)"
echo "   0 9-18 * * 1-5"
echo ""
echo "3. Three times a day (9 AM, 1 PM, 5 PM, Monday-Friday)"
echo "   0 9,13,17 * * 1-5"
echo ""
echo "4. Daily at 9 AM (Monday-Friday)"
echo "   0 9 * * 1-5"
echo ""
echo "5. Custom schedule"
echo ""

read -p "Select option (1-5): " OPTION

case $OPTION in
    1)
        CRON_SCHEDULE="*/30 9-18 * * 1-5"
        DESCRIPTION="Every 30 minutes, 9 AM - 6 PM, Mon-Fri"
        ;;
    2)
        CRON_SCHEDULE="0 9-18 * * 1-5"
        DESCRIPTION="Every hour, 9 AM - 6 PM, Mon-Fri"
        ;;
    3)
        CRON_SCHEDULE="0 9,13,17 * * 1-5"
        DESCRIPTION="Three times daily (9 AM, 1 PM, 5 PM), Mon-Fri"
        ;;
    4)
        CRON_SCHEDULE="0 9 * * 1-5"
        DESCRIPTION="Daily at 9 AM, Mon-Fri"
        ;;
    5)
        echo ""
        echo "Enter custom cron schedule (e.g., '0 9 * * 1-5' for daily at 9 AM):"
        echo "Format: minute hour day month weekday"
        echo "See: https://crontab.guru for help"
        read -p "Cron schedule: " CRON_SCHEDULE
        DESCRIPTION="Custom schedule: $CRON_SCHEDULE"
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "Selected schedule: $DESCRIPTION"
echo "Cron expression: $CRON_SCHEDULE"
echo ""

# Generate cron command
CRON_COMMAND="cd $PROJECT_DIR && $VENV_PYTHON -m src.main >> $PROJECT_DIR/logs/cron.log 2>&1"

# Full cron entry
CRON_ENTRY="$CRON_SCHEDULE $CRON_COMMAND"

echo "📝 Cron entry to be added:"
echo "---"
echo "$CRON_ENTRY"
echo "---"
echo ""

read -p "Do you want to add this to your crontab? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ Cancelled"
    echo ""
    echo "To add manually, run:"
    echo "  crontab -e"
    echo ""
    echo "Then add this line:"
    echo "  $CRON_ENTRY"
    exit 0
fi

# Backup current crontab
echo "💾 Backing up current crontab..."
crontab -l > "$PROJECT_DIR/deployment/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || true

# Add to crontab
echo "➕ Adding to crontab..."
(crontab -l 2>/dev/null || true; echo "# RYC Automation - $DESCRIPTION"; echo "$CRON_ENTRY") | crontab -

echo ""
echo "✅ Cron job successfully configured!"
echo ""
echo "📊 Current crontab:"
echo "---"
crontab -l | grep -A 1 "RYC Automation" || echo "No RYC entries found (this might be an error)"
echo "---"
echo ""
echo "📝 Logs will be written to: $PROJECT_DIR/logs/cron.log"
echo ""
echo "🔍 To view cron jobs:        crontab -l"
echo "✏️  To edit cron jobs:       crontab -e"
echo "🗑️  To remove this job:      crontab -e (then delete the RYC line)"
echo ""
echo "📊 Monitor with dashboard:  ./run_dashboard.sh"
echo "📝 View logs:               tail -f logs/cron.log"
echo ""
echo "✅ Setup complete! The automation will now run automatically."
echo ""
