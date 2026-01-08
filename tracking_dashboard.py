"""
RYC Automation - Tracking Dashboard

Comprehensive monitoring and analytics dashboard for document processing automation

Features:
- Real-time system health monitoring
- Processing statistics (today, this week, this month)
- Document classification breakdown with charts
- Processing history with detailed logs
- Error tracking and alerts
- Daily/weekly/monthly trend analysis

Run: streamlit run tracking_dashboard.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.tracking_db import get_tracking_db
from src.config.settings import settings

# Page configuration
st.set_page_config(
    page_title="RYC Automation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-metric { border-left: 5px solid #28a745; }
    .warning-metric { border-left: 5px solid #ffc107; }
    .error-metric { border-left: 5px solid #dc3545; }
    .info-metric { border-left: 5px solid #17a2b8; }
</style>
""", unsafe_allow_html=True)

# Initialize database
db = get_tracking_db()

# ==================== HEADER ====================
st.title("📊 RYC Automation Tracking Dashboard")
st.markdown("**Real-time monitoring and analytics for document processing automation**")
st.markdown("---")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()
    
    # Refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    # System info
    st.header("🖥️ System Info")
    st.write(f"**M: Drive:** `{settings.M_DRIVE_PATH}`")
    st.write(f"**Downloads:** `{settings.LOCAL_DOWNLOAD_PATH}`")
    st.write(f"**Model:** `{settings.OLLAMA_MODEL}`")
    
    st.markdown("---")
    
    # Quick stats
    st.header("📈 Quick Stats")
    stats_today = db.get_stats_today()
    st.metric("Files Today", stats_today['total_files'])
    st.metric("This Week", db.get_stats_this_week()['total_files'])
    st.metric("This Month", db.get_stats_this_month()['total_files'])

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview", 
    "📊 Analytics", 
    "📝 History", 
    "🔍 Monitoring",
    "⚠️ Errors"
])

