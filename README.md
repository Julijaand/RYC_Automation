# RYC Automation System

Automated document processing system for RYC Company - retrieves, classifies, and organizes accounting and payroll documents from Gmail to shared drive.

## 📋 What It Does

1. **Monitors Gmail** - Checks for emails with attachments (invoices, payroll, contracts)
2. **Smart Classification** - Uses RAG (Retrieval-Augmented Generation) to learn from your training documents
3. **Auto-Organization** - Files organized by type and date: `test_drive/{doc_type}/{year-month}/`

## 📋 Features

- ✅ Gmail API integration with email tracking (no duplicate downloads)
- ✅ Automatic file classification (invoice, payroll, etc.)
- ✅ RAG-based classification (learns from your documents)
- ✅ Document-type-based organization on M: drive
- ✅ Duplicate file detection (skips existing files)
- ✅ Comprehensive logging system
- ✅ Multi-language support (English, French, Chinese)
- ✅ Local LLM (Ollama) - no API costs

## 📁 Project Structure
```
RYC_Automation/
├── src/
│   ├── main.py                    # Entry point
│   ├── services/
│   │   ├── gmail_service.py       # Gmail download with tracking
│   │   ├── classification_service.py  # RAG classification
│   │   └── file_organizer_service.py  # File organization
│   ├── workflows/
│   │   └── document_pipeline.py   # Main pipeline orchestrator
│   ├── rag/
│   │   └── query_engine.py        # RAG classification engine
│   ├── config/
│   │   └── settings.py            # Configuration
│   └── utils/
│       ├── logger.py              # Logging
│       └── email_tracker.py       # Duplicate prevention
├── rag_training_docs/             # Training documents for RAG
├── vector_db/                     # ChromaDB vector store
├── ingest_training_docs.py        # Script to update RAG database
├── rag_manager_ui.py              # Streamlit UI for training docs
├── downloads/                     # Temp folder (auto-created)
├── test_drive/                    # Organized files output
│   ├── invoice/{year-month}/
│   ├── payroll/{year-month}/
│   └── contract/{year-month}/
├── logs/                          # Automation logs
├── archive/                       # Old CrewAI code (backup)
├── credentials.json               # Gmail OAuth (you provide)
├── token.json                     # Gmail token (auto-created)
├── processed_emails.json          # Email tracking (auto-created)
├── .env                           # Environment variables
└── requirements.txt               # Python dependencies
```

---

## 🚀 Quick Start

### 1. Install Ollama (Local LLM)
```bash
# macOS
brew install ollama

# Start Ollama service
ollama serve

# In new terminal, pull model
ollama pull llama3.2:latest
```

### 2. Install Python Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env - verify these settings:
# M_DRIVE_PATH=./test_drive
# OLLAMA_MODEL=llama3.2:latest
```

### 4. Setup Gmail API

#### Step 4.1: Google Cloud Console Setup
1. Go to https://console.cloud.google.com/
2. Sign in with your Google account
3. Click project dropdown → **"NEW PROJECT"**
4. Name: `RYC-Automation` → Click **"CREATE"**
5. Select your new project from the dropdown

#### Step 4.2: Enable Gmail API
1. Left sidebar → **"APIs & Services"** → **"Library"**
2. Search for: `Gmail API`
3. Click **"Gmail API"** → Click **"ENABLE"**

#### Step 4.3: Configure OAuth Consent Screen
1. Left sidebar → **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** → Click **"CREATE"**
3. Fill in required fields:
   - **App name**: `RYC Automation`
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click **"SAVE AND CONTINUE"** (3 times)
5. On "Test users" page → **"+ ADD USERS"**
   - Add your Gmail address
   - Click **"ADD"** → **"SAVE AND CONTINUE"**
6. Click **"BACK TO DASHBOARD"**

#### Step 4.4: Create OAuth Credentials
1. Left sidebar → **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Application type: **"Desktop app"**
4. Name: `RYC Desktop Client`
5. Click **"CREATE"**
6. Click **"DOWNLOAD JSON"** (⬇️ icon)

#### Step 4.5: Install Credentials
1. Rename downloaded file to: `credentials.json`
2. Move to project root: `/Users/julijaand/Desktop/RYC_Automation/credentials.json`

#### Step 4.6: Authenticate
```bash
python scripts/setup_gmail.py
```

**What happens:**
1. Browser opens automatically
2. Sign in to Google
3. Warning: "Google hasn't verified this app"
   - Click **"Advanced"** → **"Go to RYC Automation (unsafe)"**
4. Review permissions → Click **"Continue"**
5. Terminal shows: `✅ SUCCESS! Gmail API is working`

#### Step 4.7: Verify
```bash
ls -la | grep -E '(credentials|token)'
```
Should see: `credentials.json` and `token.json`

### 5. Setup RAG Training Documents

#### Add Training Documents
```bash
# Option 1: Use Streamlit UI (recommended)
streamlit run rag_manager_ui.py
# Open http://localhost:8501
# Upload sample invoices, payroll, contracts

