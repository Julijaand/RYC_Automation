"""
RAG Query Engine - Intelligent document classification using vector search
Uses LangChain (better Ollama support than LlamaIndex)
"""
from pathlib import Path
from typing import Optional
import re


def classify_document_with_rag(file_path: str, filename: str) -> str:
    """
    Classify document using RAG with LangChain + Ollama.
    
    Strategy:
    1. RAG: Search vector DB for similar documents → classify based on patterns
    2. Fallback: Direct Ollama classification with document content
    3. Final: Keyword matching
    
    Args:
        file_path: Full path to the document
        filename: Name of the file
        
    Returns:
        Document type: 'invoice', 'payroll', 'contract', 'receipt', 'statement', or 'other'
    """
    # LangChain RAG with Ollama (simplified approach without chains)
    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_ollama import OllamaLLM
        from src.config.settings import settings as app_settings
        
        # Check if vector DB exists
        vector_db_path = Path(app_settings.VECTOR_STORE_PATH)
        if vector_db_path.exists():
            print(f"Using RAG classification: {filename}")
            
            # Load embedding model (use same model as vector DB creation: all-MiniLM-L6-v2 = 384 dimensions)
            embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            
            # Initialize Ollama LLM
            llm = OllamaLLM(
                model=app_settings.OLLAMA_MODEL,
                base_url=app_settings.OLLAMA_BASE_URL,
                temperature=0.1
            )
            
            # Load vector store
            vector_store = Chroma(
                collection_name=app_settings.COLLECTION_NAME,
                embedding_function=embedding,
                persist_directory=str(vector_db_path),
            )
            
            # Read PDF content for classification
            file_content = ""
            if file_path.endswith('.pdf'):
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page_num in range(min(2, len(pdf_reader.pages))):
                            page = pdf_reader.pages[page_num]
                            file_content += page.extract_text()
                except Exception as e:
                    print(f"Could not read PDF: {e}")
            
            # Search for similar documents in vector DB with scores
            similar_docs_with_scores = vector_store.similarity_search_with_score(
                query=f"{filename} {file_content[:200]}",
                k=3
            )
            
            # Build context from similar documents
            similar_docs = [doc for doc, _ in similar_docs_with_scores]
            context = "Similar documents found:\n"
            for i, (doc, score) in enumerate(similar_docs_with_scores, 1):
                doc_type = doc.metadata.get('document_type', 'unknown')
                doc_name = doc.metadata.get('file_name', 'unknown')
                context += f"{i}. Type: {doc_type}, Name: {doc_name}, Score: {score:.3f}\n"
            
            print(f"  RAG Context: {context.strip()}")
            
            # Build classification prompt with RAG context
            prompt = f"""You are a document classifier. Your training database contains examples of invoices, payroll documents, and contracts.

Similar documents from training database:
{context}

New document to classify:
- Filename: {filename}
- Content: {file_content[:300] if file_content else "No content"}

CLASSIFICATION RULES:
1. If the new document looks like the training documents above (similar structure, purpose, content) - classify it as that type
2. If the new document does NOT look like ANY document in the training database - classify it as "other"
3. Examples of "other": notification letters, reports, memos, receipts, statements that don't match training data

Return ONLY ONE word (the category): invoice, payroll, contract, or other

Category:"""
            
            # Query Ollama with RAG context
            classification = llm.invoke(prompt).strip().lower()
            
            # Validate response
            valid_types = ['invoice', 'payroll', 'contract', 'receipt', 'statement', 'other']
            for doc_type in valid_types:
                if doc_type in classification:
                    print(f"✓ RAG classified as: {doc_type} (based on {len(similar_docs)} similar docs)")
                    return doc_type
            
            print("RAG unclear, trying direct Ollama...")
        else:
            print(f"No vector DB found, using direct Ollama...")
        
        # Fallback: Direct Ollama without RAG
        from langchain_ollama import OllamaLLM
        from src.config.settings import settings as app_settings
        
        llm = OllamaLLM(
            model=app_settings.OLLAMA_MODEL,
            base_url=app_settings.OLLAMA_BASE_URL,
            temperature=0.1
        )
        
        # Read file content for PDF files
        file_content = ""
        if file_path.endswith('.pdf'):
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page_num in range(min(2, len(pdf_reader.pages))):
                        page = pdf_reader.pages[page_num]
                        file_content += page.extract_text()
            except Exception as e:
                print(f"Could not read PDF content: {e}")
                file_content = ""
        
        # Build classification prompt
        prompt = f"""Classify this document into ONE of these categories:
- invoice (for invoices, factures, bills)
- payroll (for payroll slips, fiches de paie, salary documents)
- contract (for contracts, contrats, agreements)
- receipt (for receipts, reçus)
- statement (for bank statements, relevés bancaires)
- other (if none of the above)

Filename: {filename}

Document content preview:
{file_content[:500] if file_content else "No content available"}

Return ONLY the category name in lowercase, nothing else."""
        
        # Query Ollama directly
        classification = llm.invoke(prompt).strip().lower()
        
        # Validate classification
        valid_types = ['invoice', 'payroll', 'contract', 'receipt', 'statement', 'other']
        if classification in valid_types:
            print(f"✓ Ollama classified as: {classification}")
            return classification
        else:
            # Fallback to keyword matching if LLM returns unexpected value
            print("Ollama returned unclear result, falling back to keyword matching...")
            return _keyword_classify(filename)
            
    except Exception as e:
        print(f"Classification error: {e}. Falling back to keyword matching.")
        return _keyword_classify(filename)


def _keyword_classify(filename: str) -> str:
    """
    Fallback keyword-based classification.
    
    Args:
        filename: Name of the file
        
    Returns:
        Document type based on keywords
    """
    filename_lower = filename.lower()
    
    # Invoice keywords (English and French)
    if any(keyword in filename_lower for keyword in ['invoice', 'facture', 'bill', 'factuur']):
        return 'invoice'
    
    # Payroll keywords (English, French, Chinese pinyin)
    if any(keyword in filename_lower for keyword in ['payroll', 'paie', 'fiche de paie', 'salaire', 'salary', 'gongzi']):
        return 'payroll'
    
    # Contract keywords
    if any(keyword in filename_lower for keyword in ['contract', 'contrat', 'agreement', 'accord']):
        return 'contract'
    
    # Receipt keywords
    if any(keyword in filename_lower for keyword in ['receipt', 'reçu', 'recibo']):
        return 'receipt'
    
    # Statement keywords
    if any(keyword in filename_lower for keyword in ['statement', 'relevé', 'bank', 'bancaire']):
        return 'statement'
    
    return 'other'


def get_document_summary(file_path: str) -> str:
    """
    Extract a brief summary from document for preview.
    
    Args:
        file_path: Path to document
        
    Returns:
        First 200 characters of text content
    """
    try:
        if file_path.endswith('.pdf'):
            import PyPDF2
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                if len(pdf_reader.pages) > 0:
                    text = pdf_reader.pages[0].extract_text()
                    return text[:200].strip()
        return "No preview available"
    except Exception as e:
        return f"Error reading file: {e}"
