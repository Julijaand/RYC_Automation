"""
Streamlit UI for RAG Training Document Management

Features:
- Upload new training documents
- View existing training documents
- Manually classify uploaded files
- Trigger vector database re-ingestion
- View RAG statistics

Run: streamlit run rag_manager_ui.py
"""
import streamlit as st
from pathlib import Path
import shutil
from datetime import datetime

# Configuration (using default paths)
TRAINING_DIR = Path('./rag_training_docs')
VECTOR_DB_PATH = Path('./vector_db')
COLLECTION_NAME = 'ryc_documents'

# Page configuration
st.set_page_config(
    page_title="RAG Training Manager",
    page_icon="📚",
    layout="wide"
)

# Initialize paths
training_dir = TRAINING_DIR
vector_db_path = VECTOR_DB_PATH

# Create directories if they don't exist
training_dir.mkdir(exist_ok=True)

# Title
st.title("📚 RAG Training Document Manager")
st.markdown("---")

# Sidebar - Statistics
with st.sidebar:
    st.header("📊 Statistics")
    
    # Count training documents
    training_files = list(training_dir.glob('*'))
    training_files = [f for f in training_files if f.is_file() and not f.name.startswith('.')]
    
    st.metric("Training Documents", len(training_files))
    
    # Count by type
    invoice_count = len([f for f in training_files if 'invoice' in f.name.lower() or 'facture' in f.name.lower()])
    payroll_count = len([f for f in training_files if 'payroll' in f.name.lower() or 'paie' in f.name.lower()])
    other_count = len(training_files) - invoice_count - payroll_count
    
    st.write("**By Type:**")
    st.write(f"📄 Invoices: {invoice_count}")
    st.write(f"💰 Payroll: {payroll_count}")
    st.write(f"📋 Other: {other_count}")
    
    # Vector DB status
    st.markdown("---")
    st.header("🗄️ Vector Database")
    if vector_db_path.exists():
        st.success("✓ Database exists")
        db_size = sum(f.stat().st_size for f in vector_db_path.rglob('*') if f.is_file())
        st.write(f"Size: {db_size / 1024:.1f} KB")
    else:
        st.warning("⚠️ No database found")

# Main content - Tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "📂 View Documents", "🔄 Manage Database"])

# TAB 1: Upload Documents
with tab1:
    st.header("Upload Training Documents")
    st.write("Upload documents to train the RAG system. The more examples you provide, the better the classification.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=['pdf', 'jpg', 'jpeg', 'png', 'txt'],
            help="Upload invoice, payroll, or other business documents"
        )
    
    with col2:
        # Document type selector
        doc_type = st.selectbox(
            "Document Type",
            ["invoice", "payroll", "contract", "receipt", "statement", "other"],
            help="Select the type of documents you're uploading"
        )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) ready to upload**")
        
        if st.button("📥 Upload & Save", type="primary"):
            success_count = 0
            for uploaded_file in uploaded_files:
                try:
                    # Generate filename with type prefix
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_extension = Path(uploaded_file.name).suffix
                    new_filename = f"{doc_type}_{timestamp}_{uploaded_file.name}"
                    
                    # Save file
                    save_path = training_dir / new_filename
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    success_count += 1
                except Exception as e:
                    st.error(f"Error saving {uploaded_file.name}: {e}")
            
            if success_count > 0:
                st.success(f"✅ Uploaded {success_count} file(s) successfully!")
                st.info("💡 Don't forget to click 'Re-ingest Database' in the Manage Database tab to update the RAG system.")
                st.rerun()

# TAB 2: View Documents
with tab2:
    st.header("Current Training Documents")
    
    if not training_files:
        st.warning("No training documents found. Upload some in the Upload Documents tab.")
    else:
        # Group by type
        docs_by_type = {
            'invoice': [],
            'payroll': [],
            'other': []
        }
        
        for file in training_files:
            name_lower = file.name.lower()
            if 'invoice' in name_lower or 'facture' in name_lower:
                docs_by_type['invoice'].append(file)
            elif 'payroll' in name_lower or 'paie' in name_lower:
                docs_by_type['payroll'].append(file)
            else:
                docs_by_type['other'].append(file)
        
        # Display by type
        for doc_type, files in docs_by_type.items():
            if files:
                with st.expander(f"📁 {doc_type.upper()} ({len(files)} files)", expanded=True):
                    for file in sorted(files):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"📄 {file.name}")
                        
                        with col2:
                            size_kb = file.stat().st_size / 1024
                            st.write(f"{size_kb:.1f} KB")
                        
                        with col3:
                            if st.button("🗑️", key=f"delete_{file.name}"):
                                try:
                                    file.unlink()
                                    st.success(f"Deleted {file.name}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

# TAB 3: Manage Database
with tab3:
    st.header("Vector Database Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Re-ingest Training Documents")
        st.write("Update the vector database with current training documents.")
        st.warning("⚠️ This will delete the old database and create a new one.")
        
        if st.button("🚀 Re-ingest Database", type="primary"):
            if len(training_files) == 0:
                st.error("No training documents found. Upload some first!")
            else:
                with st.spinner("Ingesting documents into vector database..."):
                    try:
                        # Run ingestion script
                        import subprocess
                        result = subprocess.run(
                            ['python', 'ingest_training_docs.py'],
                            capture_output=True,
                            text=True,
                            cwd=Path(__file__).parent
                        )
                        
                        if result.returncode == 0:
                            st.success("✅ Database re-ingested successfully!")
                            with st.expander("📋 View ingestion log"):
                                st.code(result.stdout)
                            st.rerun()
                        else:
                            st.error(f"Error during ingestion: {result.stderr}")
                    except Exception as e:
                        st.error(f"Error during ingestion: {e}")
    
    with col2:
        st.subheader("🗑️ Delete Database")
        st.write("Remove the vector database completely.")
        st.warning("⚠️ You will need to re-ingest after deletion.")
        
        if st.button("Delete Database", type="secondary"):
            if vector_db_path.exists():
                try:
                    shutil.rmtree(vector_db_path)
                    st.success("✅ Database deleted!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.info("No database to delete.")

# Footer
st.markdown("---")
st.caption("💡 Tip: More diverse training documents = better classification accuracy")
