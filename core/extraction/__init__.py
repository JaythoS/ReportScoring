"""
Text Extraction Module

PDF ve DOCX dosyalarından metin çıkarma.
"""
from .pdf_extractor import extract_text_from_pdf, extract_text_from_docx

__all__ = ['extract_text_from_pdf', 'extract_text_from_docx']

