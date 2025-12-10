"""Pydantic models for MongoDB documents."""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(BaseModel):
    """User model."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str
    preferred_lang: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Session(BaseModel):
    """Chat session model."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    memori_session_id: str
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Message(BaseModel):
    """Chat message model."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    session_id: str
    sender: Literal["user", "assistant"]
    text: str
    lang: str
    model_used: Optional[str] = None
    audio_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Document(BaseModel):
    """Uploaded document model."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    filename: str
    mime_type: str
    original_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Chunk(BaseModel):
    """Document chunk model."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    document_id: str
    user_id: str
    text: str
    chunk_index: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
