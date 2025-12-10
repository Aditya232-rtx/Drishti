"""Document parsers for PDF, DOCX, and TXT files."""
from pathlib import Path
from typing import List
import pypdf
from docx import Document as DocxDocument


def parse_pdf(file_path: Path) -> str:
    """Extract text from PDF file.
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Extracted text
    """
    text_parts = []
    
    try:
        reader = pypdf.PdfReader(str(file_path))
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
    
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    return "\n\n".join(text_parts)


def parse_docx(file_path: Path) -> str:
    """Extract text from DOCX file.
    
    Args:
        file_path: Path to DOCX file
    
    Returns:
        Extracted text
    """
    text_parts = []
    
    try:
        doc = DocxDocument(str(file_path))
        
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
    
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {str(e)}")
    
    return "\n\n".join(text_parts)


def parse_txt(file_path: Path) -> str:
    """Extract text from TXT file.
    
    Args:
        file_path: Path to TXT file
    
    Returns:
        Extracted text
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Failed to parse TXT: {str(e)}")
    
    except Exception as e:
        raise ValueError(f"Failed to parse TXT: {str(e)}")


def parse_file(file_path: Path) -> str:
    """Parse file based on extension.
    
    Args:
        file_path: Path to file
    
    Returns:
        Extracted text
    
    Raises:
        ValueError: If file type not supported
    """
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        return parse_pdf(file_path)
    elif suffix == '.docx':
        return parse_docx(file_path)
    elif suffix == '.txt':
        return parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def chunk_text(text: str, chunk_size: int = 1024, overlap: int = 128) -> List[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum chunk size in characters
        overlap: Overlap size between chunks
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < text_length:
            # Look for period, question mark, or exclamation
            boundary_chars = ['. ', '? ', '! ', '\n\n']
            best_break = end
            
            for char_seq in boundary_chars:
                pos = text.rfind(char_seq, start, end)
                if pos > start + chunk_size // 2:  # Only if in second half
                    best_break = pos + len( char_seq)
                    break
            
            end = best_break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap if end < text_length else text_length
    
    return chunks
