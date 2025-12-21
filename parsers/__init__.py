"""
Document parsers for Private Doc Q&A
"""
from .pdf_parser import parse_pdf
from .docx_parser import parse_docx
from .text_parser import parse_text

__all__ = ['parse_pdf', 'parse_docx', 'parse_text']
