"""
PDF Parser - Extracts text from PDF files
Uses pdfplumber for better table/form extraction (important for W-2s, tax docs)
"""
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def parse_pdf(file_path: Path) -> Dict[str, Any]:
    """
    Parse a PDF file and extract text content.
    
    Returns:
        {
            'text': str,           # Full extracted text
            'pages': List[str],    # Text per page
            'metadata': dict,      # PDF metadata
            'source': str          # Original filename
        }
    """
    try:
        import pdfplumber
    except ImportError:
        # Fallback to pypdf if pdfplumber not installed
        return _parse_with_pypdf(file_path)
    
    pages = []
    full_text = []
    metadata = {}
    
    try:
        with pdfplumber.open(file_path) as pdf:
            metadata = pdf.metadata or {}
            
            for page_num, page in enumerate(pdf.pages):
                page_text = []
                
                # Extract regular text
                text = page.extract_text() or ""
                page_text.append(text)
                
                # Extract tables (important for W-2s, financial docs)
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        table_text = _table_to_text(table)
                        page_text.append(table_text)
                
                page_content = "\n".join(page_text)
                pages.append(page_content)
                full_text.append(f"[Page {page_num + 1}]\n{page_content}")
        
        return {
            'text': "\n\n".join(full_text),
            'pages': pages,
            'metadata': metadata,
            'source': file_path.name
        }
        
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        return {
            'text': '',
            'pages': [],
            'metadata': {},
            'source': file_path.name,
            'error': str(e)
        }


def _parse_with_pypdf(file_path: Path) -> Dict[str, Any]:
    """Fallback parser using pypdf"""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("Please install pdfplumber or pypdf: pip install pdfplumber pypdf")
    
    pages = []
    full_text = []
    
    try:
        reader = PdfReader(file_path)
        metadata = dict(reader.metadata) if reader.metadata else {}
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append(text)
            full_text.append(f"[Page {page_num + 1}]\n{text}")
        
        return {
            'text': "\n\n".join(full_text),
            'pages': pages,
            'metadata': metadata,
            'source': file_path.name
        }
        
    except Exception as e:
        logger.error(f"Error parsing PDF with pypdf {file_path}: {e}")
        return {
            'text': '',
            'pages': [],
            'metadata': {},
            'source': file_path.name,
            'error': str(e)
        }


def _table_to_text(table: List[List[str]]) -> str:
    """Convert a table to readable text format"""
    if not table:
        return ""
    
    rows = []
    for row in table:
        if row:
            # Clean up cells and join with tabs
            cells = [str(cell).strip() if cell else "" for cell in row]
            rows.append(" | ".join(cells))
    
    return "\n".join(rows)