# Option 2: Copy files directly
cp your_invoice.pdf rag_training_docs/
cp your_payroll.jpg rag_training_docs/
```

#### Build Vector Database
```bash
python ingest_training_docs.py
```

### 6. Run the Automation

#### Full Pipeline (Download → Classify → Organize)
```bash
python -m src.main
```

#### Without AI Agent Fallback (faster)
```bash
python -m src.main --no-agent
```

#### Check Results
```bash
ls -R test_drive/
# Should see: invoice/, payroll/, contract/ folders organized by year-month
```

### 7. Monitor with Dashboard

#### Launch Tracking Dashboard
```bash
./run_dashboard.sh
# Opens at http://localhost:8502
```

**Dashboard shows:**
- Real-time system health
- Processing statistics and trends
- Document classification breakdown
- Error tracking and alerts
- Complete processing history

---

## 💡 How It Works

### 3-Step Pipeline

1. **Download** (`gmail_service.py`)
   - Searches Gmail: `has:attachment (invoice OR payroll OR facture OR paie)`
   - Downloads attachments to `downloads/`
   - Tracks processed emails in `processed_emails.json` (no duplicates)

2. **Classify** (`classification_service.py` + `query_engine.py`)
   - **RAG**: Finds 3 most similar documents from training set (vector similarity)
   - **LLM**: Ollama analyzes patterns and classifies (invoice/payroll/contract/other)
   - **Fallback**: Keyword matching if RAG fails

3. **Organize** (`file_organizer_service.py`)
   - Creates folders: `test_drive/{doc_type}/{year-month}/`
   - Renames files: `{doc_type}_{date}_{original_name}`
   - Hash-based duplicate detection (skips existing files)

### RAG Training Flow

```
Upload docs → rag_training_docs/ → ingest script → ChromaDB vector_db/ → Query engine uses for classification
```

---

## 🎨 Streamlit Dashboards

### 📊 Tracking Dashboard 

**Comprehensive monitoring and analytics dashboard**

```bash
# Option 1: Use launcher script
./run_dashboard.sh

