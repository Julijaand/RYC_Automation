"""
Fast Ollama Data Extraction Service
Extracts structured data from documents using direct Ollama LLM calls
Replaces slow CrewAI agents (50s) with fast direct calls (5-10s)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import PyPDF2
from PIL import Image
import base64
from langchain_ollama import OllamaLLM
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataExtractionService:
    """Service for extracting structured data from documents using direct Ollama LLM"""
    
    def __init__(self):
        self.llm = OllamaLLM(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL
        )
        self.extracted_data_path = Path("extracted_data.json")
        
        # Load existing data
        if self.extracted_data_path.exists():
            with open(self.extracted_data_path, 'r') as f:
                self.extracted_data = json.load(f)
        else:
            self.extracted_data = {"invoices": [], "payroll": [], "contracts": []}
    
    def _read_pdf(self, file_path: Path) -> str:
        """Extract text from PDF"""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return ""
    
    def _analyze_image(self, file_path: Path) -> str:
        """Extract text from image using vision model"""
        try:
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            prompt = """Extract all visible text from this image.
List all information including: customer/employee names, amounts, dates, numbers, line items, totals.
Be thorough and accurate."""
            
            response = self.llm.invoke(prompt, images=[image_data])
            return response
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return ""
    
    def extract_invoice_data(self, file_path: Path) -> Dict[str, Any]:
        """Extract structured data from an invoice"""
        
        logger.info(f"📄 Extracting invoice data from {file_path.name}")
        
        # Read file content
        if file_path.suffix.lower() == '.pdf':
            content = self._read_pdf(file_path)
        else:
            content = self._analyze_image(file_path)
        
        if not content:
            return {"error": "Could not read file"}
        
        # Create extraction prompt
        prompt = f"""You are an expert data extraction assistant. Extract structured invoice data from the following document.

Document content:
{content}

Extract the following fields in JSON format:
{{
    "customer_name": "name of the customer/client",
    "invoice_number": "invoice or facture number",
    "invoice_date": "invoice date (YYYY-MM-DD format)",
    "due_date": "payment due date (YYYY-MM-DD format)",
    "total_amount": "total amount as a number",
    "tax_amount": "tax amount as a number",
    "currency": "currency symbol or code",
    "line_items": [
        {{"description": "item description", "amount": "item amount as number"}}
    ]
}}

Rules:
- Return ONLY the JSON object, no extra text
- Use null for missing fields
- Convert all amounts to numbers (remove currency symbols)
- Use YYYY-MM-DD format for dates
- Be accurate and thorough

JSON:"""
        
        try:
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Parse JSON from response
            if '{' in response and '}' in response:
                json_start = response.index('{')
                json_end = response.rindex('}') + 1
                json_str = response[json_start:json_end]
                extracted_data = json.loads(json_str)
            else:
                extracted_data = {"raw_output": response, "error": "Could not parse JSON"}
            
            # Add metadata
            extracted_data["file_path"] = str(file_path)
            extracted_data["file_name"] = file_path.name
            extracted_data["extracted_at"] = datetime.now().isoformat()
            
            logger.info(f"✓ Invoice: Customer={extracted_data.get('customer_name')}, Amount={extracted_data.get('total_amount')}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "error": str(e),
                "extracted_at": datetime.now().isoformat()
            }
    
    def extract_payroll_data(self, file_path: Path) -> Dict[str, Any]:
        """Extract structured data from a payroll document"""
        
        logger.info(f"💰 Extracting payroll data from {file_path.name}")
        
        # Read file content
        if file_path.suffix.lower() == '.pdf':
            content = self._read_pdf(file_path)
        else:
            content = self._analyze_image(file_path)
        
        if not content:
            return {"error": "Could not read file"}
        
        # Create extraction prompt
        prompt = f"""You are an expert data extraction assistant. Extract structured payroll data from the following document.

Document content:
{content}

Extract the following fields in JSON format:
{{
    "employee_name": "name of the employee",
    "employee_id": "employee ID or number",
    "period_start": "pay period start date (YYYY-MM-DD format)",
    "period_end": "pay period end date (YYYY-MM-DD format)",
    "gross_pay": "gross pay amount as a number",
    "deductions": "total deductions as a number",
    "net_pay": "net pay amount as a number",
    "payment_date": "payment date (YYYY-MM-DD format)",
    "currency": "currency symbol or code"
}}

