# Project Cleanup Plan

## What Will Happen

### ✅ KEEP (Production Code)

```
RYC_Automation/
├── src/
│   ├── services/              ✓ NEW: Direct services (hybrid approach)
│   │   ├── gmail_service.py
│   │   ├── classification_service.py
│   │   └── file_organizer_service.py
│   │
│   ├── workflows/             ✓ NEW: Hybrid pipeline
│   │   └── document_pipeline.py
│   │
│   ├── agents/
│   │   └── intelligent_classifier_agent.py  ✓ NEW: Edge case agent
│   │
│   ├── rag/                   ✓ RAG classification
│   │   ├── doc_ingestion.py
│   │   └── query_engine.py
│   │
│   ├── utils/                 ✓ Utilities
│   │   ├── logger.py
│   │   └── email_tracker.py
│   │
│   ├── config/                ✓ Configuration
│   │   └── settings.py
│   │
│   └── main.py                ✓ MAIN: Entry point (hybrid)
│
├── scripts/                   ✓ Setup scripts
│   └── setup_gmail.py
│
├── README.md                  ✓ Main documentation
├── HYBRID_APPROACH.md         ✓ How hybrid works
├── QUICK_START.md             ✓ Getting started
├── requirements.txt           ✓ Dependencies
├── .env                       ✓ Configuration
├── credentials.json           ✓ Gmail OAuth
├── token.json                 ✓ Gmail token
├── processed_emails.json      ✓ Email tracking
│
├── logs/                      ✓ Runtime logs
├── downloads/                 ✓ Temp downloads
├── test_drive/                ✓ M: drive simulation
├── vector_db/                 ✓ RAG database
└── rag_training_docs/         ✓ RAG training data
```

### 📦 ARCHIVE (Moved to archive/ folder)

```
archive/
├── old_crewai_agents/         ❌ Old CrewAI implementation
│   ├── crew.py                   - Had infinite loop issues
│   ├── gmail_agent.py
│   ├── classifier_agent.py
│   └── organizer_agent.py
│
├── old_tools/                 ❌ Old CrewAI tools
│   ├── gmail_tool.py             - Replaced by gmail_service.py
│   └── file_manager_tool.py      - Replaced by file_organizer_service.py
│
├── old_scripts/               ❌ Old test scripts
│   ├── simple_workflow.py        - Superseded by hybrid pipeline
│   ├── test_downloads.py         - Old test
│   ├── test_hybrid_pipeline.py   - Test script
│   └── init_rag.py               - RAG initialization
│
├── old_docs/                  ❌ Extra documentation
│   ├── ARCHITECTURE_COMPARISON.md
│   ├── ARCHITECTURE_IMPROVEMENTS.md
│   ├── SOLUTION_SUMMARY.md
│   └── IMPLEMENTATION_COMPLETE.md
│
└── unused_features/           ❌ Unimplemented features
    ├── api/                      - API endpoint (not implemented)
    ├── dashboard/                - Dashboard (not implemented)
    └── test_documents/           - Test file generator
```

### 🗑️ DELETE (Duplicates/Unnecessary)

```
src/main_updated.py            ❌ Duplicate of main.py
src/tools/ (empty folder)      ❌ Will be removed if empty
tests/ (empty folder)          ❌ Will be removed if empty
```

## Why This Cleanup?

### Problems with Current Structure

1. **Multiple implementations** - Old CrewAI + New hybrid (confusing)
2. **Duplicate files** - `main.py` and `main_updated.py`
3. **Unused code** - API, dashboard never implemented
4. **Too much documentation** - 7 markdown files (only need 3)
5. **Old test scripts** - Superseded by new implementation

### After Cleanup Benefits

✅ **Clear structure** - Only hybrid approach visible  
✅ **No confusion** - No old CrewAI code in main folders  
✅ **Easy to navigate** - Fewer files, clear purpose  
✅ **Still available** - Old code archived, not deleted  
✅ **Production ready** - Clean codebase for deployment  

## How to Run Cleanup

### Option 1: Run the script (Recommended)

```bash
cd /Users/julijaand/Desktop/RYC_Automation
./cleanup.sh
```

This will automatically:
- Create `archive/` folder
- Move old files to appropriate subfolders
- Keep production code in place
- Remove duplicates

### Option 2: Manual review

Look at each file and decide:
- Keep for production
- Archive for reference
- Delete permanently

## After Cleanup

Your project structure will be:

```
RYC_Automation/
├── src/                  # Production code only
│   ├── services/         # NEW: Direct services
│   ├── workflows/        # NEW: Hybrid pipeline
│   ├── agents/           # Only intelligent_classifier_agent.py
│   ├── rag/              # RAG engine
│   ├── utils/            # Utilities
│   ├── config/           # Settings
│   └── main.py           # Entry point
│
├── scripts/              # Setup scripts
├── archive/              # OLD: Archived code (reference only)
│
├── README.md             # Main docs
├── HYBRID_APPROACH.md    # How it works
├── QUICK_START.md        # Getting started
│
└── [Essential files]     # Config, credentials, logs, etc.
```

Clean, simple, production-ready! 🚀

## Verification After Cleanup

Run these commands to verify everything still works:

```bash
# Test imports
python -c "from src.workflows.document_pipeline import DocumentPipeline; print('✓ Pipeline OK')"

# Test main
python -m src.main --help

# Full test (if you have emails)
python -m src.main
```

## Rollback (If Needed)

If something breaks, you can restore files from archive:

```bash
# Restore a specific file
cp archive/old_crewai_agents/crew.py src/agents/

# Restore entire folder
cp -r archive/old_tools src/
```

Everything is preserved in `archive/` - nothing is permanently deleted.

---

**Ready to clean up?** Run `./cleanup.sh` when you're ready!