# ==================== TAB 1: OVERVIEW ====================
with tab1:
    st.header("System Overview")
    
    # System Health Card
    st.subheader("🏥 System Health")
    health = db.get_system_health()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        last_run = health['last_run']
        if last_run:
            last_run_time = datetime.fromisoformat(last_run['start_time'])
            time_ago = datetime.now() - last_run_time
            hours_ago = time_ago.total_seconds() / 3600
            
            if hours_ago < 1:
                status_color = "🟢"
                status_text = "Healthy"
            elif hours_ago < 24:
                status_color = "🟡"
                status_text = "Warning"
            else:
                status_color = "🔴"
                status_text = "Alert"
            
            st.metric(
                "System Status",
                f"{status_color} {status_text}",
                f"Last run: {int(hours_ago)}h ago"
            )
        else:
            st.metric("System Status", "🔴 No runs", "Never run")
    
    with col2:
        success_rate = health['success_rate']
        if success_rate >= 90:
            delta_color = "normal"
        elif success_rate >= 70:
            delta_color = "off"
        else:
            delta_color = "inverse"
        
        st.metric(
            "Success Rate (7d)",
            f"{success_rate:.1f}%",
            f"{health['total_runs_7days']} runs"
        )
    
    with col3:
        recent_errors = health['recent_errors']
        st.metric(
            "Recent Errors (24h)",
            recent_errors,
            "🔴 Check logs" if recent_errors > 0 else "✓ All clear"
        )
    
    with col4:
        if last_run and last_run['status'] == 'success':
            st.metric(
                "Last Run",
                "✅ Success",
                f"{last_run.get('total_files', 0)} files"
            )
        elif last_run and last_run['status'] == 'error':
            st.metric(
                "Last Run",
                "❌ Failed",
                "See errors tab"
            )
        else:
            st.metric("Last Run", "N/A", "No data")
    
    st.markdown("---")
    
    # Period Statistics
    st.subheader("📊 Processing Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Today")
        today_stats = db.get_stats_today()
        st.metric("Total Files", today_stats['total_files'])
        st.metric("Organized", today_stats['organized'], f"+{today_stats['organized']}")
        st.metric("Duplicates", today_stats['duplicates'])
        st.metric("Errors", today_stats['errors'])
    
    with col2:
        st.markdown("### This Week")
        week_stats = db.get_stats_this_week()
        st.metric("Total Files", week_stats['total_files'])
        st.metric("Organized", week_stats['organized'], f"+{week_stats['organized']}")
        st.metric("Duplicates", week_stats['duplicates'])
        st.metric("Errors", week_stats['errors'])
    
    with col3:
        st.markdown("### This Month")
        month_stats = db.get_stats_this_month()
        st.metric("Total Files", month_stats['total_files'])
        st.metric("Organized", month_stats['organized'], f"+{month_stats['organized']}")
        st.metric("Duplicates", month_stats['duplicates'])
        st.metric("Errors", month_stats['errors'])
    
    st.markdown("---")
    
    # Document Type Breakdown (Today)
    st.subheader("📂 Document Types (Today)")
    
    by_type = today_stats['by_type']
    
    if by_type:
        # Create pie chart
        fig = px.pie(
            values=list(by_type.values()),
            names=list(by_type.keys()),
            title="Classification Breakdown",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
        # Show table
        df = pd.DataFrame({
            'Document Type': list(by_type.keys()),
            'Count': list(by_type.values())
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No documents processed today")

# ==================== TAB 2: ANALYTICS ====================
with tab2:
    st.header("Analytics & Trends")
    
    # Time period selector
    period = st.selectbox(
        "Select Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days"],
        index=1
    )
    
    days_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90
    }
    days = days_map[period]
    
    # Get daily stats
    daily_stats = db.get_daily_stats(days=days)
    
    if daily_stats:
        # Convert to DataFrame
        df = pd.DataFrame(daily_stats)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Daily Processing Trend
        st.subheader("📈 Daily Processing Trend")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'], 
            y=df['organized'],
            mode='lines+markers',
            name='Organized',
            line=dict(color='green', width=2),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['duplicates'],
            mode='lines+markers',
            name='Duplicates',
            line=dict(color='orange', width=2),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['errors'],
            mode='lines+markers',
            name='Errors',
            line=dict(color='red', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Files Processed Per Day",
            xaxis_title="Date",
            yaxis_title="Number of Files",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Processed", df['total'].sum())
            st.metric("Daily Average", f"{df['total'].mean():.1f}")
        
        with col2:
            st.metric("Success Rate", f"{(df['organized'].sum() / df['total'].sum() * 100):.1f}%")
            st.metric("Peak Day", df['total'].max())
        
        with col3:
            st.metric("Total Duplicates", df['duplicates'].sum())
            st.metric("Total Errors", df['errors'].sum())
        
        st.markdown("---")
        
        # Document type breakdown over time
        st.subheader("📊 Document Type Distribution")
        
        breakdown = db.get_classification_breakdown(days=days)
        
        if breakdown:
            fig = px.bar(
                x=list(breakdown.keys()),
                y=list(breakdown.values()),
                title=f"Document Types ({period})",
                labels={'x': 'Document Type', 'y': 'Count'},
                color=list(breakdown.keys()),
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Table view
            df_types = pd.DataFrame({
                'Document Type': list(breakdown.keys()),
                'Count': list(breakdown.values()),
                'Percentage': [f"{v/sum(breakdown.values())*100:.1f}%" for v in breakdown.values()]
            })
            st.dataframe(df_types, use_container_width=True, hide_index=True)
        else:
            st.info(f"No documents processed in {period.lower()}")
        
    else:
        st.info(f"No data available for {period.lower()}")

# ==================== TAB 3: HISTORY ====================
with tab3:
    st.header("Processing History")
    
    # Recent runs
    st.subheader("🔄 Recent Processing Runs")
    
    limit = st.slider("Number of runs to display", 5, 50, 10)
    recent_runs = db.get_recent_runs(limit=limit)
    
    if recent_runs:
        # Convert to DataFrame
        df_runs = pd.DataFrame(recent_runs)
        
        # Format timestamps
        df_runs['start_time'] = pd.to_datetime(df_runs['start_time'])
        if 'end_time' in df_runs.columns:
            df_runs['end_time'] = pd.to_datetime(df_runs['end_time'])
            df_runs['duration'] = (df_runs['end_time'] - df_runs['start_time']).dt.total_seconds()
            df_runs['duration'] = df_runs['duration'].apply(lambda x: f"{x:.1f}s" if pd.notna(x) else "N/A")
        
        # Select and rename columns
        display_df = df_runs[[
            'id', 'start_time', 'status', 'total_files', 
            'organized_files', 'duplicate_files', 'error_files', 'duration'
        ]].copy()
        
        display_df.columns = [
            'Run ID', 'Start Time', 'Status', 'Total', 
            'Organized', 'Duplicates', 'Errors', 'Duration'
        ]
        
        # Color code status
        def color_status(val):
            if val == 'success':
                return 'background-color: #d4edda'
            elif val == 'error':
                return 'background-color: #f8d7da'
            elif val == 'running':
                return 'background-color: #fff3cd'
            return ''
        
        styled_df = display_df.style.applymap(color_status, subset=['Status'])
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Detailed view
        st.markdown("---")
        st.subheader("📄 Run Details")
        
        selected_run_id = st.selectbox(
            "Select a run to view details",
            options=df_runs['id'].tolist(),
            format_func=lambda x: f"Run #{x} - {df_runs[df_runs['id']==x]['start_time'].iloc[0]}"
        )
        
        if selected_run_id:
            run = db.get_run_by_id(selected_run_id)
            files = db.get_files_by_run(selected_run_id)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Run Information**")
                st.write(f"ID: {run['id']}")
                st.write(f"Status: {run['status']}")
                st.write(f"Start: {run['start_time']}")
                st.write(f"End: {run['end_time']}")
                if run.get('error_message'):
                    st.error(f"Error: {run['error_message']}")
            
            with col2:
                st.write("**Statistics**")
                st.write(f"Total Files: {run.get('total_files', 0)}")
                st.write(f"Downloaded: {run.get('downloaded_files', 0)}")
                st.write(f"Classified: {run.get('classified_files', 0)}")
                st.write(f"Organized: {run.get('organized_files', 0)}")
                st.write(f"Duplicates: {run.get('duplicate_files', 0)}")
                st.write(f"Errors: {run.get('error_files', 0)}")
            
            # Files from this run
            if files:
                st.markdown("---")
                st.write(f"**Files Processed ({len(files)} files)**")
                
                df_files = pd.DataFrame(files)
                df_files['timestamp'] = pd.to_datetime(df_files['timestamp'])
                
                display_files = df_files[[
                    'filename', 'document_type', 'status', 'file_size', 'timestamp'
                ]].copy()
                
                display_files.columns = ['Filename', 'Type', 'Status', 'Size (bytes)', 'Timestamp']
                
                st.dataframe(display_files, use_container_width=True, hide_index=True)
    else:
        st.info("No processing runs found. Run the automation to see history.")

# ==================== TAB 4: MONITORING ====================
with tab4:
    st.header("Real-Time Monitoring")
    
    # System health check
    st.subheader("🏥 System Health Check")
    
    health = db.get_system_health()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Last Run Status")
        last_run = health['last_run']
        
        if last_run:
            status = last_run['status']
            start_time = datetime.fromisoformat(last_run['start_time'])
            time_ago = datetime.now() - start_time
            
            if status == 'success':
                st.success(f"✅ Last run successful")
            elif status == 'error':
                st.error(f"❌ Last run failed")
                if last_run.get('error_message'):
                    st.code(last_run['error_message'])
            else:
                st.warning(f"⏳ Run in progress")
            
            st.write(f"**Time:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Ago:** {int(time_ago.total_seconds() / 60)} minutes")
            st.write(f"**Files:** {last_run.get('total_files', 0)}")
        else:
            st.warning("No runs found")
    
    with col2:
        st.markdown("### Error Rate")
        
        recent_errors = health['recent_errors']
        success_rate = health['success_rate']
        
        if recent_errors == 0:
            st.success("✅ No errors in last 24 hours")
        elif recent_errors < 5:
            st.warning(f"⚠️ {recent_errors} errors in last 24 hours")
        else:
            st.error(f"🔴 {recent_errors} errors in last 24 hours")
        
        st.metric("7-Day Success Rate", f"{success_rate:.1f}%")
        
        if success_rate >= 90:
            st.success("Excellent performance")
        elif success_rate >= 70:
            st.warning("Needs attention")
        else:
            st.error("Critical: Multiple failures")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    
    recent_files = db.get_recent_files(limit=20)
    
    if recent_files:
        df = pd.DataFrame(recent_files)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        display_df = df[['timestamp', 'filename', 'document_type', 'status']].copy()
        display_df.columns = ['Time', 'Filename', 'Type', 'Status']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent activity")
    
    st.markdown("---")
    
    # System checks
    st.subheader("🔧 System Checks")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Check M: drive
        m_drive = Path(settings.M_DRIVE_PATH)
        if m_drive.exists():
            st.success("✅ M: Drive accessible")
        else:
            st.error("❌ M: Drive not found")
    
    with col2:
        # Check downloads folder
        downloads = Path(settings.LOCAL_DOWNLOAD_PATH)
        if downloads.exists():
            st.success("✅ Downloads folder ready")
        else:
            st.error("❌ Downloads folder missing")
    
    with col3:
        # Check database
        db_path = Path(settings.LOG_FILE).parent / "tracking.db"
        if db_path.exists():
            db_size = db_path.stat().st_size / 1024  # KB
            st.success(f"✅ Database active ({db_size:.1f} KB)")
        else:
            st.warning("⚠️ Database not found")

# ==================== TAB 5: ERRORS ====================
with tab5:
    st.header("Error Tracking & Alerts")
    
    st.subheader("🔴 Recent Errors")
    
    limit = st.slider("Number of errors to display", 5, 50, 20, key="error_limit")
    recent_errors = db.get_recent_errors(limit=limit)
    
    if recent_errors:
        for error in recent_errors:
            error_time = datetime.fromisoformat(error['timestamp'])
            time_ago = datetime.now() - error_time
            hours_ago = int(time_ago.total_seconds() / 3600)
            
            with st.expander(f"🔴 {error['error_type']} - {error_time.strftime('%Y-%m-%d %H:%M')} ({hours_ago}h ago)"):
                st.write(f"**Type:** {error['error_type']}")
                st.write(f"**Message:** {error['error_message']}")
                
                if error.get('file_path'):
                    st.write(f"**File:** {error['file_path']}")
                
                if error.get('stack_trace'):
                    st.code(error['stack_trace'], language='python')
    else:
        st.success("✅ No errors found")
    
    st.markdown("---")
    
    # Error summary
    st.subheader("📊 Error Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Errors (24h)", health['recent_errors'])
    
    with col2:
        if recent_errors:
            error_types = {}
            for error in recent_errors:
                error_type = error['error_type']
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            st.write("**By Type:**")
            for error_type, count in error_types.items():
                st.write(f"- {error_type}: {count}")
        else:
            st.write("No errors to categorize")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>RYC Automation Dashboard | Last updated: {}</small>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
