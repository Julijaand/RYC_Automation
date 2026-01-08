"""
Ingest training documents into ChromaDB vector database
Run this script whenever you add new training documents to rag_training_docs/
"""
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from src.config.settings import settings
import PyPDF2

def extract_text_from_file(file_path: Path) -> str:
    """Extract text from PDF, TXT, or return filename for images"""
    try:
        if file_path.suffix.lower() == '.pdf':
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        elif file_path.suffix.lower() == '.txt':
            return file_path.read_text(encoding='utf-8')
        else:
            # For images, use filename as content
            return f"Document: {file_path.name}"
    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")
        return f"Document: {file_path.name}"


def classify_training_doc(filename: str, content: str) -> str:
    """Determine document type from filename and content"""
    filename_lower = filename.lower()
    content_lower = content.lower()
    
    # Check filename first
    if any(word in filename_lower for word in ['invoice', 'facture', 'bill']):
        return 'invoice'
    if any(word in filename_lower for word in ['payroll', 'paie', 'salary']):
        return 'payroll'
    if any(word in filename_lower for word in ['contract', 'contrat']):
        return 'contract'
    if any(word in filename_lower for word in ['receipt', 'recu']):
        return 'receipt'
    if any(word in filename_lower for word in ['statement', 'releve']):
        return 'statement'
    
    # Check content
    if any(word in content_lower for word in ['invoice', 'facture', 'bill']):
        return 'invoice'
    if any(word in content_lower for word in ['payroll', 'paie', 'salary']):
        return 'payroll'
    
    return 'other'


def main():
    print("=" * 60)
    print("INGESTING TRAINING DOCUMENTS INTO RAG VECTOR DATABASE")
    print("=" * 60)
    
    # Paths
    training_dir = Path(settings.RAG_TRAINING_DOCS_PATH)
    vector_db_path = Path(settings.VECTOR_STORE_PATH)
    
    # Get all training documents
    training_files = list(training_dir.glob('*'))
    training_files = [f for f in training_files if f.is_file() and not f.name.startswith('.')]
    
    if not training_files:
        print(f"❌ No training documents found in {training_dir}")
        return
    
    print(f"\nFound {len(training_files)} training documents:")
    for f in training_files:
        print(f"  - {f.name}")
    
    # Load embedding model (same as classification: 384 dimensions)
    print("\nLoading embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Prepare documents for ingestion
    documents = []
    print("\nProcessing documents:")
    for file_path in training_files:
        content = extract_text_from_file(file_path)
        doc_type = classify_training_doc(file_path.name, content)
        
        # Create LangChain Document with metadata
        doc = Document(
            page_content=content[:1000],  # First 1000 chars
            metadata={
                "file_name": file_path.name,
                "document_type": doc_type,
                "file_path": str(file_path)
            }
        )
        documents.append(doc)
        print(f"  ✓ {file_path.name} → {doc_type}")
    
    # Delete old vector database to start fresh
    if vector_db_path.exists():
        print(f"\nDeleting old vector database at {vector_db_path}...")
        import shutil
        shutil.rmtree(vector_db_path)
    
    # Create new vector store with training documents
    print(f"\nCreating vector database at {vector_db_path}...")
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        collection_name=settings.COLLECTION_NAME,
        persist_directory=str(vector_db_path)
    )
    
    print("\n" + "=" * 60)
    print("✓ INGESTION COMPLETE")
    print("=" * 60)
    print(f"Ingested {len(documents)} documents:")
    
    # Count by type
    type_counts = {}
    for doc in documents:
        doc_type = doc.metadata['document_type']
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
    
    for doc_type, count in sorted(type_counts.items()):
        print(f"  - {doc_type}: {count}")
    
    print(f"\nVector database ready at: {vector_db_path}")
    print("You can now run the pipeline to classify documents using RAG!")


if __name__ == "__main__":
    main()
