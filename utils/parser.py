"""Resume Parser Module"""

import PyPDF2
from docx import Document
from io import BytesIO

class ResumeParser:
    """Parses resume files in various formats"""
    
    def parse(self, file_obj):
        """
        Parse resume file and extract text
        
        Args:
            file_obj: File object (PDF or DOCX)
            
        Returns:
            str: Extracted text from resume
        """
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        filename = file_obj.filename.lower()
        
        if filename.endswith('.pdf'):
            return self._parse_pdf(file_obj)
        elif filename.endswith('.docx'):
            return self._parse_docx(file_obj)
        elif filename.endswith('.txt'):
            return self._parse_txt(file_obj)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    def _parse_pdf(self, file_obj):
        """Extract text from PDF"""
        try:
            file_obj.seek(0)
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_obj.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""
    
    def _parse_docx(self, file_obj):
        """Extract text from DOCX"""
        try:
            file_obj.seek(0)
            doc = Document(BytesIO(file_obj.read()))
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return ""
    
    def _parse_txt(self, file_obj):
        """Extract text from TXT"""
        try:
            file_obj.seek(0)
            raw = file_obj.read()
            if isinstance(raw, str):
                return raw
            return raw.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"Error parsing TXT: {e}")
            return ""