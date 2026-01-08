"""
Document Ingestion - Build RAG knowledge base from existing documents
"""
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
import chromadb
from pathlib import Path
from typing import List
from src.config.settings import settings
import ssl

# SSL fix for NLTK
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

import nltk
try:
    nltk.download("punkt_tab", quiet=True)
    nltk.download("stopwords", quiet=True)
except:
    pass


def ingest_documents_for_rag(document_paths: List[str], collection_name: str = "ryc_documents"):
    """
    Ingest specific documents to build RAG knowledge base for classification.
    
    This function:
    1. Loads documents from specified paths
    2. Chunks them into nodes (chunk_size=1024, overlap=50)
    3. Creates embeddings using HuggingFace
    4. Stores in ChromaDB vector store
    
    Args:
        document_paths: List of paths to documents to ingest
        collection_name: Name of the vector store collection
        
    Returns:
        VectorStoreIndex: Indexed documents ready for querying
    """
    print(f"Ingesting {len(document_paths)} documents for RAG...")
    
    # Configuration
    vector_db_path = Path(settings.VECTOR_STORE_PATH)
    vector_db_path.mkdir(parents=True, exist_ok=True)
    
    # Define embedding model (HuggingFace)
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Configure Ollama LLM
    Settings.llm = Ollama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.1
    )
    
    # Load documents using SimpleDirectoryReader for each file
    documents = []
    for doc_path in document_paths:
        path = Path(doc_path)
        if not path.exists():
            print(f"Warning: Document not found: {doc_path}")
            continue
        
        try:
            # Load document
            loader = SimpleDirectoryReader(input_files=[str(path)])
            docs = loader.load_data()
            
            # Add metadata about document type (from folder structure)
            doc_type = "other"
            path_str = str(path).lower()
            if 'invoice' in path_str or 'facture' in path_str:
                doc_type = "invoice"
            elif 'payroll' in path_str or 'paie' in path_str:
                doc_type = "payroll"
            elif 'contract' in path_str:
                doc_type = "contract"
            elif 'receipt' in path_str:
                doc_type = "receipt"
            elif 'statement' in path_str:
                doc_type = "statement"
            
            for doc in docs:
                doc.metadata['doc_type'] = doc_type
                doc.metadata['original_path'] = str(path)
            
            documents.extend(docs)
            print(f"  ✓ Loaded: {path.name} (type: {doc_type})")
            
        except Exception as e:
            print(f"  ✗ Error loading {doc_path}: {e}")
            continue
    
    if not documents:
        print("❌ No documents were successfully loaded")
        return None
    
    print(f"\nTotal documents loaded: {len(documents)}")
    
    # Create parser with chunking strategy
    parser = SimpleNodeParser.from_defaults(
        chunk_size=1024,
        chunk_overlap=50
    )
    
    # Convert documents to chunks (nodes)
    print("Creating chunks from documents...")
    nodes = parser.get_nodes_from_documents(documents)
    print(f"Created {len(nodes)} chunks")
    
    # Define persistent DB location
    db = chromadb.PersistentClient(path=str(vector_db_path))
    
    # Create or retrieve the vector collection
    chroma_collection = db.get_or_create_collection(name=collection_name)
    
    # Create vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Create storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create the vector store index
    print("Creating vector index...")
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        vector_store=vector_store,
        embed_model=embed_model,
        show_progress=True
    )
    
    print(f"\n✅ Vector database created at: {vector_db_path}")
    print(f"   Collection: {collection_name}")
    print(f"   Total chunks indexed: {len(nodes)}")
    
    return index


def initialize_rag_from_existing_files():
    """
    Initialize RAG system by ingesting sample documents from test_drive.
    
    This should be run once to build the initial knowledge base.
    """
    # Get all PDF files from test_drive
    test_drive = Path(settings.M_DRIVE_PATH)
    
    if not test_drive.exists():
        print(f"Test drive not found at {test_drive}")
        return None
    
    # Find all PDF files
    pdf_files = list(test_drive.rglob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in test_drive for RAG initialization")
        return None
    
    print(f"Found {len(pdf_files)} PDF files for RAG ingestion")
    
    # Ingest documents
    index = ingest_documents_for_rag([str(f) for f in pdf_files])
    
    return index


if __name__ == "__main__":
    # Run this script to initialize RAG system
    print("Initializing RAG system with existing documents...")
    initialize_rag_from_existing_files()
    print("RAG initialization complete!")