Rules:
- Return ONLY the JSON object, no extra text
- Use null for missing fields
- Convert all amounts to numbers (remove currency symbols)
- Use YYYY-MM-DD format for dates
- Be accurate and thorough

JSON:"""
        
        try:
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Parse JSON from response
            if '{' in response and '}' in response:
                json_start = response.index('{')
                json_end = response.rindex('}') + 1
                json_str = response[json_start:json_end]
                extracted_data = json.loads(json_str)
            else:
                extracted_data = {"raw_output": response, "error": "Could not parse JSON"}
            
            # Add metadata
            extracted_data["file_path"] = str(file_path)
            extracted_data["file_name"] = file_path.name
            extracted_data["extracted_at"] = datetime.now().isoformat()
            
            logger.info(f"✓ Payroll: Employee={extracted_data.get('employee_name')}, Net Pay={extracted_data.get('net_pay')}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "error": str(e),
                "extracted_at": datetime.now().isoformat()
            }
    
    def extract_contract_data(self, file_path: Path) -> Dict[str, Any]:
        """Extract structured data from a contract"""
        
        logger.info(f"📋 Extracting contract data from {file_path.name}")
        
        # Read file content
        if file_path.suffix.lower() == '.pdf':
            content = self._read_pdf(file_path)
        else:
            content = self._analyze_image(file_path)
        
        if not content:
            return {"error": "Could not read file"}
        
        # Create extraction prompt
        prompt = f"""You are an expert data extraction assistant. Extract structured contract data from the following document.

Document content:
{content}

Extract the following fields in JSON format:
{{
    "contract_number": "contract number or ID",
    "parties": ["name of party 1", "name of party 2"],
    "contract_type": "type of contract (employment, service, etc.)",
    "start_date": "contract start date (YYYY-MM-DD format)",
    "end_date": "contract end date (YYYY-MM-DD format)",
    "contract_value": "total contract value as a number",
    "currency": "currency symbol or code",
    "renewal_terms": "renewal terms description"
}}

Rules:
- Return ONLY the JSON object, no extra text
- Use null for missing fields
- Convert all amounts to numbers (remove currency symbols)
- Use YYYY-MM-DD format for dates
- parties should be a list of strings
- Be accurate and thorough

JSON:"""
        
        try:
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Parse JSON from response
            if '{' in response and '}' in response:
                json_start = response.index('{')
                json_end = response.rindex('}') + 1
                json_str = response[json_start:json_end]
                extracted_data = json.loads(json_str)
            else:
                extracted_data = {"raw_output": response, "error": "Could not parse JSON"}
            
            # Add metadata
            extracted_data["file_path"] = str(file_path)
            extracted_data["file_name"] = file_path.name
            extracted_data["extracted_at"] = datetime.now().isoformat()
            
            logger.info(f"✓ Contract: Type={extracted_data.get('contract_type')}, Parties={extracted_data.get('parties')}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "error": str(e),
                "extracted_at": datetime.now().isoformat()
            }
    
    def save_extracted_data(self, doc_type: str, data: Dict[str, Any]):
        """Save extracted data to JSON file"""
        
        if doc_type == "invoice":
            self.extracted_data["invoices"].append(data)
        elif doc_type == "payroll":
            self.extracted_data["payroll"].append(data)
        elif doc_type == "contract":
            self.extracted_data["contracts"].append(data)
        
        # Save to file
        with open(self.extracted_data_path, 'w') as f:
            json.dump(self.extracted_data, f, indent=2)
        
        logger.info(f"💾 Saved extracted data to {self.extracted_data_path}")
    
    def extract_from_file(self, file_path: Path, doc_type: str) -> Dict[str, Any]:
        """
        Extract data from a file based on its document type
        
        Args:
            file_path: Path to the document
            doc_type: Document type (invoice, payroll, contract)
            
        Returns:
            Extracted data dictionary
        """
        if doc_type == "invoice":
            data = self.extract_invoice_data(file_path)
        elif doc_type == "payroll":
            data = self.extract_payroll_data(file_path)
        elif doc_type == "contract":
            data = self.extract_contract_data(file_path)
        else:
            logger.warning(f"⚠️  No extractor for document type: {doc_type}")
            return {}
        
        # Save to storage
        self.save_extracted_data(doc_type, data)
        
        return data
