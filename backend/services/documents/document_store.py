"""Document storage and retrieval using MongoDB."""
from pathlib import Path
from typing import List
from datetime import datetime
from bson import ObjectId
from fastapi import UploadFile
from backend.db.mongo import get_documents_collection, get_chunks_collection
from backend.config.settings import get_settings
from backend.services.documents.parsers import parse_file, chunk_text


async def save_uploaded_file(user_id: str, file: UploadFile) -> ObjectId:
    """Save uploaded file and extract chunks.
    
    Args:
        user_id: User identifier
        file: Uploaded file
    
    Returns:
        Document ObjectId
    
    Raises:
        ValueError: If file type not supported or parsing fails
    """
    settings = get_settings()
    uploads_dir = settings.UPLOADS_DIR
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{user_id}_{timestamp}_{file.filename}"
    file_path = uploads_dir / safe_filename
    
    # Save file to disk
    content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Parse file
    try:
        text = parse_file(file_path)
    except Exception as e:
        # Clean up file on parse error
        file_path.unlink(missing_ok=True)
        raise ValueError(f"Failed to parse file: {str(e)}")
    
    # Chunk text
    chunks = chunk_text(text, chunk_size=settings.MAX_CHUNK_SIZE)
    
    # Insert document record
    documents_col = get_documents_collection()
    document_record = {
        "user_id": user_id,
        "filename": file.filename,
        "mime_type": file.content_type or "application/octet-stream",
        "original_path": str(file_path),
        "created_at": datetime.utcnow()
    }
    
    result = await documents_col.insert_one(document_record)
    document_id = result.inserted_id
    
    # Insert chunks
    chunks_col = get_chunks_collection()
    chunk_records = []
    
    for idx, chunk_text_content in enumerate(chunks):
        chunk_records.append({
            "document_id": str(document_id),
            "user_id": user_id,
            "text": chunk_text_content,
            "chunk_index": idx,
            "created_at": datetime.utcnow()
        })
    
    if chunk_records:
        await chunks_col.insert_many(chunk_records)
    
    print(f"✅ Saved document {file.filename} with {len(chunks)} chunks")
    
    return document_id


async def get_relevant_chunks(user_id: str, query: str, limit: int = 5) -> List[str]:
    """Get relevant document chunks for a query.
    
    Simple keyword-based search using case-insensitive text matching.
    
    Args:
        user_id: User identifier
        query: Search query
        limit: Maximum chunks to return
    
    Returns:
        List of relevant chunk texts
    """
    chunks_col = get_chunks_collection()
    
    # Extract keywords from query (simple tokenization)
    keywords = [word.lower() for word in query.split() if len(word) > 3]
    
    if not keywords:
        # No meaningful keywords, return empty
        return []
    
    # Build regex pattern for OR matching
    # Match any of the keywords (case-insensitive)
    pattern = "|".join(keywords[:5])  # Limit to first 5 keywords
    
    # Query chunks
    cursor = chunks_col.find({
        "user_id": user_id,
        "text": {"$regex": pattern, "$options": "i"}
    }).limit(limit)
    
    chunks = []
    async for doc in cursor:
        chunks.append(doc["text"])
    
    return chunks


async def list_user_documents(user_id: str) -> List[dict]:
    """List all documents for a user.
    
    Args:
        user_id: User identifier
    
    Returns:
        List of document records with chunk counts
    """
    documents_col = get_documents_collection()
    chunks_col = get_chunks_collection()
    
    cursor = documents_col.find({"user_id": user_id}).sort("created_at", -1)
    
    results = []
    async for doc in cursor:
        # Count chunks for this document
        chunk_count = await chunks_col.count_documents({
            "document_id": str(doc["_id"])
        })
        
        results.append({
            "document_id": str(doc["_id"]),
            "filename": doc["filename"],
            "mime_type": doc["mime_type"],
            "chunk_count": chunk_count,
            "created_at": doc["created_at"].isoformat()
        })
    
    return results
