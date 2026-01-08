#!/bin/bash
# Quick launcher for RYC Automation Dashboard

echo "🚀 Starting RYC Automation Tracking Dashboard..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Launch Streamlit dashboard
streamlit run tracking_dashboard.py --server.port=8502

echo ""
echo "Dashboard closed."
