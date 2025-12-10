"""Enhanced test configuration and fixtures."""
import pytest
import asyncio
from pathlib import Path
import warnings
import io


# Suppress specific warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*Config.*deprecated.*")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def settings():
    """Get settings instance."""
    from backend.config.settings import get_settings
    return get_settings()


@pytest.fixture
def sample_text_file(tmp_path):
    """Create a sample text file for testing."""
    test_file = tmp_path / "test_document.txt"
    test_file.write_text(
        "This is a test document.\n"
        "It contains sample text for testing the document processing system.\n"
        "Machine learning is a subset of artificial intelligence.\n"
        "Python is a popular programming language for AI development."
    )
    return test_file


@pytest.fixture
def sample_pdf_content():
    """Create minimal valid PDF content."""
    # Minimal valid PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
409
%%EOF
"""
    return pdf_content


@pytest.fixture
def sample_docx_content():
    """Create minimal DOCX content (ZIP with minimal structure)."""
    import zipfile
    
    docx_io = io.BytesIO()
    
    with zipfile.ZipFile(docx_io, 'w', zipfile.ZIP_DEFLATED) as docx:
        # Add minimal DOCX structure
        docx.writestr('[Content_Types].xml', 
            '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>'
        )
        
        docx.writestr('_rels/.rels',
            '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>'
        )
        
        docx.writestr('word/document.xml',
            '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body><w:p><w:r><w:t>Test DOCX content for testing.</w:t></w:r></w:p></w:body></w:document>'
        )
    
    docx_io.seek(0)
    return docx_io.getvalue()


@pytest.fixture
def sample_audio_wav():
    """Create a minimal valid WAV file."""
    import struct
    
    # WAV file parameters
    sample_rate = 16000
    num_channels = 1
    bits_per_sample = 16
    duration = 1  # 1 second
    
    # Calculate data
    num_samples = sample_rate * duration
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = num_samples * num_channels * bits_per_sample // 8
    
    # Build WAV header
    wav = b'RIFF'
    wav += struct.pack('<I', 36 + data_size)  # File size - 8
    wav += b'WAVE'
    
    # fmt chunk
    wav += b'fmt '
    wav += struct.pack('<I', 16)  # Subchunk1Size
    wav += struct.pack('<H', 1)   # AudioFormat (PCM)
    wav += struct.pack('<H', num_channels)
    wav += struct.pack('<I', sample_rate)
    wav += struct.pack('<I', byte_rate)
    wav += struct.pack('<H', block_align)
    wav += struct.pack('<H', bits_per_sample)
    
    # data chunk
    wav += b'data'
    wav += struct.pack('<I', data_size)
    
    # Generate simple sine wave data
    import math
    frequency = 440  # A4 note
    for i in range(num_samples):
        value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
        wav += struct.pack('<h', value)
    
    return wav


@pytest.fixture
def test_user_id():
    """Standard test user ID."""
    return "test_user_123"


@pytest.fixture
def test_session_id():
    """Standard test session ID."""
    return "test_session_456"
