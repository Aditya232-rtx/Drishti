"""File upload and management endpoints."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
from backend.services.documents.document_store import save_uploaded_file, list_user_documents


router = APIRouter(prefix="/files", tags=["files"])


class UploadResponse(BaseModel):
    """File upload response model."""
    document_id: str
    filename: str
    chunks: int


class DocumentInfo(BaseModel):
    """Document information model."""
    document_id: str
    filename: str
    mime_type: str
    chunk_count: int
    created_at: str


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload and process a document.
    
    Args:
        user_id: User identifier
        file: Document file (PDF, DOCX, TXT)
    
    Returns:
        UploadResponse with document metadata
    """
    try:
        document_id = await save_uploaded_file(user_id, file)
        
        # Get chunk count
        from backend.db.mongo import get_chunks_collection
        chunks_col = get_chunks_collection()
        chunk_count = await chunks_col.count_documents({
            "document_id": str(document_id)
        })
        
        return UploadResponse(
            document_id=str(document_id),
            filename=file.filename,
            chunks=chunk_count
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list", response_model=List[DocumentInfo])
async def list_files(user_id: str):
    """List all documents for a user.
    
    Args:
        user_id: User identifier
    
    Returns:
        List of DocumentInfo
    """
    try:
        documents = await list_user_documents(user_id)
        return [DocumentInfo(**doc) for doc in documents]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")