# Option 2: Run directly
streamlit run tracking_dashboard.py --server.port=8502
```

Open: http://localhost:8502

**Features:**
- 🏠 **Overview Tab**
  - System health status
  - Processing statistics (today/week/month)
  - Success rate monitoring
  - Document type breakdown with pie charts
  
- 📊 **Analytics Tab**
  - Daily processing trends (line charts)
  - Document type distribution (bar charts)
  - Performance metrics
  - Historical analysis (7/30/90 days)

- 📝 **History Tab**
  - Recent processing runs
  - Detailed run information
  - File-level tracking
  - Searchable and filterable logs

- 🔍 **Monitoring Tab**
  - Real-time system status
  - Last run details
  - Recent activity feed
  - System health checks

- ⚠️ **Errors Tab**
  - Error tracking and categorization
  - Stack traces for debugging
  - Error trends and patterns
  - Alert notifications

### 📚 RAG Training Manager

**Manage training documents with web interface:**

```bash
streamlit run rag_manager_ui.py
```

Open: http://localhost:8501

**Features:**
- 📤 Upload new training documents
- 📂 View/delete existing documents
- 🔄 Re-ingest vector database
- 📊 Statistics (doc counts by type)

---

## 📝 Configuration

Edit `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `M_DRIVE_PATH` | Output folder for organized files | `./test_drive` |
| `LOCAL_DOWNLOAD_PATH` | Temp downloads | `./downloads` |
| `OLLAMA_MODEL` | Ollama model name | `llama3.2:latest` |
| `OLLAMA_BASE_URL` | Ollama API endpoint | `http://localhost:11434` |
| `RAG_TRAINING_DOCS_PATH` | Training documents | `./rag_training_docs` |
| `GMAIL_CREDENTIALS_PATH` | Gmail OAuth credentials | `credentials.json` |
| `GMAIL_TOKEN_PATH` | Gmail access token | `token.json` |
| `LOG_LEVEL` | Logging level | `INFO` |

---

## 🔧 Useful Commands

### View Logs
```bash
tail -f logs/automation.log
```

### Clear Email Tracking (Force Re-download)
```bash
echo '{}' > processed_emails.json
```

### Re-train RAG System
```bash
# Add new training documents to rag_training_docs/
python ingest_training_docs.py
```

### Check Ollama Status
```bash
ollama list  # Show installed models
curl http://localhost:11434/api/tags  # Check if Ollama is running
```

### Production Deployment

#### Quick Start: Automated Scheduling

**macOS/Linux (Recommended):**
```bash
./deployment/setup_cron.sh
# Interactive script - select schedule (30min/hourly/3x daily/custom)
```

**Linux Servers (systemd):**
```bash
# See deployment/ryc-automation.service
sudo cp deployment/ryc-automation.service /etc/systemd/system/
sudo systemctl enable ryc-automation.timer
sudo systemctl start ryc-automation.timer
```

**Windows:**
- See [DEPLOYMENT.md](DEPLOYMENT.md) for Task Scheduler setup

#### Health Monitoring

**Option 1: Dashboard (Visual)**
```bash
./run_dashboard.sh
# Monitor at http://localhost:8502
```

**Option 2: CLI (Automation)**
```bash
python deployment/health_check.py
# Exit codes: 0=Healthy, 1=Warning, 2=Critical
```

#### Complete Guide

📖 **See [DEPLOYMENT.md](DEPLOYMENT.md)** for:
- Automated scheduling setup (cron/systemd/Task Scheduler)
- Health monitoring and alerting
- Backup and maintenance procedures
- Production checklist
- Troubleshooting guide

#### Manual Setup (Advanced)

1. Update `.env` with real M: drive path:
   ```env
   M_DRIVE_PATH=/Volumes/ShareDrive  # macOS
   M_DRIVE_PATH=/mnt/share           # Linux
   M_DRIVE_PATH=M:\                  # Windows
   ```

2. Schedule with cron (macOS/Linux):
   ```bash
   crontab -e
   # Add: Run every 30 minutes during business hours
   */30 9-17 * * 1-5 cd /path/to/RYC_Automation && /path/to/venv/bin/python -m src.main --no-agent
   ```

3. Or use Task Scheduler (Windows) - see DEPLOYMENT.md

---

## 🛠️ Troubleshooting

### Ollama Issues

**"Connection refused" or "Ollama not running"**
```bash
ollama serve  # Start Ollama service
```

**"Model not found"**
```bash
ollama pull llama3.2:latest
```

### Gmail API Issues

**"File credentials.json not found"**
- Ensure file is in project root
- Check filename is exactly `credentials.json`

