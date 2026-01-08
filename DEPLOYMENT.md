# 🚀 RYC Automation - Production Deployment Guide

Complete guide for deploying RYC document automation to production with automated scheduling.

---

## ⚡ Quick Start

**Deploy in 3 steps:**

```bash
# 1. Setup automated scheduling
./deployment/setup_cron.sh

# 2. Verify it's working
crontab -l  # Should show RYC automation entry

# 3. Monitor with dashboard
./run_dashboard.sh  # Opens at http://localhost:8502
```

**Daily monitoring:**
```bash
python deployment/health_check.py  # Quick health check
./run_dashboard.sh                  # Full dashboard
tail -f logs/automation.log         # Live logs
```

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Scheduling Options](#scheduling-options)
3. [macOS/Linux Setup (Cron)](#macoslinux-setup-cron)
4. [Linux Server Setup (Systemd)](#linux-server-setup-systemd)
5. [Windows Setup (Task Scheduler)](#windows-setup-task-scheduler)
6. [Health Monitoring](#health-monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

---

## Prerequisites

Before deploying to production:

- ✅ Automation runs successfully manually: `python -m src.main`
- ✅ Gmail API credentials configured (`credentials.json`, `token.json`)
- ✅ Ollama service installed and running
- ✅ RAG training documents added
- ✅ M: drive path configured in `.env`
- ✅ Dashboard tested: `./run_dashboard.sh`

**Test Run:**
```bash
cd /Users/julijaand/Desktop/RYC_Automation
python -m src.main
```

If this works without errors, you're ready to deploy!

---

## Scheduling Options

Choose the scheduling method based on your operating system:

| OS | Method | Best For |
|----|--------|----------|
| **macOS** | Cron | Personal Mac, development |
| **Linux** | Cron or Systemd | Servers, production |
| **Windows** | Task Scheduler | Windows desktops/servers |

**Recommended Schedule:**
- **Every 30 minutes** during business hours (9 AM - 6 PM, Mon-Fri)
- OR **3 times daily** (9 AM, 1 PM, 5 PM, Mon-Fri)

---

## macOS/Linux Setup (Cron)

### Option 1: Automated Setup (Recommended)

```bash
cd /Users/julijaand/Desktop/RYC_Automation
./deployment/setup_cron.sh
```

**Interactive Setup:**
1. Select scheduling frequency
2. Confirms cron entry
3. Adds to crontab automatically
4. Backs up existing crontab

### Option 2: Manual Setup

**Step 1: Open crontab editor**
```bash
crontab -e
```

**Step 2: Add one of these schedules:**

```bash
# Every 30 minutes, 9 AM - 6 PM, Monday-Friday
*/30 9-18 * * 1-5 cd /Users/julijaand/Desktop/RYC_Automation && /Users/julijaand/Desktop/RYC_Automation/venv/bin/python -m src.main >> /Users/julijaand/Desktop/RYC_Automation/logs/cron.log 2>&1

# Three times daily (9 AM, 1 PM, 5 PM), Monday-Friday
0 9,13,17 * * 1-5 cd /Users/julijaand/Desktop/RYC_Automation && /Users/julijaand/Desktop/RYC_Automation/venv/bin/python -m src.main >> /Users/julijaand/Desktop/RYC_Automation/logs/cron.log 2>&1

# Daily at 9 AM, Monday-Friday
0 9 * * 1-5 cd /Users/julijaand/Desktop/RYC_Automation && /Users/julijaand/Desktop/RYC_Automation/venv/bin/python -m src.main >> /Users/julijaand/Desktop/RYC_Automation/logs/cron.log 2>&1
```

**Step 3: Save and exit** (`:wq` in vim, or Ctrl+X in nano)

**Step 4: Verify**
```bash
crontab -l  # List all cron jobs
```

### Cron Tips

**View logs:**
```bash
tail -f logs/cron.log
```

**List cron jobs:**
```bash
crontab -l
```

**Edit cron jobs:**
```bash
crontab -e
```

**Remove all cron jobs:**
```bash
crontab -r  # ⚠️ Removes ALL jobs!
```

**Test schedule syntax:**
- Visit https://crontab.guru
- Enter your cron expression
- Verify it matches your expectation

---

## Linux Server Setup (Systemd)

For production Linux servers, systemd provides better control and monitoring.

### Option 1: One-Time Execution (Cron-like)

Use the cron setup above - it works on Linux too!

### Option 2: Systemd Service (Background Service)

**Step 1: Edit service file**
```bash
nano deployment/ryc-automation.service
```

Replace these values:
- `/path/to/RYC_Automation` → Your actual project path
- `User=ryc` → Your Linux username

**Step 2: Install service**
```bash
sudo cp deployment/ryc-automation.service /etc/systemd/system/
sudo systemctl daemon-reload
```

**Step 3: Enable and start**
```bash
# Enable (start on boot)
sudo systemctl enable ryc-automation.service

# Start now
sudo systemctl start ryc-automation.service
```

**Step 4: Verify**
```bash
# Check status
sudo systemctl status ryc-automation.service

# View logs
sudo journalctl -u ryc-automation.service -f
```

### Systemd Timer (Scheduled Execution)

For scheduled runs (instead of continuous service):

**Step 1: Create timer file**
```bash
sudo nano /etc/systemd/system/ryc-automation.timer
```

**Step 2: Add timer configuration**
```ini
[Unit]
Description=RYC Automation Timer - Run every 30 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min

[Install]
WantedBy=timers.target
```

**Step 3: Enable timer**
```bash
sudo systemctl enable ryc-automation.timer
sudo systemctl start ryc-automation.timer
```

**Step 4: Check timer**
```bash
systemctl list-timers
```

### Systemd Commands

```bash
# Status
sudo systemctl status ryc-automation.service

# Start
sudo systemctl start ryc-automation.service

# Stop
sudo systemctl stop ryc-automation.service

# Restart
sudo systemctl restart ryc-automation.service

# Logs (live)
sudo journalctl -u ryc-automation.service -f

# Logs (last 100 lines)
sudo journalctl -u ryc-automation.service -n 100
```

---

## Windows Setup (Task Scheduler)

### Step 1: Open Task Scheduler
- Press `Win + R`
- Type `taskschd.msc`
- Press Enter

### Step 2: Create New Task
1. Click **"Create Task"** (not "Create Basic Task")
2. **General Tab:**
   - Name: `RYC Document Automation`
   - Description: `Automated document processing`
   - Select: **"Run whether user is logged on or not"**
   - Check: **"Run with highest privileges"**

### Step 3: Configure Trigger
1. **Triggers Tab** → **New**
2. **Daily** automation:
   - Begin the task: **On a schedule**
   - Settings: **Daily**, Start at **9:00 AM**
   - Advanced: Repeat task every **30 minutes** for **9 hours**
   - Days: Monday through Friday
3. Click **OK**

### Step 4: Configure Action
1. **Actions Tab** → **New**
2. Action: **Start a program**
3. Program/script: 
   ```
   C:\Path\To\RYC_Automation\venv\Scripts\python.exe
   ```
4. Arguments:
   ```
   -m src.main
   ```
5. Start in:
   ```
   C:\Path\To\RYC_Automation
   ```
6. Click **OK**

### Step 5: Configure Settings
1. **Settings Tab:**
   - Check: **"Run task as soon as possible after a scheduled start is missed"**
   - Check: **"If the task fails, restart every 5 minutes"**
   - Attempts: **3**
   - Stop task if runs longer than: **1 hour**

### Step 6: Save and Test
1. Click **OK** (enter password if prompted)
2. Right-click task → **Run** to test
3. Check logs: `C:\Path\To\RYC_Automation\logs\automation.log`

---

## Health Monitoring

### Dashboard Monitoring (Primary)

**Start dashboard:**
```bash
./run_dashboard.sh
```

Open: http://localhost:8502

**Monitor:**
- 🟢 Green status = Healthy
- 🟡 Yellow status = Warning
- 🔴 Red status = Critical

**Daily routine:**
1. Open dashboard
2. Check Overview tab (system status)
3. Review any errors in Errors tab
4. Done!

### CLI Health Check (Optional)

For automated monitoring or alerts:

```bash
python deployment/health_check.py
```

**Exit Codes:**
- `0` = Healthy
- `1` = Warning (needs attention)
- `2` = Critical (immediate action)

**Example: Send email on failure**
```bash
# Add to cron (runs every hour)
0 * * * * cd /path/to/RYC_Automation && python deployment/health_check.py || mail -s "RYC Alert: System Unhealthy" admin@company.com < /dev/null
```

**Example: Slack notification**
```bash
python deployment/health_check.py || curl -X POST -H 'Content-type: application/json' --data '{"text":"RYC Automation unhealthy!"}' YOUR_SLACK_WEBHOOK_URL
```

---

## Troubleshooting

### Cron Not Running

**Check cron logs (macOS):**
```bash
log show --predicate 'process == "cron"' --last 1h
```

**Check cron logs (Linux):**
```bash
grep CRON /var/log/syslog
```

**Common issues:**
1. **Wrong Python path** - Use full path to venv python
2. **Wrong working directory** - Add `cd /path/to/project` before command
3. **Environment variables** - Cron has minimal environment, source .env if needed
4. **Permissions** - Ensure cron user can access project files

**Test command manually:**
```bash
cd /Users/julijaand/Desktop/RYC_Automation && /Users/julijaand/Desktop/RYC_Automation/venv/bin/python -m src.main
```

If this works but cron doesn't, check paths and permissions.

### Ollama Not Running

**Start Ollama:**
```bash
ollama serve
```

**Check if running:**
```bash
curl http://localhost:11434/api/tags
```

**Auto-start Ollama (macOS):**
```bash
brew services start ollama
```

**Auto-start Ollama (Linux systemd):**
```bash
sudo systemctl enable ollama
sudo systemctl start ollama
```

### Gmail Token Expired

**Symptoms:**
- "Invalid token" error
- "Authentication failed"

**Solution:**
```bash
rm token.json
python scripts/setup_gmail.py
```

This will re-authenticate.

### M: Drive Not Accessible

**Check path:**
```bash
ls -la test_drive/  # or your M: drive path
```

**Update .env:**
```bash
M_DRIVE_PATH=/correct/path/here
```

### Database Issues

**Check database:**
```bash
ls -lh logs/tracking.db
```

**Repair database:**
```bash
sqlite3 logs/tracking.db "PRAGMA integrity_check;"
```

**Backup and reset:**
```bash
mv logs/tracking.db logs/tracking_backup.db
# New database created on next run
```

---

## Maintenance

### Daily
- ✅ Check dashboard for system status
- ✅ Review any errors

### Weekly
- ✅ Review weekly statistics in dashboard
- ✅ Check success rate (should be >90%)
- ✅ Verify M: drive has sufficient space

### Monthly
- ✅ Review monthly trends
- ✅ Archive or clean old logs if needed
- ✅ Update training documents if classification accuracy drops
- ✅ Backup database: `cp logs/tracking.db backups/tracking_$(date +%Y%m).db`

### As Needed
- 🔄 Update training documents for better classification
- 🔄 Adjust cron schedule based on email volume
- 🔄 Update Ollama model: `ollama pull llama3.2:latest`

---

## Backup Strategy

### What to Backup

**Critical:**
- `credentials.json` - Gmail OAuth credentials
- `token.json` - Gmail access token
- `.env` - Configuration
- `logs/tracking.db` - Processing history
- `rag_training_docs/` - Training documents
- `vector_db/` - RAG database

**Optional:**
- `logs/automation.log` - Text logs (can be archived)
- `processed_emails.json` - Email tracking

### Backup Commands

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup critical files
cp credentials.json token.json .env backups/$(date +%Y%m%d)/
cp logs/tracking.db backups/$(date +%Y%m%d)/
cp -r rag_training_docs backups/$(date +%Y%m%d)/
cp -r vector_db backups/$(date +%Y%m%d)/

# Create tar archive
tar -czf backups/ryc_backup_$(date +%Y%m%d).tar.gz \
    credentials.json token.json .env \
    logs/tracking.db rag_training_docs/ vector_db/
```

### Automated Backup (Cron)

```bash
# Add to crontab - backup daily at midnight
0 0 * * * cd /path/to/RYC_Automation && tar -czf backups/ryc_backup_$(date +\%Y\%m\%d).tar.gz credentials.json token.json .env logs/tracking.db rag_training_docs/ vector_db/
```

---

## Performance Optimization

### Database Cleanup (After 6+ Months)

```bash
# Check database size
ls -lh logs/tracking.db

# If > 100MB, archive old data
sqlite3 logs/tracking.db << EOF
DELETE FROM file_records WHERE timestamp < date('now', '-90 days');
DELETE FROM processing_runs WHERE start_time < date('now', '-90 days');
DELETE FROM errors WHERE timestamp < date('now', '-90 days');
VACUUM;
EOF
```

### Log Rotation

```bash
# Rotate automation.log monthly
cd logs
mv automation.log automation_$(date +%Y%m).log
gzip automation_$(date +%Y%m).log
```

### Vector Database Refresh

If classification accuracy drops:

```bash
# Re-ingest training documents
python ingest_training_docs.py
```

---

## Production Checklist

Before going to production:

- [ ] ✅ Automation runs successfully manually
- [ ] ✅ Dashboard accessible and showing data
- [ ] ✅ Cron job or scheduled task configured
- [ ] ✅ Logs directory created and writable
- [ ] ✅ M: drive path correct in `.env`
- [ ] ✅ Ollama service running
- [ ] ✅ Gmail credentials valid
- [ ] ✅ Training documents added
- [ ] ✅ Test run completed successfully
- [ ] ✅ Health check passing
- [ ] ✅ Backup strategy in place
- [ ] ✅ Team trained on dashboard usage

---

## Support

### View Logs
```bash
# Automation logs
tail -f logs/automation.log

# Cron logs
tail -f logs/cron.log

# Dashboard
# Open: http://localhost:8502 → History/Errors tabs
```

### Quick Commands

```bash
# Run automation manually
python -m src.main

# Check health
python deployment/health_check.py

# View dashboard
./run_dashboard.sh

# List cron jobs
crontab -l

# Test Ollama
curl http://localhost:11434/api/tags
```

---

## Next Steps

1. ✅ Configure scheduling (cron/systemd/Task Scheduler)
2. ✅ Monitor via dashboard for first week
3. ✅ Adjust schedule based on email volume
4. ✅ Set up backup strategy
5. ✅ Train team on dashboard usage

---

**Deployment complete! 🎉**

Your RYC automation is now running in production with:
- ✅ Automated scheduling
- ✅ Real-time monitoring dashboard
- ✅ Complete tracking and logging
- ✅ Health checks and alerts

For questions, refer to:
- **README.md** - General documentation
- **DASHBOARD_GUIDE.md** - Dashboard usage
- **This file** - Deployment and scheduling