**"Access blocked: This app's request is invalid"**
- Add yourself as test user in OAuth consent screen

**"All emails already processed"**
- Normal behavior (prevents duplicates)
- To force re-download: `echo '{}' > processed_emails.json`

### RAG Classification Issues

**"Classification always returns 'other'"**
- Need more training documents
- Run: `python ingest_training_docs.py` after adding docs

**"Vector DB not found"**
```bash
python ingest_training_docs.py  # Rebuild vector database
```

### File Organization Issues

**Files not organizing**
- Check logs: `tail -f logs/automation.log`
- Verify downloads/ folder has files
- Check M: drive path exists: `ls -la test_drive/`

---

## 📚 Technical Details

### RAG Classification Pipeline
```
User uploads training docs → ChromaDB vectors → Query finds similar docs → Ollama analyzes → Classification result
```

**Why RAG?**
- Learns from YOUR specific documents
- No training required - just add examples
- Improves accuracy over time
- Works with any document format

### Technologies Used
- **LangChain** - RAG framework
- **ChromaDB** - Vector database (embeddings storage)
- **Ollama** - Local LLM (no API costs)
- **Sentence Transformers** - Text embeddings (384-dim)
- **Gmail API** - Email access
- **Streamlit** - Web UI

### File Naming Convention
```
DocType_YYYYMMDD_OriginalName.ext
```

Examples:
- `invoice_20241228_Invoice123.pdf`
- `payroll_20241215_Payroll_Dec2024.jpg`

### Folder Structure
```
M: (or test_drive/)
├── invoice/
│   ├── 2024/
│   │   ├── 11/
│   │   └── 12/
│   │       ├── invoice_20241228_Invoice123.pdf
│   │       └── invoice_20241228_Facture_042.pdf
├── payroll/
│   └── 2024/
│       └── 12/
│           ├── payroll_20241215_Payroll_WangHua.jpg
│           └── payroll_20241228_Fiche_Paie_ChenXiaoli.png
└── other/
    └── 2024/
        └── 12/
            └── other_20241210_Document.pdf
```

### Email Tracking
The system maintains `processed_emails.json` to track which emails have been downloaded:

```json
{
  "19b64b18b295476e": {
    "processed_at": "2025-12-30T12:05:26",
    "subject": "Fiche de paie décembre"
  }
}
```

This prevents:
- Re-downloading the same attachments
- Wasting Gmail API quota
- Creating duplicate files

---

## 🔒 Security

- ✅ All credentials in `.gitignore`
- ✅ OAuth 2.0 for Gmail access (read-only)
- ✅ Email tracking stored locally
- ✅ No external API calls except Gmail

**Never commit:**
- `credentials.json`
- `token.json`
- `.env`
- `processed_emails.json`

---

## 📊 Performance

- **Email tracking**: Prevents duplicate downloads
- **File duplicate detection**: Skips existing files
- **Efficient**: Processes 100+ files in seconds
- **Gmail API quota**: ~1 request per email

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] Update `.env` with real M: drive path
- [ ] Test with a few emails first
- [ ] Verify folder structure is correct
- [ ] ✅ **Set up automated scheduling** - Run `./deployment/setup_cron.sh`
- [ ] ✅ **Configure health monitoring** - Dashboard + CLI checks
- [ ] Monitor `logs/automation.log` regularly
- [ ] Back up `processed_emails.json` periodically
- [ ] Back up `logs/tracking.db` (tracking database)
- [ ] Document your Gmail search query
- [ ] Review [DEPLOYMENT.md](DEPLOYMENT.md) for production best practices

**📖 Complete deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)**

---

## 🚧 Future Enhancements

Potential improvements:
- OCR for scanned documents
- Client name extraction from PDFs
- Email notifications on errors
- Web dashboard for monitoring
- Database instead of JSON tracking
- Support for more document types

---

## 🤝 Support

For issues or questions, contact the RYC development team.

## 📄 License

Internal use only - RYC Company